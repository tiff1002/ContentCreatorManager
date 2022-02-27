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
    
    #Private Method to load in credentials from pickle file returning none if no file is present
    def __load__creds(self):
        pickle_file = os.path.join(os.getcwd(),self.__creds_pickle_file_name())
        
        if not os.path.isfile(pickle_file):
            self.logger.info("Pickle File for Google Creds does not exist...Returning None")
            return None

        self.logger.info("Loading Credentials for Google from pickle file")
        with open(pickle_file, 'rb') as token:
            return pickle.load(token)
    
    #Private Method to return the name of the pickle file
    def __creds_pickle_file_name(self):
        return f'token_{YouTube.API_SERVICE_NAME}_{YouTube.API_VERSION}.pickle'
    
    #Private Method to save auth creds to a pickle file
    def __save_creds(self, cred : google.oauth2.credentials.Credentials):
        pickle_file = self.__creds_pickle_file_name()

        self.logger.info(f"Saving Credentials for Google to pickle file: {pickle_file}")
        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)
    
    #private Method to create the youtube service will use pickle file creds if availble and they work otherwise will generate new ones with lient secrets file
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
    
    #Private Method to get channel/playlist id for user's uploads    
    def __get_channel(self):
        result = None
        self.logger.info("Making channels.list API call to get Id for the Channel of the authenticated user")
        #uses channels.list with mine set to true to get authed users channel
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
    
    #Private Method to add all videos on the channel to the media_objects property via the add_video_with_request method after getting the requests for all the vids with __get_videos()
    def __set_videos(self):
        vids = self.__get_videos()
        for vid in vids:
            self.add_video_with_request(vid,self)
    
    #Private Method to get all the video_ids from the channel (also returns the number of pages the data came in as well as providing the length each csv will need to be to make video list calls to grab all channel data
    def __get_playlist_video_ids(self):
        #initialize some variables the method will use
        result = None
        num_pages = 1
        
        self.logger.info("Making intial PlaylistItems.list API call to get first 50 results and the first next_page_token")
        #Grab the first page of data for user's videos and store the results
        try:
            result = self.service.playlistItems().list(
                playlistId=self.id,
                maxResults=50,
                part="contentDetails"
            ).execute()
        except Exception as e:
            self.logger.error(f"Error:\n{e}")
            return None
        self.logger.info("PlaylistIems.list API Call made without exception")
        
        self.logger.info("Adding first page of data to pages")
        pages = []
        pages.append(result['items'])
        
        #initializing the csv_length variable that will be returned it will be set to the number of items in the result and if there is more than one page of data this will get overwritten
        csv_length = result['pageInfo']['totalResults']
        #initializing the next_page_token to None if there is one it will be set
        next_page_token = None
        
        #if the next page token is in the results there are multiple pages of data so set variables based on the length of the results
        if 'nextPageToken' in result:
            self.logger.info("Setting next page token as there are multiple pages of data")
            next_page_token = result['nextPageToken']
            num_pages = math.ceil(result['pageInfo']['totalResults']/result['pageInfo']['resultsPerPage'])
            csv_length = math.ceil(result['pageInfo']['totalResults'] / num_pages);
        
        #Loop through to get other pages of data
        while next_page_token is not None:
            self.logger.info("Making a playlistitems.list call in loop to get remaining data")
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
            
            self.logger.info("Adding page of data to pages")
            pages.append(result['items'])
            
            #Setting to None if this is not overwritten the loop will end
            next_page_token = None
            
            #If there is another page set the token
            if 'nextPageToken' in result:
                self.logger.info("There is another page of data setting the token")
                next_page_token = result['nextPageToken']
                
        #pull ids from the results to return
        video_ids = self.__get_items_from_pages(pages, True)
                
        #puts three return variables into a dict
        return_data = {
            "video_ids":video_ids,
            "num_pages":num_pages,
            "csv_length":csv_length        
        }
        return return_data
    
    #Private Method to pull individual items from pages of data
    def __get_items_from_pages(self, pages, just_ids : bool = False):
        return_data = []
        for p in pages:
            for r in p:
                if just_ids:
                    return_data.append(r['contentDetails']['videoId'])
                else:
                    return_data.append(r)
        return return_data
    
    #Returns a list of requests for all vids on the channel        
    def __get_videos(self):
        #get the channel video IDs and info about how many there are
        playlist_ids = self.__get_playlist_video_ids()
        
        #pull the parts of the dict out as individual variables
        video_ids = playlist_ids['video_ids']
        num_pages = playlist_ids['num_pages']
        csv_length = playlist_ids['csv_length']
        
        #initialize a list to hold the different csv strings that will be used to get the rest of the video data
        id_csvs = []
        
        #loop once for each page of data
        for x in range(num_pages):
            #intialize an empty list to hold the IDs that will make up a csv string of IDs
            ids = []
            #loop once for each item that will be in single csv string
            for y in range(csv_length):
                #use try catch to except the Index Error that will occur depending on the number of results
                try:
                    #use the x and the y and the length we want the csv strings to be to calculate the index of the ID we want to add to the ids list
                    ids.append(video_ids[(x*csv_length)+y])
                except IndexError:
                    self.logger.info("Reached the end of the list of ids")
                    
            #once the y loop finishes ids will be populated with a single csv string worth of ids so using join with ',' to make said csv string and add it to the list of csv strings
            id_csvs.append(",".join(ids))
                    
        #grab full data using the list of csv strings
        pages = self.__get_video_data_from_csvs(id_csvs)
            
        #pull the individual data from the pages of data
        self.logger.info("Looping through the page data to make a list of results to return")    
        results = self.__get_items_from_pages(pages)
        
        #reverse the results so they go in the right order before returning them
        results.reverse()        
        return results

    #private Method to grab data from multiple csv strings provided in form of a list
    def __get_video_data_from_csvs(self, csvs : list):
        #initialize and empty list to store the page data in
        pages = []
        
        #loop once for each csv string and add to the pages list before returning the data
        for csv in csvs:
            pages.append(self.__get_video_data_from_csv(csv))
        return pages
    
    #Private Method to grAB video data from a single csv string using the videos.list api call
    def __get_video_data_from_csv(self, csv : str):
        #initialize the result as None
        result = None
        
        self.logger.info("Making videos.list api call with csv string of Video IDs")
        try:
            result = self.service.videos().list(
                part="snippet,contentDetails,statistics,status",
                id=csv
            ).execute()
        except Exception as e:
            self.logger.error(f"Error:\n{e}")
        
        #return the results
        if 'items' in result:
            return result['items']
        
        #if there was no items in results declare something went wrong and return whatever is there
        self.logger.error(f"Something went wrong and there is no items in the result to return so returning as is:\n{result}")
        return result
    
    #constructor
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
            
    #Method to allow adding a video manually using its id (this assumes it is already uploaded)
    def add_video_with_id(self, ID):
        #creates the Video object only setting the channel and the ID and asking for it to update from the web
        v = contentcreatormanager.media.video.youtube.YouTubeVideo(channel=self, ID=ID, update_from_web=True)
        # Add the video to the media_objects list with the add_video method
        self.add_video(v)
    
    #Method to add a YouTube video to media_objects    
    def add_video(self, vid : contentcreatormanager.media.video.youtube.YouTubeVideo):
        self.add_media(vid)
            
    #Method that will add a video to the media_objects list using a provided request (results from an API call)
    def add_video_with_request(self,request,channel):
        #Checks some of the request results that are optional and initialize them to something to prevent exceptions
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
            
        #use all the details to create the YouTube Video Object
        ytv = contentcreatormanager.media.video.youtube.YouTubeVideo(channel=channel, ID=request['id'], favorite_count=request['statistics']['favoriteCount'],
                                                                     comment_count=request['statistics']['commentCount'], dislike_count=request['statistics']['dislikeCount'],
                                                                     like_count=request['statistics']['likeCount'], view_count=request['statistics']['viewCount'],
                                                                     self_declared_made_for_kids=self_declared_made_for_kids, made_for_kids=request['status']['madeForKids'],
                                                                     public_stats_viewable=request['status']['publicStatsViewable'], embeddable=request['status']['embeddable'],
                                                                     lic=request['status']['license'], privacy_status=request['status']['privacyStatus'], upload_status=request['status']['uploadStatus'],
                                                                     has_custom_thumbnail=request['contentDetails']['hasCustomThumbnail'], content_rating=request['contentDetails']['contentRating'],
                                                                     licensed_content=request['contentDetails']['licensedContent'], default_audio_language=default_audio_language,
                                                                     published_at=request['snippet']['publishedAt'], channel_id=request['snippet']['channelId'], title=request['snippet']['title'],
                                                                     description=description, thumbnails=request['snippet']['thumbnails'], channel_title=request['snippet']['channelTitle'],
                                                                     tags=tags, category_id=request['snippet']['categoryId'], live_broadcast_content=request['snippet']['liveBroadcastContent'])
        #Adds the new video to media_objects with add_video method
        self.add_video(ytv)