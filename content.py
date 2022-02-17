'''
Created on Feb 9, 2022

@author: tiff
'''

import ffmpeg
import math
import random
import time
import logging.config
import os
import httplib2
import http.client
import pickle
import pytube
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import cv2
import numpy as np
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from pathlib import Path
import urllib.request

#Function to return a string that is a valid filename based on string given
def getValidFilename(filename):
    valid_chars = '`~!@#$%^&+=,-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    getVals = list([val for val in filename if val in valid_chars])
    return "".join(getVals)

# Function to get filename from given stream
def getInputFilename(stream):
    while stream.node._KwargReprNode__incoming_edge_map != {}:
        stream = stream.node._KwargReprNode__incoming_edge_map[None][0]
        if not hasattr(stream, 'node'):
            return stream.__dict__['kwargs']['filename']
    return stream.node.__dict__['kwargs']['filename']

# Checks a youtube URL to see if it leads to a video (does not validate that it is a youtube URL
def isYoutubeVideoURLValid(url):
    r = requests.get(url) 
    # Check response for video unavailable to determine validity
    return not ("Video unavailable" in r.text)

# Returns a youtube obj given its ID and a settings object
def getYouTubeFromID(ID, settings):
    url = f"{YouTube.BASE_VID_URL}{ID}"
    settings.Base_Method_logger.info(f"Attempting to load details about YouTube video with ID {ID}")
    
    if not isYoutubeVideoURLValid(url):
        settings.Base_Method_logger.error(f"The Video ID {ID} is not a valid YouTube Video ID.  Returning None")
        return None
    
    ytVid = pytube.YouTube(url)
    title = ytVid.title
    description = ytVid.description
    tags = ytVid.keywords
    channel_id = ytVid.channel_id
    settings.Base_Method_logger.info(f"Returning YouTube object with title: {self.__sanitized_title()} and setting description, tags, and channel_id from the api call.")
    return YouTube(settings, title, description, tags, ID=ID, uploaded=True, channel_id=channel_id)

# Returns a content object with its youtube obj being made from its ID and the LBRY object made from a lookup to LBRY if it doesnt find anything it uses the Youtube details and sets upoaded flag for LBRY to false
def makeContentWithYouTubeID(ID, settings, LBRY_Channel_ID):
    ytVid = getYouTubeFromID(ID, settings)
    title = ytVid.title
    description = ytVid.description
    tags = ytVid.tags
    getVals = list([val for val in title if val.isalpha() or val.isnumeric() or val == '-'])
    name = "".join(getVals)
    settings.Base_Method_logger.info(f"Using data from YouTube Obj to create LBRY oject with channel_claim_id set to {LBRY_Channel_ID}")
    lbry = LBRY(settings, f"{ytVid.title}.mp4", channel_claim_id=LBRY_Channel_ID, name=name, title=title, description=description, tags=tags)
    settings.Base_Method_logger.info("Checking LBRY to see if the content is already on the channel and if so will update object with that data")
    lbry.updateFromLBRY()
    
    settings.Base_Method_logger.info("Returning Content Object with the YouTube and LBRY obj created")
    return Content(settings=settings, youtube_obj=ytVid, lbry_obj=lbry)

