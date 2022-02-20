'''
Created on Feb 20, 2022

@author: tiff
'''
import config
import httplib2
import http.client
import pathlib
import os
import math
import pickle
import google_auth_oauthlib
import googleapiclient.discovery
import google.oauth2.credentials
from google.auth.transport.requests import Request as GoogleAuthRequest


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
        pickle_file = self.__creds_pickle_file_name()
 
        if not pathlib.Path(f"{os.getcwd()}\\{pickle_file}").is_file():
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
            video = Video(video_id=vid['items'][0]['id'], favorite_count=vid['items'][0]['statistics']['favoriteCount'], comment_count=vid['items'][0]['statistics']['commentCount'], dislike_count=vid['items'][0]['statistics']['dislikeCount'], like_count=vid['items'][0]['statistics']['likeCount'], view_count=vid['items'][0]['statistics']['viewCount'], self_declared_made_for_kids=vid['items'][0]['status']['selfDeclaredMadeForKids'], made_for_kids=vid['items'][0]['status']['madeForKids'], public_stats_viewable=vid['items'][0]['status']['publicStatsViewable'], embeddable=vid['items'][0]['status']['embeddable'], license=vid['items'][0]['status']['license'], privacy_status=vid['items'][0]['status']['privacyStatus'], upload_status=vid['items'][0]['status']['uploadStatus'], has_custom_thumbnail=vid['items'][0]['contentDetails']['hasCustomThumbnail'], content_rating=vid['items'][0]['contentDetails']['contentRating'], licensed_content=vid['items'][0]['contentDetails']['licensedContent'], default_audio_language=vid['items'][0]['snippet']['defaultAudioLanguage'], published_at=vid['items'][0]['snippet']['publishedAt'], channel_id=vid['items'][0]['snippet']['channelId'], title=vid['items'][0]['snippet']['title'], description=vid['items'][0]['snippet']['description'], thumbnails=vid['items'][0]['snippet']['thumbnails'], channel_title=vid['items'][0]['snippet']['channelTitle'], tags=vid['items'][0]['snippet']['tags'], category_id=vid['items'][0]['snippet']['categoryId'], live_broadcast_content=vid['items'][0]['snippet']['liveBroadcastContent'])
            self.videos.append(video)

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
        
        self.video = []
        self.__set_videos()
    
        
    def refresh_service(self):
        os.chdir(self.original_dir)
        self.YouTube_service = self.create_YouTube_service()
        os.chdir(self.folder_location)
        
        
class Video(object):
    '''
    classdocs
    '''


    def __init__(self, video_id=None, favorite_count='0', comment_count='0', dislike_count='0', like_count='0', view_count='0', self_declared_made_for_kids=False, made_for_kids=False, public_stats_viewable=True, embeddable=True, license='youtube', privacy_status="public", upload_status='notUploaded', has_custom_thumbnail=False, content_rating={}, licensed_content=False, default_audio_language='en-US', published_at=None, channel_id=None, title=None, description=None, thumbnails={}, channel_title=None, tags=[], category_id=22, live_broadcast_content=None):
        '''
        Constructor
        '''
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
        self.licensed_content = licensed_content
        self.content_rating = content_rating
        self.has_custom_thumbnail = has_custom_thumbnail
        self.upload_status = upload_status
        self.privacy_status = privacy_status
        self.license = license
        self.embeddable = embeddable
        self.public_stats_viewable = public_stats_viewable
        self.made_for_kids = made_for_kids
        self.self_declared_made_for_kids = self_declared_made_for_kids
        self.view_count = view_count
        self.like_count = like_count
        self.dislike_count = dislike_count
        self.comment_count = comment_count
        self.favorite_count = favorite_count
