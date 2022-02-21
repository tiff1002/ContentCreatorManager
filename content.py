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
    
  
    
    

    def setLBRYChannel(self, Channel_ID):
        self.logger.info(f"Setting settings object LBRYChannelClaimID to {Channel_ID}")
        self.LBRYChannelClaimID = Channel_ID
        self.logger.info("Loading and setting the LBRY claim IDs to a list from the channel")
        self.LBRYClaimIDs = self.__getLBRYChannelVidClaimIDs()

class YouTube(object):
    
    
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

    #method to update the thumbnail on youtube if the file linked to the obj does not match the uploaded one
    def updateThumbnail(self):
        if not self.__check_thumb():
            self.__upload_thumbnail()
            self.logger.info("Removing the current thumbnail file and downloading a new copy so future compares are accurate")
            self.downloadThumbnail()

    
        
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