# class to store and handle various settings
class Settings(object):
    # filename for the client secrets file
    CLIENT_SECRETS_FILE = 'client_secret.json'
    def __init__(self, folder_location):
        logging.config.fileConfig("logging.ini")
        self.logger = logging.getLogger('SettingsLogger')

        
        self.YouTube_logger = logging.getLogger('YouTubeLogger')
        self.LBRY_logger = logging.getLogger('LBRYLogger')
        self.Rumble_logger = logging.getLogger('RumbleLogger')
        self.Content_logger = logging.getLogger('ContentLogger')
        self.Base_Method_logger = logging.getLogger('BaseMethodsLogger')
        self.logger.info("Loggers initialized")
        
        self.logger.info("Setting up YouTube Service")
        self.YouTube_service = self.create_YouTube_service()
        
        self.logger.info(f"setting folder_location:{folder_location}")
        self.logger.info("Changing to that folder")
        self.folder_location = folder_location
        self.original_dir = os.getcwd()
        os.chdir(self.folder_location)
        
        # Explicitly tell the underlying HTTP transport library not to retry, since
        # we are handling retry logic ourselves.
        httplib2.RETRIES = 1
        self.logger.info(f"Setting httplib2.RETRIES to {httplib2.RETRIES} since code will handle retry logic")
        
        self.logger.info("initing YouTubeIDs as empty list")
        self.YouTubeIDs = []
        self.logger.info("initing YouTubeChannelID as None")
        self.YouTubeChannelID = None
        self.logger.info("Initing LBRYChannelClaimID")
        self.LBRYChannelClaimID = None
        self.LBRYClaimIDs = []
        self.logger.info("initing LBRYClaimIDs to empty list")
        
    # private method used to generate the filename used for the pickle file that will store youtube creds
    def __YouTube_creds_pickle_file_name(self):
        return f'token_{YouTube.API_SERVICE_NAME}_{YouTube.API_VERSION}.pickle'
    
    # private method to load youtube creds from pickle file or return None if there is not one
    def __load_YouTube_credentials(self):
        pickle_file = self.__YouTube_creds_pickle_file_name()
 
        if not Path(f"{os.getcwd()}\\{pickle_file}").is_file():
            self.logger.info("Pickle File for Google Creds does not exist...Returning None")
            return None

        self.logger.info("Loading Credentials for Google from pickle file")
        with open(pickle_file, 'rb') as token:
            return pickle.load(token)

    #private method to save youtube creds to pickle file
    def __save_YouTube_credentials(self, cred):
        pickle_file = self.__YouTube_creds_pickle_file_name()

        self.logger.info(f"Saving Credentials for Google to pickle file: {pickle_file}")
        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)
            
    #private method to find all vid ids on the youtube channel with the ID set in the settings object and return them
    def __getYTChannelVidIDs(self):
        self.logger.info("loading channel as a pytube object to extract video IDs")
        c = pytube.Channel(f"https://www.youtube.com/channel/{self.YouTubeChannelID}")
        id_list = []
        for v in c:
            ID = f"{v[32:]}"
            self.logger.info(f"Adding ID: {ID}")
            id_list.append(ID)
        return id_list
    
    def testmeth(self):
        result = None
        try:
            result = self.YouTube_service.channels().list(
                part="snippet",
                mine=True
            ).execute()
        except Exception as e:
            self.logger.error(f"Error:\n{e}")
            return None
        self.logger.info("worked?")
        channel_id = result['items'][0]['id']
        try:
            result = self.YouTube_service.search().list(
                part="snippet",
                channelId=channel_id,
                order='date',
                type='video'
            ).execute()
        except Exception as e:
            self.logger.error(f"Error:\n{e}")
            return None
        pages = []
        pages.append(result['items'])
        next_page_token = result['nextPageToken']
        num_pages = math.ceil(result['pageInfo']['totalResults'] /  result['pageInfo']['resultsPerPage'])
        for x in range(num_pages - 1):
            new_result = None
            try:
                new_result = self.YouTube_service.search().list(
                    part="snippet",
                    channelId=channel_id,
                    order='date',
                    type='video',
                    pageToken=next_page_token
                ).execute()
            except Exception as e:
                self.logger.error(f"Error:\n{e}")
                return None
            if 'nextPageToken' in new_result:
                next_page_token = new_result['nextPageToken']
            pages.append(new_result['items'])
        
        for i in pages:
            print(f"{i['title']}")
            
        return result
    
    #private method to find all vid ids on the LBRY channel with the ID set in the settings object and return them
    def __getLBRYChannelVidClaimIDs(self):
        intialRequest = requests.post("http://localhost:5279", json={"method": "claim_search", "params": {"claim_ids": [], "channel_ids": [self.LBRYChannelClaimID], "not_channel_ids": [], "has_channel_signature": False, "valid_channel_signature": False, "invalid_channel_signature": False, "is_controlling": False, "stream_types": [], "media_types": [], "any_tags": [], "all_tags": [], "not_tags": [], "any_languages": [], "all_languages": [], "not_languages": [], "any_locations": [], "all_locations": [], "not_locations": [], "order_by": [], "no_totals": False, "include_purchase_receipt": False, "include_is_my_output": False, "remove_duplicates": False, "has_source": False, "has_no_source": False}}).json()
        
        numPages = intialRequest['result']['total_pages']
        numItems = intialRequest['result']['total_items']
        
        self.logger.info(f"Found {numItems} videos on channel {self.LBRYChannelClaimID} with {numPages} pages of data")
        
        pages = []
        claim_ids = []
        claims = []
        self.logger.info("adding initial request as 1st page of data")
        pages.append(intialRequest['result']['items'])

        for x in range(numPages-1):
            self.logger.info(f"getting page {x+2} of data and adding it")
            currentRequest = requests.post("http://localhost:5279", json={"method": "claim_search", "params": {"page":x+2,"claim_ids": [], "channel_ids": [self.LBRYChannelClaimID], "not_channel_ids": [], "has_channel_signature": False, "valid_channel_signature": False, "invalid_channel_signature": False, "is_controlling": False, "stream_types": [], "media_types": [], "any_tags": [], "all_tags": [], "not_tags": [], "any_languages": [], "all_languages": [], "not_languages": [], "any_locations": [], "all_locations": [], "not_locations": [], "order_by": [], "no_totals": False, "include_purchase_receipt": False, "include_is_my_output": False, "remove_duplicates": False, "has_source": False, "has_no_source": False}}).json()
            pages.append(currentRequest['result']['items'])
            
        page = 0
        x = 0
        for p in pages:
            page += 1
            for i in p:
                x += 1
                self.logger.info(f"Adding claim_id {i['claim_id']} with name {i['name']} from page {page} this is the {x} claim_id added")
                claims.append(i)
        
        sorted_claims = sorted(claims, key = lambda i: i['name'])
        for x in sorted_claims:
            claim_ids.append(x['claim_id'])
        return claim_ids
    
    #method to refresh youtube creds
    def refresh_YouTube_service(self):
        os.chdir(self.original_dir)
        self.YouTube_service = self.create_YouTube_service()
        os.chdir(self.folder_location)
    
    # This method implements an exponential backoff strategy to resume a
    # failed upload. slightly modified from provided python youtube api examples
    def resumable_upload(self, request):
        response = None
        error = None
        retry = 0
        vidID = None
        while response is None:
            try:
                self.logger.info('Uploading file...') 
                status, response = request.next_chunk()
                if(response is not None):
                    if('id' in response):
                        self.logger.info(f"Video id \"{response['id']}\" was successfully uploaded.")
                        vidID = response['id']
                    else:
                        exit(f"The upload failed with an unexpected response: {response}")
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise e
            except self.RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > self.MAX_RETRIES:
                    exit('No longer attempting to retry.')

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                self.logger.info(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)
        self.logger.info(f"setting ID to {vidID}")
        self.ID = vidID
    
    # method to create the youtube service it will try to use pickle file first and if it can not or there is a problem regrenerate via client secrets file
    def create_YouTube_service(self):
        self.logger.info(f"{self.CLIENT_SECRETS_FILE}, {YouTube.SCOPES}, {YouTube.API_SERVICE_NAME}, {YouTube.API_VERSION}")
        self.logger.info("Attempting to load youtube credentials from pickle file")
        cred = self.__load_YouTube_credentials()

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                self.logger.info("Google creds expired...Refreshing")
                cred.refresh(Request())
                self.logger.info("Saving Refreshed creds to pickle file")
            else:
                self.logger.info("Creating Google Credentials...")
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRETS_FILE, YouTube.SCOPES)
                cred = flow.run_console()
                self.logger.info("Saving Created creds to pickle file")
            self.__save_YouTube_credentials(cred)
        self.logger.info("Attempting to build youtube service to return")
        try:
            service = googleapiclient.discovery.build(YouTube.API_SERVICE_NAME, YouTube.API_VERSION, credentials = cred)
            self.logger.info(f"{YouTube.API_SERVICE_NAME} service created successfully")
            return service
        except Exception as e:
            self.logger.error(f"something went wrong:\n{e}\nReturning None")
            return None
    #method to set the youtube channel and list of IDs
    def setYouTubeChannel(self, ID):
        self.logger.info(f"Setting settings object YoutubeChannelID to {ID}")
        self.YouTubeChannelID = ID
        self.logger.info("Loading and setting the YouTubeIDs to a list of video IDs from the channel")
        self.YouTubeIDs = self.__getYTChannelVidIDs()
        
    #method set the LBRY channel and grab its claim IDs
    def setLBRYChannel(self, Channel_ID):
        self.logger.info(f"Setting settings object LBRYChannelClaimID to {Channel_ID}")
        self.LBRYChannelClaimID = Channel_ID
        self.logger.info("Loading and setting the LBRY claim IDs to a list from the channel")
        self.LBRYClaimIDs = self.__getLBRYChannelVidClaimIDs()

