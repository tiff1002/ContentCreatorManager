'''
Created on Feb 20, 2022

@author: tiff
'''
import config
import content
import ffmpeg
import random
import time
import httplib2
import http.client
import pathlib
import os
import math
import pickle
import pytube
import google_auth_oauthlib
import googleapiclient.discovery
import google.oauth2.credentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request as GoogleAuthRequest

def make_video(video,channel):
    if 'tags' not in video['snippet']:
        tags = []
    else:
        tags = video['snippet']['tags']
    if 'description' not in video['snippet']:
        description = ""
    else:
        description = video['snippet']['description']
    if 'selfDeclaredMadeForKids' not in video['status']:
        self_declared_made_for_kids = False
    else:
        self_declared_made_for_kids = video['status']['selfDeclaredMadeForKids']
    if 'defaultAudioLanguage' not in video['snippet']:
        default_audio_language = 'en-US'
    else:
        default_audio_language = video['snippet']['defaultAudioLanguage']
    return Video(channel=channel, video_id=video['id'], favorite_count=video['statistics']['favoriteCount'], comment_count=video['statistics']['commentCount'], dislike_count=video['statistics']['dislikeCount'], like_count=video['statistics']['likeCount'], view_count=video['statistics']['viewCount'], self_declared_made_for_kids=self_declared_made_for_kids, made_for_kids=video['status']['madeForKids'], public_stats_viewable=video['status']['publicStatsViewable'], embeddable=video['status']['embeddable'], lic=video['status']['license'], privacy_status=video['status']['privacyStatus'], upload_status=video['status']['uploadStatus'], has_custom_thumbnail=video['contentDetails']['hasCustomThumbnail'], content_rating=video['contentDetails']['contentRating'], licensed_content=video['contentDetails']['licensedContent'], default_audio_language=default_audio_language, published_at=video['snippet']['publishedAt'], channel_id=video['snippet']['channelId'], title=video['snippet']['title'], description=description, thumbnails=video['snippet']['thumbnails'], channel_title=video['snippet']['channelTitle'], tags=tags, category_id=video['snippet']['categoryId'], live_broadcast_content=video['snippet']['liveBroadcastContent'])

