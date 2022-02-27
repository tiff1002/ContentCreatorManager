'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.platform.platform
import contentcreatormanager.media.video.youtube
import httplib2
import http.client
import os.path
import google.oauth2.credentials
import google_auth_oauthlib
import pickle
import math
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request as GoogleAuthRequest

class YouTube(contentcreatormanager.platform.platform.Platform):
    '''
    classdocs
    '''
    CLIENT_SECRETS_FILE = 'youtube_client_secret.json'
    
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
    
    def __load__creds(self):
        pickle_file = os.path.join(os.getcwd(),self.__creds_pickle_file_name())
        
        if not os.path.isfile(pickle_file):
            self.logger.info("Pickle File for Google Creds does not exist...Returning None")
            return None

        self.logger.info("Loading Credentials for Google from pickle file")
        with open(pickle_file, 'rb') as token:
            return pickle.load(token)
    
    def __creds_pickle_file_name(self):
        return f'token_{YouTube.API_SERVICE_NAME}_{YouTube.API_VERSION}.pickle'
    
    def __save_creds(self, cred : google.oauth2.credentials.Credentials):
        pickle_file = self.__creds_pickle_file_name()

        self.logger.info(f"Saving Credentials for Google to pickle file: {pickle_file}")
        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)
    
    def __create_service(self):
        self.logger.info("Changing to original dir to load creds")
        os.chdir(self.settings.original_dir)
        
        self.logger.info(f"{YouTube.CLIENT_SECRETS_FILE}, {YouTube.SCOPES}, {YouTube.API_SERVICE_NAME}, {YouTube.API_VERSION}")
        self.logger.info("Attempting to load youtube credentials from pickle file")
        cred = self.__load__creds()

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                self.logger.info("Google creds expired...Refreshing")
                cred.refresh(GoogleAuthRequest())
                self.logger.info("Saving Refreshed creds to pickle file")
            else:
                self.logger.info("Creating Google Credentials...")
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(YouTube.CLIENT_SECRETS_FILE, YouTube.SCOPES)
                cred = flow.run_console()
                self.logger.info("Saving Created creds to pickle file")
            self.__save_creds(cred)
        
        self.logger.info("Changing back to proper folder")
        
        os.chdir(self.settings.folder_location)
        
        self.logger.info("Attempting to build youtube service to return")
        
        try:
            service = googleapiclient.discovery.build(YouTube.API_SERVICE_NAME, YouTube.API_VERSION, credentials = cred)
            self.logger.info(f"{YouTube.API_SERVICE_NAME} service created successfully")
            return service
        except Exception as e:
            self.logger.error(f"something went wrong:\n{e}\nReturning None")
            return None
        
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
    
    def __set_videos(self):
        vids = self.__get_videos()
        for vid in vids:
            self.add_video_with_request(vid,self)
            
    def __get_videos(self):
        result = None
        self.logger.info("Making intial PlaylistItems.list API call to get first 50 results and the first next_page_token")
        
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

    def __init__(self, settings : contentcreatormanager.config.Settings, init_videos : bool = False):
        '''
        Constructor
        '''
        super(YouTube, self).__init__(settings=settings, ID='')
        self.logger = settings.YouTube_logger
        self.logger.info("Initializing Platform Object as a YouTube Platform")
        
        # Explicitly tell the underlying HTTP transport library not to retry, since
        # we are handling retry logic ourselves.
        httplib2.RETRIES = 1
        self.logger.info("Set httplib2.RETRIES to 1 as retry logic is handled in this tool")
        
        
        self.service = self.__create_service()
        self.logger.info("Created and set YouTube service")
        
        self.logger.info("Setting Id for the Channel")
        self.id = self.__get_channel()
        
        if init_videos:
            self.__set_videos()
            
    def add_video_with_id(self, ID):
        v = contentcreatormanager.media.video.youtube.YouTubeVideo(channel=self, ID=ID)
        
        v.update_local()
        
        self.add_video(v)
        
    def add_video(self, vid : contentcreatormanager.media.video.youtube.YouTubeVideo):
        self.add_media(vid)
            
    def add_video_with_request(self,request,channel):
        tags = []
        if not ('tags' not in request['snippet']):
            tags = request['snippet']['tags']
        description = ""
        if not ('description' not in request['snippet']):
            description = request['snippet']['description']
        self_declared_made_for_kids = False
        if not ('selfDeclaredMadeForKids' not in request['status']):
            self_declared_made_for_kids = request['status']['selfDeclaredMadeForKids']
        default_audio_language = 'en-US'
        if not ('defaultAudioLanguage' not in request['snippet']):
            default_audio_language = request['snippet']['defaultAudioLanguage']
        ytv = contentcreatormanager.media.video.youtube.YouTubeVideo(channel=channel, ID=request['id'], favorite_count=request['statistics']['favoriteCount'], comment_count=request['statistics']['commentCount'], dislike_count=request['statistics']['dislikeCount'], like_count=request['statistics']['likeCount'], view_count=request['statistics']['viewCount'], self_declared_made_for_kids=self_declared_made_for_kids, made_for_kids=request['status']['madeForKids'], public_stats_viewable=request['status']['publicStatsViewable'], embeddable=request['status']['embeddable'], lic=request['status']['license'], privacy_status=request['status']['privacyStatus'], upload_status=request['status']['uploadStatus'], has_custom_thumbnail=request['contentDetails']['hasCustomThumbnail'], content_rating=request['contentDetails']['contentRating'], licensed_content=request['contentDetails']['licensedContent'], default_audio_language=default_audio_language, published_at=request['snippet']['publishedAt'], channel_id=request['snippet']['channelId'], title=request['snippet']['title'], description=description, thumbnails=request['snippet']['thumbnails'], channel_title=request['snippet']['channelTitle'], tags=tags, category_id=request['snippet']['categoryId'], live_broadcast_content=request['snippet']['liveBroadcastContent'])
        
        self.add_video(ytv)