class YouTube(object):
    #base of the url used to grab YT thumbs
    THUMBNAIL_URL_BASE = 'https://img.youtube.com/vi/'
    #end of the URL to get YT thumbs (just put the vid ID between the base and end
    THUMBNAIL_URL_END = '/0.jpg'
    #base URL of a youtube vid
    BASE_VID_URL = "https://www.youtube.com/watch?v="
    # Always retry when these exceptions are raised.
    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected, http.client.IncompleteRead, http.client.ImproperConnectionState, http.client.CannotSendRequest, http.client.CannotSendHeader, http.client.ResponseNotReady, http.client.BadStatusLine)
    # Always retry when an apiclient.errors.HttpError with one of these status
    # codes is raised.
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
    
    #scopes needed for youtube API to work
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/youtube.force-ssl']
    #API info
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'

    #list of valid privacy statuses
    VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')
    
    # Maximum number of times to retry before giving up.
    MAX_RETRIES = 100
    
    def __init__(self, settings, title, description, tags=[], ID=None, channel_id=None, lic = None, thumbnail_file=None, uploaded=False, recordingDate=None, selfDeclaredMadeForKids=False, publishAt=None, publicStatsViewable=True, categoryId = 22, privacyStatus='public', embeddable=True, defaultLanguage='en'):
        self.settings = settings
        self.logger = self.settings.YouTube_logger
        self.logger.info("initing YouTube Obj")
        self.logger.info(f"setting uploaded flag to {uploaded}")
        self.uploaded = uploaded
        if ID is None:
            self.logger.info("No ID to set")
        else:
            self.logger.info(f"setting ID to {ID}")
        self.ID = ID
        if channel_id is None:
            self.logger.info("No Channel ID to set")
        else:
            self.logger.info(f"setting channel_id to {channel_id}")
        self.channel_id = channel_id
        
        
        #snippet.title
        self.title = title
        self.logger.info(f"setting title to {self.__sanitized_title()}")  #logging errors occur if certain things like emojis are in title so logging with a sanitized version of the title
        
        self.filename = self.__filename()
        self.logger.info(f"setting filename to {self.filename}")
        self.logger.info("Setting description")
        #snippet.description
        self.description = description
        if len(tags) == 0:
            self.logger.info("No tags to set")
        else:
            self.logger.info("Setting tags")
        #snippet.tags[]
        self.tags = tags
        
        #snippet.categoryId
        self.categoryId = categoryId
        self.logger.info(f"setting categoryId to {categoryId}")
        #snippet.defaultLanguage
        self.defaultLanguage = defaultLanguage
        self.logger.info(f"setting defaultLanguage to {defaultLanguage}")
        #status.embeddable
        self.logger.info(f"setting embeddable flag to {embeddable}")
        self.embeddable = embeddable
        if lic is None:
            self.logger.info("No license to set")
        else:
            self.logger.info(f"setting license to {lic}")
        #status.license
        self.license = lic
        self.logger.info(f"setting privacyStatus flag to {privacyStatus}")
        #status.privacyStatus
        self.privacyStatus = privacyStatus
        self.logger.info(f"setting publicStatsViewable flag to {publicStatsViewable}")
        #status.publicStatsViewable
        self.publicStatsViewable = publicStatsViewable
        self.logger.info(f"setting selfDeclaredMadeForKids flag to {selfDeclaredMadeForKids}")
        #status.selfDeclaredMadeForKids
        self.selfDeclaredMadeForKids = selfDeclaredMadeForKids
        
        self.thumbnail_file = thumbnail_file
        if thumbnail_file is None:
            self.__setThumbnailFileName()
    
    #private method to get filename
    def __filename(self):
        return getValidFilename(f"{self.title}.mp4")
    
    #private method to get a sanitized version of a title to use for logging (atm it only removes one specific emoji)
    def __sanitized_title(self):
        return self.title.replace('\U0001f61e',':(')
    
    #private method to get a sanitized version of description for logging
    def __sanitized_description(self):
        return

    #private method to get the URL of the videos thumbnail
    def __thumb_URL(self):
        return f"{self.THUMBNAIL_URL_BASE}{self.ID}{self.THUMBNAIL_URL_END}"
    
    #checks to see if a thumbnail needs to be updated (the compared file needs to be the same file and files typically change during processing so after setting a thumbnail you should download the new one to preent constant re-uploading
    def __check_thumb(self):
        if self.thumbnail_file is None:
            self.logger.info("no thumbnail_file set returning True so no action is taken")
            return True
        else:
            if not Path(self.__thumb_path()).is_file():
                self.logger.info("thumbnail_file set but no file exists downloading and returning True")
                self.downloadThumbnail()
                return True
        temp_file_name = f"temp_thumb_{self.filename.replace('.mp4','.jpg')}"
        f = open(temp_file_name,'wb')
        f_r = f.write(urllib.request.urlopen(urllib.request.Request(self.__thumb_URL(), headers={'User-Agent': 'Mozilla/5.0'})).read())
        f.close()
        file_1 = cv2.imread(self.__thumb_path())
        file_2 = cv2.imread(temp_file_name)
        difference = cv2.subtract(file_1, file_2)
        f_r = not np.any(difference)
        self.logger.info(f"Removing temporary thumbnail file {temp_file_name} that was used for comparing")
        os.remove(f"{os.getcwd()}\\{temp_file_name}")
        if f_r:
            self.logger.info(f"thumbnail_file matches thumbnail at {self.__thumb_URL()}")
            self.logger.info("Returning True so no action is taken")
            return True
        else:
            self.logger.info(f"thumbnail_file does not match {self.__thumb_URL()}")
            self.logger.info("returning False so that thumbnail can be updated")
            return False
    
    #private method to get the URL of the youtube video
    def __URL(self):
        return f"{YouTube.BASE_VID_URL}{self.ID}"

    #private method to get the full file path of the video file
    def __path(self):
        return f"{os.getcwd()}\\{self.filename}"
    
    #private method to get full filepath of the thumbnail file
    def __thumb_path(self):
        return f"{os.getcwd()}\\{self.thumbnail_file}"
    
    #private method to initialize youtube upload mostly from the provided example this wont work properly without your APP in google dev console being approved
    def __initialize_upload(self, youtube):
        self.logger.info(f"Preparing to upload video to youtube with title: {self.title} ad other stored details")
        body=dict(
            snippet=dict(
                title=self.title,
                description=self.description,
                tags=self.tags,
                categoryId=self.categoryId,
                defaultLanguage=self.defaultLanguage
            ),
            status=dict(
                privacyStatus=self.privacyStatus,
                embeddable=self.embeddable,
                license=self.license,
                publicStatsViewable=self.publicStatsViewable,
                publishAt=self.publishAt,
                selfDeclaredMadeForKids=self.selfDeclaredMadeForKids
            ),
            recordingDetails=dict(
                recordingDate=self.recordingDate
            )
        )
        self.logger.info("Starting the upload")
        # Call the API's videos.insert method to create and upload the video.
        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            # The chunksize parameter specifies the size of each chunk of data, in
            # bytes, that will be uploaded at a time. Set a higher value for
            # reliable connections as fewer chunks lead to faster uploads. Set a lower
            # value for better recovery on less reliable connections.
            #
            # Setting 'chunksize' equal to -1 in the code below means that the entire
            # file will be uploaded in a single HTTP request. (If the upload fails,
            # it will still be retried where it left off.) This is usually a best
            # practice, but if you're using Python older than 2.6 or if you're
            # running on App Engine, you should set the chunksize to something like
            # 1024 * 1024 (1 megabyte).
            media_body=MediaFileUpload(self.filename, chunksize=-1, resumable=True)
        )
        self.logger.info("returning resumable_upload private method to create a resumable upload")
        return self.settings.resumable_YouTube_upload(insert_request)
    
    #private method to upload new thumbnail for youtube video
    def __upload_thumbnail(self):
        self.logger.info(f"Attempting to set thumbnail to {self.thumbnail_file}")
        result = None
        try:
            result = self.settings.YouTube_service.thumbnails().set(
                videoId=self.ID,
                media_body=self.thumbnail_file
            ).execute()
        except Exception as e:
            self.logger.error(f"Error uploading thumbnail:\n{e}\nThumbnail not uploaded.")
            return None
        self.logger.info("New thumbnail is set")
        return result
    
    #private method to check if the obj is upoaded to youtube and sets the uploaded flag appropriately also returns the api response
    def __checkIfUploadedViaID(self):
        if self.ID is None:
            self.logger.info("ID not set can not check if is uploaded setting uploaded flag to False")
            self.uploaded = False
            return
        # Call the API's videos.list method to retrieve the video resource.
        videos_list_response = self.settings.YouTube_service.videos().list(
            id=self.ID,
            part='snippet'
        ).execute()
        
        if videos_list_response['items']:
            if self.uploaded:
                self.logger.info("uploaded flag already True no change needed")
            else:
                self.logger.info(f"Video with ID: '{self.ID}' is uploaded setting flag")
                self.uploaded = True
        else:
            if self.uploaded:
                self.logger.info(f"Video with ID: '{self.ID}' is not uploaded.  uploaded flag was set wrong...correcting...")
                self.uploaded = False
            else:
                self.logger.info("uploaded flag already False no need to change")
        return videos_list_response
    
    # private method to set the Thumbnail filename
    def __setThumbnailFileName(self):
        self.thumbnail_file = f"thumb_{self.filename.replace('.mp4','.jpg')}"
    
    # public version of the __thumb_URL private method
    def TNURL(self):
        return self.__thumb_URL()
    
    # method to download thumbnail from youtube this will remove existing thumbnail file assosiated with this obj
    def downloadThumbnail(self):
        url = self.__thumb_URL()
        if not self.thumbnail_file is None:
            if Path(self.__thumb_path()).is_file():
                self.logger.info("Removing existing Thumbnail file")
                os.remove(self.__thumb_path())
        else:
            self.__setThumbnailFileName()
            self.logger.info(f"thumbnail_file not set setting to {self.thumbnail_file}")
            if Path(self.__thumb_path()).is_file():
                self.logger.info("Removing existing Thumbnail file")
                os.remove(self.__thumb_path())
           
        self.logger.info(f"Downloading thumb from {url}")    
        f = open(self.__thumb_path(),'wb')
        f_r = f.write(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read())
        f.close()
        return f_r
    
    #method to update youtube video currently only updates title description and tags will not run the update API call if there are no changes to those three values
    def update(self):
        videos_list_response = self.__checkIfUploadedViaID()
        # If the response does not contain an array of 'items' then the video was
        # not found.
        if not self.uploaded:
            self.logger.info(f"Video with ID: '{self.ID}' was not found.  No Update will be performed")
            return

        # Since the request specified a video ID, the response only contains one
        # video resource. This code extracts the snippet from that resource.
        videos_list_snippet = videos_list_response['items'][0]['snippet']
        
        if videos_list_snippet['title'] == self.title and videos_list_snippet['description'] == self.description and videos_list_snippet['tags'] == self.tags:
            self.logger.info("No changes to local object requiring an update.  Skipping update to avoid useless quota use")
            return videos_list_response
        # Set video title, description, and tags
        videos_list_snippet['title'] = self.title
        videos_list_snippet['description'] = self.description
        videos_list_snippet['tags'] = self.tags


        videos_update_response = self.settings.YouTube_service.videos().update(
            part='snippet',
            body=dict(
                snippet=videos_list_snippet,
                id=self.ID
            )
        ).execute()
        
        if videos_update_response['snippet']['title']:
            self.logger.info(f"The updated video Title: {self.__sanitized_title()}")
        if videos_update_response['snippet']['description']:
            self.logger.info("Description updated")
        if videos_update_response['snippet']['tags']:
            self.logger.info("tags updated")
        return videos_update_response
    
    #method to upload to youtube will result in locked private video if app is not approved by google
    def upload(self):
        file = f"{os.getcwd()}\\{self.title}.mp4"
        self.logger.info("Creating YouTube Service to allow uploading")
        
        try:
            self.logger.info(f"Attempting to upload {file}")
            self.__initialize_upload(self.settings.YouTube_service)
        except HttpError as e:
            raise e

    #method to update the thumbnail on youtube if the file linked to the obj does not match the uploaded one
    def updateThumbnail(self):
        if not self.__check_thumb():
            self.__upload_thumbnail()
            self.logger.info("Removing the current thumbnail file and downloading a new copy so future compares are accurate")
            self.downloadThumbnail()

    #method to download a vid from youtube it downloads highest res video then audio then FFMPEGs them together before cleaning up
    def download(self, overwrite=False, resolution=0):
        if Path(self.__path()).is_file():
            self.logger.info(f"File {self.filename} already exists.")
            if overwrite:
                self.logger.info("Overwrite set removing file re-downloading")
                os.remove(self.filename)
            else:
                self.logger.info("Overwrite not set not downloading")
                return
        
        if not isYoutubeVideoURLValid(self.__URL()):
            self.logger.error(f"URL {self.__URL} is not a valid YouTube video URL can't download")
            return
        
        self.logger.info(f"Attempting to download video portion of {self.title}")
        video_file = None
        vid = pytube.YouTube(self.__URL())
        finished = False
        tries = 0
        if(not resolution):
            while not finished and tries < self.MAX_RETRIES + 2:
                try:
                    video_file = vid.streams.order_by('resolution').desc().first().download(filename_prefix="video_")
                    finished = True
                except Exception as e:
                    if tries > self.MAX_RETRIES:
                        self.logger.error("Too many failed download attempts raising new exception")
                        raise Exception()
                    self.logger.error(f"got error:\n{e}\nGoing to try again")
                    tries += 1
                    self.logger.info(f"Attempted {tries} time(s) of a possible {self.MAX_RETRIES}")
                    finished = False
        else:
            while not finished and tries < self.MAX_RETRIES + 2:
                try:
                    self.logger.info(f"Setting video download resolution to {resolution}")
                    video_file = vid.streams.filter(res=f"{resolution}p").order_by('resolution').desc().first().download(filename_prefix="video_")
                    finished = True
                except Exception as e:
                    if tries > self.MAX_RETRIES:
                        self.logger.error("Too many failed download attempts raising new exception")
                        raise Exception()
                    self.logger.error(f"got error:\n{e}\nGoing to try again")
                    tries += 1
                    self.logger.info(f"Attempted {tries} time(s) of a possible {self.MAX_RETRIES}")
                    finished = False
            
        
    
        self.logger.info(f"Downloaded video for {self.title}")
        
        self.logger.info(f"Attempting to download audio portion of {self.title}")
        
        finished = False
        tries = 0
        while not finished and tries < self.MAX_RETRIES + 2:
            try:
                audio_file = pytube.YouTube(self.__URL()).streams.filter(only_audio=True).order_by('abr').desc().first().download(filename_prefix="audio_") 
                finished = True
            except Exception as e:
                if tries > self.MAX_RETRIES:
                    self.logger.error("Too many failed download attempts raising new exception")
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                self.logger.info(f"Attempted {tries} time(s) of a possible {self.MAX_RETRIES}")
                finished = False
        
        
        self.logger.info(f"Downloaded audio for {self.title}")
        
        audFile = None
        vidFile = None
        source_audio = None
        source_video = None
        
        finished = False
        tries = 0
        while not finished and tries < self.MAX_RETRIES + 2:
            try:
                self.logger.info("Attempting to prep source audio and video to merge")
                source_audio = ffmpeg.input(audio_file)
                source_video = ffmpeg.input(video_file)
                audFile = getInputFilename(source_audio)
                vidFile = getInputFilename(source_video)
                finished = True
            except Exception as e:
                if tries > self.MAX_RETRIES:
                    self.logger.error("Too many failed download attempts raising new exception")
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                self.logger.info(f"Attempted {tries} time(s) of a possible {self.MAX_RETRIES}")
                finished = False
        
        self.logger.info(f"Attempting to merge {vidFile} and {audFile} together as {self.filename}")
        finished = False
        tries = 0
        while not finished and tries < self.MAX_RETRIES + 2:
            try:
                self.logger.info("Attempting to merge audio and video")
                ffmpeg.concat(source_video, source_audio, v=1, a=1).output(self.filename).run()
                finished = True
            except Exception as e:
                if tries > self.MAX_RETRIES:
                    self.logger.error("Too many failed download attempts raising new exception")
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                self.logger.info(f"Attempted {tries} time(s) of a possible {self.MAX_RETRIES}")
                finished = False
                
        self.logger.info(f"Files merged as {self.filename}")
    
        self.logger.info("Cleaning up source files....")
        self.logger.info(f"Removing {audFile}")
        os.remove(audFile)
        self.logger.info(f"Removing {vidFile}")
        os.remove(vidFile)
        
        