class Channel(object):
    '''
    classdocs
    '''
    CLIENT_SECRETS_FILE = 'client_secret.json'
    
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
    MAX_RETRIES = 50

    
    def __creds_pickle_file_name(self):
        return f'token_{Channel.API_SERVICE_NAME}_{Channel.API_VERSION}.pickle'
    
    def __load__creds(self):
        pickle_file = os.path.join(os.getcwd(),self.__creds_pickle_file_name())
        
        if not pathlib.Path(pickle_file).is_file():
            self.logger.info("Pickle File for Google Creds does not exist...Returning None")
            return None

        self.logger.info("Loading Credentials for Google from pickle file")
        with open(pickle_file, 'rb') as token:
            return pickle.load(token)
        
    def __save_creds(self, cred : google.oauth2.credentials.Credentials):
        pickle_file = self.__creds_pickle_file_name()

        self.logger.info(f"Saving Credentials for Google to pickle file: {pickle_file}")
        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)
    
    def __get_channel(self):
        result = None
        self.logger.info("Making channels.list API call to get Id for the Channel of the authenticated user")
        
        try:
            result = self.service.channels().list(
                part="contentDetails",
                mine=True
            ).execute()
        except Exception as e:
            self.logger.error(f"Error:\n{e}")
            return None
        self.logger.info("API Call made")
        return result['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    def __get_videos(self):
        result = None
        self.logger.info("Making intial PlaylistItems.list API call to get first 50 resuts and the first next_page_token")
        
        try:
            result = self.service.playlistItems().list(
                playlistId=self.id,
                maxResults=50,
                part="contentDetails"
            ).execute()
        except Exception as e:
            self.logger.error(f"Error:\n{e}")
            return None
        self.logger.info("API Call made")
        
        result_pages = [result['items']]
        next_page_token = result['nextPageToken']
        
        self.logger.info(f"Added first page of results to list and set first next_page_token: {next_page_token}")
        
        while next_page_token is not None:
            self.logger.info("Grabbing next page of results")
            try:
                result = self.service.playlistItems().list(
                    playlistId=self.id,
                    maxResults=50,
                    part="contentDetails",
                    pageToken=next_page_token
                ).execute()
            except Exception as e:
                self.logger.error(f"Error:\n{e}")
                return None
            self.logger.info("API Call made")
            result_pages.append(result['items'])
            self.logger.info("Added next page of results to list")
            if 'nextPageToken' in result:
                next_page_token = result['nextPageToken']
                self.logger.info(f"Set next_page_token to {next_page_token}")
            else:
                next_page_token = None
                self.logger.info("Set next_page_token to None")
        results = []
        Ids = []
        
        for x in result_pages:
            for y in x:
                self.logger.info(f"Adding id: {y['contentDetails']['videoId']} to list")
                Ids.append(y['contentDetails']['videoId'])
      

        num_pages = math.ceil(len(Ids)/50)
        max_num_per_page = math.ceil(len(Ids)/num_pages)
        Id_csvs = []
        Ids.reverse()
        
        for x in range(num_pages):
            Id_csvs.append([])
            page_ids = []
            for y in range(max_num_per_page):
                try:
                    self.logger.info(f"Adding {Ids[y+(x*max_num_per_page)]} to page_ids")
                    page_ids.append(Ids[y+(x*max_num_per_page)])
                except Exception as e:
                    self.logger.info("finished making pages of id csv strings")
            
            page_csv = ",".join(page_ids)
            
            Id_csvs.append(page_csv)
            
        for x in range(math.ceil(len(Id_csvs) / 2)):
            self.logger.info(f"Making API call to grab video data using {Id_csvs[x*2+1]}")
            try:
                result = self.service.videos().list(
                    part="snippet,contentDetails,statistics,status",
                    id=Id_csvs[x*2+1]
                ).execute()
            except Exception as e:
                self.logger.error(f"Error:\n{e}")
                return None    
            self.logger.info("API call made")
            for j in result['items']:
                self.logger.info(f"Adding Video results for {j['snippet']['title']} to results to return")
                results.append(j)
            
        self.logger.info("finished processing results")
        
        return results
    
    def __create_service(self):
        self.logger.info("Changing to original dir to load creds")
        os.chdir(self.settings.original_dir)
        
        self.logger.info(f"{Channel.CLIENT_SECRETS_FILE}, {Channel.SCOPES}, {Channel.API_SERVICE_NAME}, {Channel.API_VERSION}")
        self.logger.info("Attempting to load youtube credentials from pickle file")
        cred = self.__load__creds()

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                self.logger.info("Google creds expired...Refreshing")
                cred.refresh(GoogleAuthRequest())
                self.logger.info("Saving Refreshed creds to pickle file")
            else:
                self.logger.info("Creating Google Credentials...")
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(Channel.CLIENT_SECRETS_FILE, Channel.SCOPES)
                cred = flow.run_console()
                self.logger.info("Saving Created creds to pickle file")
            self.__save_creds(cred)
        self.logger.info("Changing back to proper folder")
        os.chdir(self.settings.folder_location)
        self.logger.info("Attempting to build youtube service to return")
        try:
            service = googleapiclient.discovery.build(Channel.API_SERVICE_NAME, Channel.API_VERSION, credentials = cred)
            self.logger.info(f"{Channel.API_SERVICE_NAME} service created successfully")
            return service
        except Exception as e:
            self.logger.error(f"something went wrong:\n{e}\nReturning None")
            return None
        
    def __set_videos(self):
        vids = self.__get_videos()
        for vid in vids:
            self.videos.append(make_video(vid,self))

    def __init__(self, settings : config.Settings):
        '''
        Constructor
        '''
        self.logger = settings.YouTube_logger
        self.logger.info("Initializing Channel object")
        
        self.settings = settings
        self.logger.info("Set settings for Channel Object")
        
        # Explicitly tell the underlying HTTP transport library not to retry, since
        # we are handling retry logic ourselves.
        httplib2.RETRIES = 1
        self.logger.info("Set httplib2.RETRIES to 1 as retry logic is handled in this tool")
        
        self.service = self.__create_service()
        self.logger.info("Created and set YouTube service")
        
        self.logger.info("Setting Id for the Channel")
        self.id = self.__get_channel()
        
        self.videos = []
        self.__set_videos()
    
    def download_videos(self):
        for video in self.videos:
            if not video.downloaded:
                video.download()
        
    def refresh_service(self):
        os.chdir(self.original_dir)
        self.YouTube_service = self.create_YouTube_service()
        os.chdir(self.folder_location)
        
        
class Video(object):
    '''
    classdocs
    '''
    BASE_URL = "https://www.youtube.com/watch?v="
    
    MAX_RETRIES = 25
    
    def __is_downloaded(self):
        f = os.path.join(os.getcwd(),self.__file_name())
        return pathlib.Path(f).is_file()
    
    def __file_name(self):
        valid_chars = '`~!@#$%^&+=,-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        getVals = list([val for val in f"youtube_{self.title}.mp4" if val in valid_chars])
        return "".join(getVals)
        
    def __get_pytube(self, use_oauth=True):
        url = f"{Video.BASE_URL}{self.id}"
        return pytube.YouTube(url, use_oauth=use_oauth)
    
    def __initialize_upload(self):
        self.logger.info(f"Preparing to upload video to youtube with title: {self.title} ad other stored details")
        body=dict(
            snippet=dict(
                title=self.title,
                description=self.description,
                tags=self.tags,
                categoryId=self.category_id,
                defaultLanguage=self.default_language
            ),
            status=dict(
                embeddable=self.embeddable,
                license=self.license,
                privacyStatus=self.privacy_status,
                publicStatsViewable=self.public_stats_viewable,
                selfDeclaredMadeForKids=self.self_declared_made_for_kids
            )
        )
        self.logger.info("Starting the upload")
        # Call the API's videos.insert method to create and upload the video.
        insert_request = self.channel.service.videos().insert(
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
            media_body=MediaFileUpload(self.__file_name(), chunksize=-1, resumable=True)
        )
        self.logger.info("returning resumable_upload private method to create a resumable upload")
        return self.__resumable_upload(insert_request)
    
    def __resumable_upload(self, request):
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
                if e.resp.status in Channel.RETRIABLE_STATUS_CODES:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise e
            except Channel.RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > Video.MAX_RETRIES:
                    exit('No longer attempting to retry.')

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                self.logger.info(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)
        self.logger.info(f"setting ID to {vidID}")
        self.id = vidID
        
    def __get_web_data(self):
        request = self.channel.service.videos().list(
            part="snippet,contentDetails,statistics,status",
            id=self.id
        )
        result = request.execute()
        
        return result['items'][0]
        
    def __init__(self, channel, video_id=None, favorite_count='0', 
                 comment_count='0', dislike_count='0', like_count='0', view_count='0', self_declared_made_for_kids=False, 
                 made_for_kids=False, public_stats_viewable=True, embeddable=True, lic='youtube', privacy_status="public", 
                 upload_status='notUploaded', has_custom_thumbnail=False, content_rating={}, licensed_content=False, 
                 default_audio_language='en-US', published_at=None, channel_id=None, title=None, description=None, 
                 thumbnails={}, channel_title=None, tags=[], category_id=22, live_broadcast_content=None, new_video=False):
        '''
        Constructor
        '''
        self.logger = channel.settings.YouTube_logger
        self.logger.info('initializing Video Object')
        self.settings = channel.settings
        self.id = video_id
        self.published_at = published_at
        self.channel_id = channel_id
        self.title = title
        self.description = description
        self.thumbnails = thumbnails
        self.channel_title = channel_title
        self.tags = tags
        self.category_id = category_id
        self.live_broadcast_content = live_broadcast_content
        self.default_audio_language = default_audio_language
        self.default_language = default_audio_language
        self.licensed_content = licensed_content
        self.content_rating = content_rating
        self.has_custom_thumbnail = has_custom_thumbnail
        self.upload_status = upload_status
        self.privacy_status = privacy_status
        self.license = lic
        self.embeddable = embeddable
        self.public_stats_viewable = public_stats_viewable
        self.made_for_kids = made_for_kids
        self.self_declared_made_for_kids = self_declared_made_for_kids
        self.view_count = view_count
        self.like_count = like_count
        self.dislike_count = dislike_count
        self.comment_count = comment_count
        self.favorite_count = favorite_count
        self.downloaded = self.__is_downloaded()
        if new_video:
            self.pytube_obj = None
        else:
            self.pytube_obj = self.__get_pytube()
        self.channel = channel
    
    def update_to_web(self):
        current_web_status = self.__get_web_data()
        
        current_web_snippet = current_web_status['snippet']
        current_web_status = current_web_status['status']
    
        need_to_update=False
        
        update_snippet = {}
        update_snippet['categoryId']=self.category_id
        update_snippet['defaultLanguage']=self.default_language
        update_snippet['description']=self.description
        update_snippet['tags']=self.tags
        update_snippet['title']=self.title
        update_status = {}
        update_status['embeddable']=self.embeddable
        update_status['license']=self.license
        update_status['privacyStatus']=self.privacy_status
        update_status['publicStatsViewable']=self.public_stats_viewable
        update_status['selfDeclaredMadeForKids']=self.self_declared_made_for_kids
        
        if not (update_snippet == current_web_snippet and update_status == current_web_status):
            need_to_update = True
        
        if not need_to_update:
            self.logger.info("No need to update returning None")
            return None

        request = self.channel.service.videos().update(
            part='snippet,status',
            body=dict(
                snippet=update_snippet,
                status=update_status,
                id=self.id
            )
        )
        
        return request.execute()
        
    def update_from_web(self):
        video = self.__get_web_data()
        if 'tags' not in video['snippet']:
            tags = []
        else:
            tags = video['snippet']['tags']
        if 'description' not in video['snippet']:
            description = ""
        else:
            description = video['snippet']['description']
        if 'selfDeclaredMadeForKids' not in video['status']:
            self_declared_made_for_kids = False
        else:
            self_declared_made_for_kids = video['status']['selfDeclaredMadeForKids']
        if 'defaultAudioLanguage' not in video['snippet']:
            default_audio_language = 'en-US'
        else:
            default_audio_language = video['snippet']['defaultAudioLanguage']
    
        self.published_at = video['snippet']['publishedAt']
        self.channel_id = video['snippet']['channelId']
        self.title = video['snippet']['title']
        self.description = description
        self.thumbnails = video['snippet']['thumbnails']
        self.channel_title = video['snippet']['channelTitle']
        self.tags = tags
        self.category_id = video['snippet']['categoryId']
        self.live_broadcast_content = video['snippet']['liveBroadcastContent']
        self.default_audio_language = default_audio_language
        self.licensed_content = video['contentDetails']['licensedContent']
        self.content_rating = video['contentDetails']['contentRating']
        self.has_custom_thumbnail = video['contentDetails']['hasCustomThumbnail']
        self.upload_status = video['status']['uploadStatus']
        self.privacy_status = video['status']['privacyStatus']
        self.license = video['status']['license']
        self.embeddable = video['status']['embeddable']
        self.public_stats_viewable = video['status']['publicStatsViewable']
        self.made_for_kids = video['status']['madeForKids']
        self.self_declared_made_for_kids = self_declared_made_for_kids
        self.view_count = video['statistics']['viewCount']
        self.like_count = video['statistics']['likeCount']
        self.dislike_count = video['statistics']['dislikeCount']
        self.comment_count = video['statistics']['commentCount']
        self.favorite_count = video['statistics']['favoriteCount']
        self.downloaded = self.__is_downloaded()
        
    
    def download(self, overwrite=False):
        file_name = self.__file_name()
        self.logger.info(f"Downloading {file_name}")
        if pathlib.Path(os.path.join(os.getcwd(),self.__file_name())).is_file():
            self.logger.info(f"File {file_name} already exists.")
            if overwrite:
                self.logger.info("Overwrite set removing file re-downloading")
                os.remove(self.__file_name())
            else:
                self.logger.info("Overwrite not set not downloading")
                return
        
        self.logger.info(f"Attempting to download video portion of {self.title}")
        video_file = None
        vid = self.pytube_obj
        finished = False
        tries = 0
       
        while not finished and tries < Video.MAX_RETRIES + 2:
            try:
                video_file = vid.streams.order_by('resolution').desc().first().download(filename_prefix="video_")
                finished = True
            except Exception as e:
                if tries > Video.MAX_RETRIES:
                    self.logger.error("Too many failed download attempts raising new exception")
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                self.logger.info(f"Attempted {tries} time(s) of a possible {Video.MAX_RETRIES}")
                finished = False
        
    
        self.logger.info(f"Downloaded video for {self.title}")
        
        self.logger.info(f"Attempting to download audio portion of {self.title}")
        
        finished = False
        tries = 0
        while not finished and tries < Video.MAX_RETRIES + 2:
            try:
                audio_file = vid.streams.filter(only_audio=True).order_by('abr').desc().first().download(filename_prefix="audio_") 
                finished = True
            except Exception as e:
                if tries > Video.MAX_RETRIES:
                    self.logger.error("Too many failed download attempts raising new exception")
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                self.logger.info(f"Attempted {tries} time(s) of a possible {Video.MAX_RETRIES}")
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
                audFile = content.getInputFilename(source_audio)
                vidFile = content.getInputFilename(source_video)
                finished = True
            except Exception as e:
                if tries > self.MAX_RETRIES:
                    self.logger.error("Too many failed download attempts raising new exception")
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                self.logger.info(f"Attempted {tries} time(s) of a possible {self.MAX_RETRIES}")
                finished = False
        
        self.logger.info(f"Attempting to merge {vidFile} and {audFile} together as {file_name}")
        finished = False
        tries = 0
        while not finished and tries < self.MAX_RETRIES + 2:
            try:
                self.logger.info("Attempting to merge audio and video")
                ffmpeg.concat(source_video, source_audio, v=1, a=1).output(self.__file_name()).run()
                finished = True
            except Exception as e:
                if tries > self.MAX_RETRIES:
                    self.logger.error("Too many failed download attempts raising new exception")
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                self.logger.info(f"Attempted {tries} time(s) of a possible {Video.MAX_RETRIES}")
                finished = False
                
        self.logger.info(f"Files merged as {file_name}")
    
        self.logger.info("Cleaning up source files....")
        self.logger.info(f"Removing {audFile}")
        os.remove(audFile)
        self.logger.info(f"Removing {vidFile}")
        os.remove(vidFile)
        
    def upload(self):
        file = os.path.join(os.getcwd(),self.__file_name())
        self.logger.info("Creating YouTube Service to allow uploading")
        
        try:
            self.logger.info(f"Attempting to upload {file}")
            self.__initialize_upload()
        except HttpError as e:
            raise e
        
        self.pytube_obj = self.__get_pytube()
        self.update_from_web()