class LBRY(object):
    #URL for LBRY api calls
    LBRY_SDK_URL = "http://localhost:5279"
    
    def __init__(self, settings, file_name, channel_claim_id=None, channel_name=None, claim_id=None, claim_name=None, name=None, description="Default Description", title=None, uri=None, languages=['en'], tags=[], bid='0.02', nsfw=False, shouldUpload=True, uploaded=False):
        self.settings = settings
        self.logger = self.settings.LBRY_logger
        
        self.file_name = getValidFilename(file_name)
        self.logger.info(f"initing LBRY obj for {self.file_name}")
        self.channel_claim_id = channel_claim_id
        self.channel_name = channel_name
        self.claim_id = claim_id
        if claim_name is None:
            self.claim_name = claim_name
        else:
            getVals = list([val for val in claim_name if val.isalpha() or val.isnumeric() or val == '-'])
            self.claim_name = "".join(getVals)
        if name is None:
            getVals = list([val for val in file_name.split('.mp4')[0] if val.isalpha() or val.isnumeric() or val == '-'])
            self.name = "".join(getVals)
        else:
            getVals = list([val for val in name if val.isalpha() or val.isnumeric() or val == '-'])
            self.name = "".join(getVals)
        self.bid = bid
        self.description = description
        self.languages = languages
        if title is None:
            self.title = file_name.split('.mp4')[0]
        else:
            self.title = title
        self.nsfw = nsfw
        self.shouldUpload = shouldUpload
        self.uri = uri
        self.tags = tags
        self.uploaded = uploaded
        
        self.thumbnail_url = None
    
    #private method to determine if the object is uploaded (lookup by self.name and the set channel claim id)
    def __uploaded(self):
        if self.__request()['result']['total_items'] > 0:
            return True
        else:
            return False
        
    #returns request results for looking up obj on LBRY based on self.name and the set channel claim id
    def __request(self):
        return requests.post("http://localhost:5279", json={"method": "stream_list", "params": {"name": [self.name], "claim_id": [], "is_spent": False, "resolve": False, "no_totals": False}}).json()
    
    #method to lookup details of vid on lbry and updates based on info found there (searches done with name and channel id)
    def updateFromLBRY(self):
        if not self.__uploaded():
            self.logger.info(f"Can not update from LBRY as {self.name} does not appear to be uploaded setting uploaded flag to False")
            self.uploaded = False
            return
        request = self.__request()
        
        self.uploaded = True
        self.logger.info(f"uploaded flag set to {self.uploaded}")
        
        self.claim_id = request['result']['items'][0]['claim_id']
        self.logger.info(f"claim_id set to {self.claim_id}")
        
        self.bid = request['result']['items'][0]['amount']
        self.logger.info(f"bid set to {self.bid}")
        
        self.channel_claim_id = request['result']['items'][0]['signing_channel']['claim_id']
        self.logger.info(f"channel_claim_id set to {self.channel_claim_id}")
        
        self.channel_name = request['result']['items'][0]['signing_channel']['name']
        self.logger.info(f"channel_name set to {self.channel_name}")
        
        self.claim_name = request['result']['items'][0]['name']
        self.logger.info(f"claim_name set to {self.claim_name}")
        
        if 'description' in request['result']['items'][0]['value'].keys():
            self.description = request['result']['items'][0]['value']['description']
            self.logger.info(f"description set to from web object")
        else:
            self.logger.info("No description to set")
            
        self.file_name = request['result']['items'][0]['value']['source']['name']
        self.logger.info(f"file_name set to {self.file_name}")
        
        self.languages = request['result']['items'][0]['value']['languages']
        self.logger.info(f"languages set to {self.languages}")
        
        self.name = request['result']['items'][0]['name']
        self.logger.info(f"name set to {self.name}")
        
        
        if 'tags' in request['result']['items'][0]['value'].keys():
            self.tags = request['result']['items'][0]['value']['tags']
            self.logger.info(f"tags set to {self.tags}")
        else:
            self.tags = []
            self.logger.info("No tags to set")
        self.title = request['result']['items'][0]['value']['title']
        self.logger.info(f"title set to {self.__sanitized_title()}")
    
    # runs an update on the object in LBRY (does not check if there are actually any differences to update before calling the update)
    def update(self):
        self.logger.info(f"prepping for updating info on LBRY")
        
        params_for_update = {
            "claim_id":f"{self.claim_id}",
            "bid": self.bid,  
            "title": self.title, 
            "description": self.description, 
            "tags": self.tags, 
            "channel_id": self.channel_claim_id,
            "languages": self.languages,
            "locations": [],
            "channel_account_id": [],
            "funding_account_ids": [],
            "thumbnail_url":self.thumbnail_url
        }
        self.logger.info(f"Attempting to update the data for video {self.title}")
        
        data = requests.post(LBRY.LBRY_SDK_URL, json={"method": "stream_update", "params": params_for_update}).json()
        
        return data
        
    # method to upload the video to LBRY does not check if already uploaded currently
    def upload(self):
        self.logger.info(f"prepping for upload to LBRY")
        #Set up the parameters used for the stream_create api call
        params_for_upload = {
            "name": f"{self.name}", 
            "bid": self.bid, 
            "file_path": f"{os.getcwd()}\\{self.file_name}", 
            "title": self.title, 
            "description": self.description, 
            "tags": self.tags, 
            "channel_id": self.channel_claim_id,
            "validate_file": False,
            "optimize_file": False,
            "languages": self.languages,
            "locations": [],
            "channel_account_id": [],
            "funding_account_ids": [],
            "preview": False,
            "blocking": False,
            "thumbnail_url":self.thumbnail_url
        }
        self.logger.info(f"Attempting to upload the video {self.file_name}")
        #api call made and results stored in data
        data = requests.post(LBRY.LBRY_SDK_URL, json={"method": "stream_create", "params": params_for_upload}).json()
        
        
        try:
            self.logger.info("Attempting to set URI and claim_id...")
            self.uri = data['result']['outputs'][0]['permanent_url'].split('//')[1]
            self.claim_id = data['result']['outputs'][0]['claim_id']
            self.logger.info(f"uri set to {self.uri} and claim_id set to {self.claim_id}")
        except Exception as e:
            self.logger.info(f"Upload failed...\nresults:\n{data}")
            raise e
        
        while not self.__uploaded():
            self.logger.info("Upload not complete waiting for a minute and checking again")
            time.sleep(60)
        self.logger.info(f"upload is complete running an update on the LBRY obj from LBRY")
        self.updateFromLBRY()
        
        
class Rumble(object):
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = self.settings.Rumble_logger
        self.logger.info("Initing Rumble object")

class Content(object):

    def __init__(self, settings, youtube_obj, lbry_obj, rumble_obj, setThumbsFromYouTube=True):
        self.settings = settings
        self.logger = self.settings.Content_logger
        self.logger.info(f"initing Content obj")
        self.yt = youtube_obj
        self.lbry = lbry_obj
        self.rumble = rumble_obj
        if setThumbsFromYouTube:
            self.__setThumbsFromYouTube()
    
    #private method to check LBRY against YouTube
    def __YouTubeMatchesLBRY(self):
        return self.lbry.title == self.yt.title and self.lbry.description == self.yt.description and self.lbry.tags == self.yt.tags
    
    #private method to check if Rumble and YouTube match
    def __YouTubeMatchesRumble(self):
        return True
    
    #private method to update LBRY from Youtube (currently only does title description and tags
    def __updateLBRYFromYouTube(self):
        return
    
    #private method to set LBRY thumb from YouTube thumb
    def ____setLBRYThumbFromYouTube(self):
        self.logger.info("Setting LBRY thumbnail URL based on YouTube conterpart")
        self.lbry.thumbnail_url = self.yt.TNURL()
        
    #private method to set rumble thumb from youtube one
    def ____setRumbleThumbFromYouTube(self):
        return
        
    #private method to set all thumbs based on youtube obj
    def ____setThumbsFromYouTube(self):
        self.____setLBRYThumbFromYouTube()
        self.____setRumbleThumbFromYouTube()
    
    #method to update all other objects based on youtube object (this is all local no API calls)
    def updateAllBasedOnYouTube(self):
        if self.yt is None:
            self.logger.info("No YouTube Object taking no action")
            return 
        
        if self.__YouTubeMatchesLBRY():
            self.logger.info("YouTube and LBRY data already matches")
        if self.__YouTubeMatchesRumble():
            self.logger.info("YouTube and Rumble data already matches")
            
        if self.__YouTubeMatchesLBRY() and self.__YouTubeMatchesRumble():
            self.logger.info("All videos data already matches YouTube")
            return
        
        self.updateLBRYBasedOnYouTube()
        self.updateRumbleBasedOnYouTube()
    
    #method to update LBRY based on Youtube
    def updateLBRYBasedOnYouTube(self):
        self.lbry.title = self.yt.title
        self.lbry.description = self.yt.description
        self.lbry.tags = self.yt.tags
        
        self.lbry.update()
    
    #method to update Rumble based on Youtube
    def updateRumbleBasedOnYouTube(self):
        return