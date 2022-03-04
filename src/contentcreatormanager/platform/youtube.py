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
import random
import time
import googleapiclient.discovery
import googleapiclient.http
from googleapiclient.errors import HttpError
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
    MAX_RETRIES = 25
    
    def __get_parts(self, contentDetails : bool, snippet : bool, statistics : bool, status : bool, 
                        fileDetails : bool, ID : bool, liveStreamingDetails : bool, localizations : bool,
                        player : bool, processingDetails : bool, recordingDetails : bool, suggestions : bool,
                        topicDetails : bool, auditDetails: bool, brandingSettings: bool, contentOwnerDetails : bool):
        """
        Private Method to turn a list of strings to make a part string for an API call based on several bool inputs
        """
        parts = []
        
        if brandingSettings:
            parts.append('brandingSettings')
            
        if auditDetails:
            parts.append('auditDetails')
        
        if contentOwnerDetails:
            parts.append('contentOwnerDetails')
        
        if contentDetails:
            parts.append('contentDetails')
            
        if snippet:
            parts.append('snippet')
            
        if statistics:
            parts.append('statistics')
            
        if status:
            parts.append('status')
            
        if fileDetails:
            parts.append('fileDetails')
        
        if ID:
            parts.append('id')
        
        if liveStreamingDetails:
            parts.append('liveStreamingDetails')
        
        if localizations:
            parts.append('localizations')
        
        if player:
            parts.append('player')
        
        if processingDetails:
            parts.append('processingDetails')
        
        if recordingDetails:
            parts.append('recordingDetails')
        
        if suggestions:
            parts.append('suggestions')
        
        if topicDetails:
            parts.append('topicDetails')
            
        return parts
    
    def __load__creds(self):
        """Private Method to load in credentials from pickle file returning none if no file is present"""
        pickle_file = os.path.join(os.getcwd(),self.__creds_pickle_file_name())
        
        if not os.path.isfile(pickle_file):
            self.logger.info("Pickle File for Google Creds does not exist...Returning None")
            return None

        self.logger.info("Loading Credentials for Google from pickle file")
        with open(pickle_file, 'rb') as token:
            return pickle.load(token)
    
    def __creds_pickle_file_name(self):
        """Private Method to return the file name of the pickle file used for creds"""
        return f'token_{YouTube.API_SERVICE_NAME}_{YouTube.API_VERSION}.pickle'
    
    def __save_creds(self, cred : google.oauth2.credentials.Credentials):
        """Private Method to save auth creds to a pickle file"""
        pickle_file = self.__creds_pickle_file_name()

        self.logger.info(f"Saving Credentials for Google to pickle file: {pickle_file}")
        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)
    
    def __create_service(self):
        """Private Method to create the youtube service will use pickle file creds if availble and they work otherwise will generate new ones with client secrets file"""
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
        
        service = googleapiclient.discovery.build(YouTube.API_SERVICE_NAME, YouTube.API_VERSION, credentials = cred)
        self.logger.info(f"{YouTube.API_SERVICE_NAME} service created successfully")
        return service
        
    def __get_channel(self):
        """Private Method to get channel/playlist id for user's uploads"""
        result = None
        self.logger.info("Making channels.list API call to get Id for the Channel of the authenticated user")
        #uses channels.list with mine set to true to get authed users channel
        try:
            result = self.api_channels_list_mine(contentDetails=True)
        except HttpError as e:
            self.logger.error(f"Error:\n{e}")
            return result
        self.logger.info("Chanels.list API Call made without Exception")
        
        return result['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    def __set_videos(self):
        """Private Method to add all videos on the channel to the media_objects list property"""
        vid_data = self.__get_all_video_data()
        for vid in vid_data:
            self.add_video_with_request(vid)
    
    def __get_playlist_video_ids(self):
        """
        Private Method to get all the video_ids from the channel 
        (also returns the number of pages the data came in as well 
        as providing the length each csv will need to be to make 
        video list calls to grab all channel data)
        """
        #initialize some variables the method will use
        result = None
        num_pages = 1
        
        self.logger.info("Making intial PlaylistItems.list API call to get first 50 results and the first next_page_token")
        #Grab the first page of data for user's videos and store the results        
        try:
            result = self.api_playlistitems_list(contentDetails=True, maxResults=50, playlistId=self.id)
        except HttpError as e:
            self.logger.error(f"Error During API call:\n{e}")
            return None
        self.logger.info("PlaylistIems.list API Call made without exception")
        
        self.logger.info("Adding first page of data to pages")
        pages = [result['items']]
        
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
                result = self.api_playlistitems_list(contentDetails=True, maxResults=50, playlistId=self.id, pageToken=next_page_token)
            except HttpError as e:
                self.logger.error(f"Error:\n{e}")
                return None
            self.logger.info("PlaylistIems.list API Call made without exception")
            
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
    
    def __get_items_from_pages(self, pages, just_ids : bool = False):
        """Private Method to pull individual items from pages of data.  Use this to get API results that are accross multiple pages of data, just provide a list object containing all the pages of data"""
        return_data = []
        for p in pages:
            for r in p:
                if just_ids:
                    return_data.append(r['contentDetails']['videoId'])
                else:
                    return_data.append(r)
        return return_data
          
    def __get_all_video_data(self):
        """Private Method to return a list of requests for all vids on the channel"""
        #get the channel video IDs and info about how many there are
        response = self.__get_playlist_video_ids()
        
        #pull the parts of the dict out as individual variables
        video_ids = response['video_ids']
        num_pages = response['num_pages']
        csv_length = response['csv_length']
        
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

    def __get_video_data_from_csvs(self, csvs : list):
        """Private Method to grab data from multiple csv strings provided in the form of a list"""
        #initialize and empty list to store the page data in
        pages = []
        
        #loop once for each csv string and add to the pages list before returning the data
        for csv in csvs:
            pages.append(self.__get_video_data_from_csv(csv))
        return pages
    
    def __get_video_data_from_csv(self, csv : str):
        """Private Method to grab video data from a single csv string using the videos.list api call"""
        #initialize the result as None
        result = self.api_videos_list(ids=csv, contentDetails=True, snippet=True, statistics=True, status=True)
        
        #return the results
        if 'items' in result:
            return result['items']
        
        #if there was no items in results declare something went wrong and return whatever is there
        self.logger.error(f"Something went wrong and there is no items in the result to return so returning as is:\n{result}")
        return result
    
    def __init__(self, settings : contentcreatormanager.config.Settings, init_videos : bool = False, current_quota_usage : int = 0):
        '''
        Constructor takes a Settings object.  No ID needs to be provided it is grabbed using an API call.  
        init_videos flag (default False) set to True will grab all video data and use it to make video 
        objects and add them to media_objects list property.
        '''
        super(YouTube, self).__init__(settings=settings, ID='')
        self.logger = settings.YouTube_logger
        self.logger.info("Initializing Platform Object as a YouTube Platform")
        
        #setting starting quota usage
        self.quota_usage = current_quota_usage
        
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
        """Method to allow adding a video manually using its id (this assumes it is already uploaded)"""
        #creates the Video object only setting the channel and the ID and asking for it to update from the web
        v = contentcreatormanager.media.video.youtube.YouTubeVideo(channel=self, ID=ID, update_from_web=True)
        # Add the video to the media_objects list with the add_video method
        self.add_video(v)
        return v
        
    def add_video(self, vid : contentcreatormanager.media.video.youtube.YouTubeVideo):
        """Method to add a YouTube video to media_objects"""
        self.add_media(vid)
            
    def add_video_with_request(self,request):
        """Method that will add a video to the media_objects list.  First object data will be set using provided request (results from an API call)"""
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
        ytv = contentcreatormanager.media.video.youtube.YouTubeVideo(channel=self, ID=request['id'], favorite_count=request['statistics']['favoriteCount'],
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
        
    def upload_media(self, ID : str = ''):
        """Method overridden so it will not be used by this type of object"""
        self.logger.warning(f"Can not possibly know the ID of a video that is not uploaded so will not look for {ID} to upload")
        
    def api_videos_list(self, ids : str, contentDetails : bool = False, snippet : bool = False, statistics : bool = False, status : bool = False, 
                        fileDetails : bool = False, ID : bool = False, liveStreamingDetails : bool = False, localizations : bool = False,
                        player : bool = False, processingDetails : bool = False, recordingDetails : bool = False, suggestions : bool = False,
                        topicDetails : bool = False):
        """
        Method for making videos.list api call
        Quota impact: A call to this method has a quota cost of 1 unit.
        Example Call with 0 results: api_videos_list(ids='', contentDetails=True)
        Example Return with 0 results: {'kind': 'youtube#videoListResponse', 'etag': 'YIUPVpqNjppyCWOZfL-19bLb7uk', 'items': [], 'pageInfo': {'totalResults': 0, 'resultsPerPage': 0}}
        Example Call with 1 result: api_videos_list(ids='j61rqh2q6Kg', contentDetails=True)
        Example Return with 1 result: {'kind': 'youtube#videoListResponse', 'etag': 'K-Kq14CaYq6Y_bf5rHY6OjV_4bI', 'items': [{'kind': 'youtube#video', 'etag': '5EHl_ntuFowoftGC2-8fJT76YeE', 'id': 'j61rqh2q6Kg', 'contentDetails': {'duration': 'PT9M23S', 'dimension': '2d', 'definition': 'hd', 'caption': 'false', 'licensedContent': False, 'contentRating': {}, 'projection': 'rectangular', 'hasCustomThumbnail': True}}], 'pageInfo': {'totalResults': 1, 'resultsPerPage': 1}}
        Example Call with multiple results: api_videos_list(ids='j61rqh2q6Kg,dNtR6iekI40', contentDetails=True)
        Example Return with multiple results: {'kind': 'youtube#videoListResponse', 'etag': 'NB9j7iW8etTLjU9tc8mabfK-8vE', 'items': [{'kind': 'youtube#video', 'etag': '5EHl_ntuFowoftGC2-8fJT76YeE', 'id': 'j61rqh2q6Kg', 'contentDetails': {'duration': 'PT9M23S', 'dimension': '2d', 'definition': 'hd', 'caption': 'false', 'licensedContent': False, 'contentRating': {}, 'projection': 'rectangular', 'hasCustomThumbnail': True}}, {'kind': 'youtube#video', 'etag': 'm5p1cKOsvLDy_8urjLjnkAzAVQ0', 'id': 'dNtR6iekI40', 'contentDetails': {'duration': 'PT25M50S', 'dimension': '2d', 'definition': 'hd', 'caption': 'false', 'licensedContent': False, 'contentRating': {}, 'projection': 'rectangular', 'hasCustomThumbnail': False}}], 'pageInfo': {'totalResults': 2, 'resultsPerPage': 2}}
        """
        self.logger.info("Making YouTube API Call to videos.list which costs 1 quota unit")
        quota_cost = 1
        
        parts = self.__get_parts(contentDetails=contentDetails, snippet=snippet, statistics=statistics, status=status, 
                        fileDetails=fileDetails, ID=ID, liveStreamingDetails=liveStreamingDetails, localizations=localizations,
                        player=player, processingDetails=processingDetails, recordingDetails=recordingDetails, suggestions=suggestions,
                        topicDetails=topicDetails, auditDetails=False, brandingSettings=False, contentOwnerDetails=False)
        
        if len(parts) == 0:
            self.logger.error("At least one part required api call will not be made")
            return None
        
        part = ','.join(parts)
        
        self.logger.info(f"API call part: {part} id: {ids}")
        
        request = self.service.videos().list(part=part, id=ids)
        
        result = request.execute()
        
        self.quota_usage += quota_cost
        
        self.logger.info(f"API call made.  Current Quota Usage: {self.quota_usage}")
        
        return result
    
    def api_videos_insert_req(self, file : str, snippet_title : str, snippet_description : str, snippet_tags : list, snippet_categoryId : int
                          , snippet_defaultLanguage : str, status_embeddable : bool, status_license : str,
                          status_privacyStatus : str, status_publicStatsViewable : bool, status_selfDeclaredMadeForKids : bool,
                          contentDetails : bool = False, snippet : bool = False, statistics : bool = False, status : bool = False, 
                        fileDetails : bool = False, ID : bool = False, liveStreamingDetails : bool = False, localizations : bool = False,
                        player : bool = False, processingDetails : bool = False, recordingDetails : bool = False, suggestions : bool = False,
                        topicDetails : bool = False, notifySubscribers : bool = True):
        """
        Method for making videos.insert api call
        Quota impact: A call to this method has a quota cost of 1600 units, but the call will not be made in this method.  This just returns the request ready to use.
        Example Call: api_videos_insert_req(file="D:\\Python\\workspace\\Content Creator Manager\\src\\test\\upload_test.mp4", snippet_title='Test Upload', snippet_description='Test Description', snippet_tags=['test1','test2'], snippet_categoryId=22, snippet_defaultLanguage='en-US', status_embeddable=True, status_license='youtube', status_privacyStatus='private', status_publicStatsViewable=True, status_selfDeclaredMadeForKids=False, snippet=True, status=True)
        Returns a googleapiclient.http.HttpRequest object to be fed to api_videos_insert_exec
        """
        self.logger.info("Making YouTube API Call to videos.insert which costs 1600 quota unit")
        
        parts = self.__get_parts(contentDetails=contentDetails, snippet=snippet, statistics=statistics, status=status, 
                        fileDetails=fileDetails, ID=ID, liveStreamingDetails=liveStreamingDetails, localizations=localizations,
                        player=player, processingDetails=processingDetails, recordingDetails=recordingDetails, suggestions=suggestions,
                        topicDetails=topicDetails, auditDetails=False, brandingSettings=False, contentOwnerDetails=False)
        
        
        if len(parts) == 0:
            self.logger.error("At least one part required api call will not be made")
            return None
        
        part = ','.join(parts)
        
        snippet_dict = {'title':snippet_title, 'description':snippet_description, 'tags':snippet_tags, 'categoryId':snippet_categoryId, 'defaultLanguage':snippet_defaultLanguage}
        status_dict = {'embeddable':status_embeddable, 'license':status_license, 'privacyStatus':status_privacyStatus, 'publicStatsViewable':status_publicStatsViewable, 'selfDeclaredMadeForKids':status_selfDeclaredMadeForKids}
        
        body = {'snippet':snippet_dict,'status':status_dict}        
        
        self.logger.info(f"API call part: {part}, body: {body}, notifySubscribers: {notifySubscribers}, video file: {file}")
        
        request = self.service.videos().insert(body=body, media_body=googleapiclient.http.MediaFileUpload(file, chunksize=-1, resumable=True), part=part, notifySubscribers=notifySubscribers)
        
        return request
    
    def api_videos_insert_exec(self, request):
        """
        Method that takes the videos.insert request and completes it in a resumable fashion
        Example Call: api_videos_insert_exec(contentcreatormanager.platform.youtube.YouTube().api_videos_insert_req(file="D:\\Python\\workspace\\Content Creator Manager\\src\\test\\upload_test.mp4", snippet_title='Test Upload', snippet_description='Test Description', snippet_tags=['test1','test2'], snippet_categoryId=22, snippet_defaultLanguage='en-US', status_embeddable=True, status_license='youtube', status_privacyStatus='private', status_publicStatsViewable=True, status_selfDeclaredMadeForKids=False, snippet=True, status=True))
        Example Result: (None, {'kind': 'youtube#video', 'etag': 'f0g_zDeZkHqi39F3hsc_MVvuhw0', 'id': 'I5VIcY3rjQI', 'snippet': {'publishedAt': '2022-03-02T17:23:18Z', 'channelId': 'UCidrHvFXBvyesh1hbOR2rTw', 'title': 'Test Upload', 'description': 'Test Description', 'thumbnails': {'default': {'url': 'https://i9.ytimg.com/vi/I5VIcY3rjQI/default.jpg?sqp=CMDO_pAG&rs=AOn4CLDWOQRH2ykKnWeEllu8sT9f7iKzaw', 'width': 120, 'height': 90}, 'medium': {'url': 'https://i9.ytimg.com/vi/I5VIcY3rjQI/mqdefault.jpg?sqp=CMDO_pAG&rs=AOn4CLD21pKxtGpntSd-cOYEZRz0EeDjJA', 'width': 320, 'height': 180}, 'high': {'url': 'https://i9.ytimg.com/vi/I5VIcY3rjQI/hqdefault.jpg?sqp=CMDO_pAG&rs=AOn4CLCB7sXMw2BEO_Kn6fwaZXJkWwvdMg', 'width': 480, 'height': 360}}, 'channelTitle': 'Tech Girl Tiff', 'tags': ['test1', 'test2'], 'categoryId': '22', 'liveBroadcastContent': 'none', 'defaultLanguage': 'en-US', 'localized': {'title': 'Test Upload', 'description': 'Test Description'}}, 'status': {'uploadStatus': 'uploaded', 'privacyStatus': 'private', 'license': 'youtube', 'embeddable': True, 'publicStatsViewable': True, 'selfDeclaredMadeForKids': False}})
        """
        quota_cost = 1600
        self.logger.info("Completing YouTube videos.insert API call")
        response = None
        error = None
        retry = 0

        while response is None:
            try:
                self.logger.info('Uploading file...') 
                response = request.next_chunk()
                if(response is not None):
                    self.logger.info(f"Checking Response for id:\n{response}")
                    if('id' in response[1]):
                        self.logger.info(f"Video id \"{response[1]['id']}\" was successfully uploaded.")
                    else:
                        self.logger.warning(f"The upload failed with an unexpected response: {response}")
                        return response
            except HttpError as e:
                if e.resp.status in contentcreatormanager.platform.youtube.YouTube.RETRIABLE_STATUS_CODES:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise e
            except contentcreatormanager.platform.youtube.YouTube.RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > YouTube.MAX_RETRIES:
                    self.logger.error('No longer attempting to retry.')
                    return response
                    

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                self.logger.info(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)
        
        self.logger.info("Videos.insert call to YouTube API complete")
        
        self.quota_usage += quota_cost
        
        self.logger.info(f"API call made.  Current Quota Usage: {self.quota_usage}")
        
        return response
    
    def api_videos_update(self, snippet_categoryId : int, snippet_defaultLanguage : str, snippet_description : str, snippet_tags : list, snippet_title : str, 
                          status_embeddable : bool, status_license : str, status_privacyStatus : str, status_publicStatsViewable : bool, status_selfDeclaredMadeForKids : bool,
                          vid_id : str, contentDetails : bool = False, snippet : bool = False, statistics : bool = False, status : bool = False, 
                        fileDetails : bool = False, ID : bool = False, liveStreamingDetails : bool = False, localizations : bool = False,
                        player : bool = False, processingDetails : bool = False, recordingDetails : bool = False, suggestions : bool = False,
                        topicDetails : bool = False):
        """
        Method for making videos.update api call
        Quota impact: A call to this method has a quota cost of 50 units.
        Example Call: api_videos_update(snippet_categoryId=22, snippet_defaultLanguage='en-US', snippet_description="So one of my passions/hobbies is cooking.  Often times I drop a hobby and seldom pick it back up.  With cooking I always come back (possibly because of my adjacent hobby of eating).  Lately I have been getting into baking in an attempt to ruin my diet and all the weight loss.  Anyway I decided to make and film the making of a 3 layer lemon flavored cake.  It is frosted with a lemon buttercream frosting and there is lemon curd between the middle layers in addition to the frosting.  I am mostly following recipes I found here:\n\nhttps://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbGd1RXBwZjZpYUVnUTI4N3dCdVdMUmFtT00yUXxBQ3Jtc0tuNFBMUzVEQUs2R3g3aFVoQmc3Vk9GS0p5dnFDN25ONDhNRWZiS3RTOEpkNHhFUXctRUpoMjk1OUpwandQTVhNZlFydmZ1bkZGeWNpbl9yRW5oeExmZHUyMXhaU1psQ3htcmtuSGFWODBFTmVaeVJlRQ&q=https%3A%2F%2Fwww.biggerbolderbaking.com%2Flemon-curd%2F\nhttps://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbENwUmlDZThveG1DWXhaZURaNHpjTkhuTjNUQXxBQ3Jtc0ttZ084aGREQ3JQaGs3Y3Noc19PQ3pvSXNLQ052ZzZLaVRLNkVrSjZuMmM1MUoxTFZQczhuS1BVTmtUUnU3R1RuaXlfaDdqdjZhNUZqNElneVBGZE91M1hPelBPOEZLT2tscmtZOXZZS0xPMDFwY0V6TQ&q=https%3A%2F%2Fwww.biggerbolderbaking.com%2Flemon-cake-with-lemon-buttercream%2F\n\nI hope you enjoy and let me know what you think :)", snippet_tags=['cooking','baking','lemon','lemon curd','curd','cake','layers','frosting','buttercream','buttercream frosting','american buttercream','lemon buttercream','lemon buttercream frosting','american lemon buttercream','american lemon buttercream frosting','cake making','decorating'], snippet_title='(0153) Tiff Makes a Three Layer Lemon Cake with Buttercream and Lemon Curd ! ! !', status_embeddable=True, status_license='youtube', status_privacyStatus='public', status_publicStatsViewable=True, status_selfDeclaredMadeForKids=False, vid_id='j61rqh2q6Kg', snippet=True, status=True)
        Example Return: {'kind': 'youtube#video', 'etag': 'uQM_y4xDGhzWwVA6PKYObhbMRrc', 'id': 'j61rqh2q6Kg', 'snippet': {'publishedAt': '2022-02-11T23:13:19Z', 'channelId': 'UCidrHvFXBvyesh1hbOR2rTw', 'title': '(0153) Tiff Makes a Three Layer Lemon Cake with Buttercream and Lemon Curd ! ! !', 'description': 'So one of my passions/hobbies is cooking.  Often times I drop a hobby and seldom pick it back up.  With cooking I always come back (possibly because of my adjacent hobby of eating).  Lately I have been getting into baking in an attempt to ruin my diet and all the weight loss.  Anyway I decided to make and film the making of a 3 layer lemon flavored cake.  It is frosted with a lemon buttercream frosting and there is lemon curd between the middle layers in addition to the frosting.  I am mostly following recipes I found here:\n\nhttps://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbGd1RXBwZjZpYUVnUTI4N3dCdVdMUmFtT00yUXxBQ3Jtc0tuNFBMUzVEQUs2R3g3aFVoQmc3Vk9GS0p5dnFDN25ONDhNRWZiS3RTOEpkNHhFUXctRUpoMjk1OUpwandQTVhNZlFydmZ1bkZGeWNpbl9yRW5oeExmZHUyMXhaU1psQ3htcmtuSGFWODBFTmVaeVJlRQ&q=https%3A%2F%2Fwww.biggerbolderbaking.com%2Flemon-curd%2F\nhttps://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbENwUmlDZThveG1DWXhaZURaNHpjTkhuTjNUQXxBQ3Jtc0ttZ084aGREQ3JQaGs3Y3Noc19PQ3pvSXNLQ052ZzZLaVRLNkVrSjZuMmM1MUoxTFZQczhuS1BVTmtUUnU3R1RuaXlfaDdqdjZhNUZqNElneVBGZE91M1hPelBPOEZLT2tscmtZOXZZS0xPMDFwY0V6TQ&q=https%3A%2F%2Fwww.biggerbolderbaking.com%2Flemon-cake-with-lemon-buttercream%2F\n\nI hope you enjoy and let me know what you think :)', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/j61rqh2q6Kg/default.jpg', 'width': 120, 'height': 90}, 'medium': {'url': 'https://i.ytimg.com/vi/j61rqh2q6Kg/mqdefault.jpg', 'width': 320, 'height': 180}, 'high': {'url': 'https://i.ytimg.com/vi/j61rqh2q6Kg/hqdefault.jpg', 'width': 480, 'height': 360}}, 'channelTitle': 'Tech Girl Tiff', 'tags': ['american buttercream', 'american lemon buttercream', 'american lemon buttercream frosting', 'baking', 'buttercream', 'buttercream frosting', 'cake', 'cake making', 'cooking', 'curd', 'decorating', 'frosting', 'layers', 'lemon', 'lemon buttercream', 'lemon buttercream frosting', 'lemon curd'], 'categoryId': '22', 'liveBroadcastContent': 'none', 'defaultLanguage': 'en-US', 'localized': {'title': '(0153) Tiff Makes a Three Layer Lemon Cake with Buttercream and Lemon Curd ! ! !', 'description': 'So one of my passions/hobbies is cooking.  Often times I drop a hobby and seldom pick it back up.  With cooking I always come back (possibly because of my adjacent hobby of eating).  Lately I have been getting into baking in an attempt to ruin my diet and all the weight loss.  Anyway I decided to make and film the making of a 3 layer lemon flavored cake.  It is frosted with a lemon buttercream frosting and there is lemon curd between the middle layers in addition to the frosting.  I am mostly following recipes I found here:\n\nhttps://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbGd1RXBwZjZpYUVnUTI4N3dCdVdMUmFtT00yUXxBQ3Jtc0tuNFBMUzVEQUs2R3g3aFVoQmc3Vk9GS0p5dnFDN25ONDhNRWZiS3RTOEpkNHhFUXctRUpoMjk1OUpwandQTVhNZlFydmZ1bkZGeWNpbl9yRW5oeExmZHUyMXhaU1psQ3htcmtuSGFWODBFTmVaeVJlRQ&q=https%3A%2F%2Fwww.biggerbolderbaking.com%2Flemon-curd%2F\nhttps://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbENwUmlDZThveG1DWXhaZURaNHpjTkhuTjNUQXxBQ3Jtc0ttZ084aGREQ3JQaGs3Y3Noc19PQ3pvSXNLQ052ZzZLaVRLNkVrSjZuMmM1MUoxTFZQczhuS1BVTmtUUnU3R1RuaXlfaDdqdjZhNUZqNElneVBGZE91M1hPelBPOEZLT2tscmtZOXZZS0xPMDFwY0V6TQ&q=https%3A%2F%2Fwww.biggerbolderbaking.com%2Flemon-cake-with-lemon-buttercream%2F\n\nI hope you enjoy and let me know what you think :)'}, 'defaultAudioLanguage': 'en-US'}, 'status': {'uploadStatus': 'processed', 'privacyStatus': 'public', 'license': 'youtube', 'embeddable': True, 'publicStatsViewable': True, 'selfDeclaredMadeForKids': False}}
        """
        self.logger.info("Making YouTube API Call to videos.update which costs 50 quota units")
        quota_cost = 50
        
        parts = self.__get_parts(contentDetails=contentDetails, snippet=snippet, statistics=statistics, status=status, 
                        fileDetails=fileDetails, ID=ID, liveStreamingDetails=liveStreamingDetails, localizations=localizations,
                        player=player, processingDetails=processingDetails, recordingDetails=recordingDetails, suggestions=suggestions,
                        topicDetails=topicDetails, auditDetails=False, brandingSettings=False, contentOwnerDetails=False)
        
        if len(parts) == 0:
            self.logger.error("At least one part required api call will not be made")
            return None
        
        part = ','.join(parts)
        
        snippet_dict = {'categoryId':snippet_categoryId, 'defaultLanguage':snippet_defaultLanguage, 'description':snippet_description, 'tags':snippet_tags, 'title':snippet_title}
        status_dict = {'embeddable':status_embeddable, 'license':status_license, 'privacyStatus':status_privacyStatus, 'publicStatsViewable':status_publicStatsViewable, 'selfDeclaredMadeForKids':status_selfDeclaredMadeForKids}
        
        body = {'snippet':snippet_dict, 'status':status_dict, 'id':vid_id}                       
        
        self.logger.info(f"API call part: {part} body: {body}")
        
        request = self.service.videos().update(body=body, part=part)
        
        result = request.execute()
        
        self.quota_usage += quota_cost
        
        self.logger.info(f"API call made.  Current Quota Usage: {self.quota_usage}")
        
        return result
    
    def api_videos_delete(self, ID : str):
        """
        Method for making videos.delete api call
        Quota impact: A call to this method has a quota cost of 50 units.
        If successful, this method returns an HTTP 204 response code (No Content).  The response and request returned in a dict
        Example Call: api_videos_delete(ID='I5VIcY3rjQI')
        Example Return: {'response': '', 'request': <googleapiclient.http.HttpRequest object at 0x000001A492BA9F60>}
        """
        self.logger.info("Making YouTube API Call to videos.delete which costs 50 quota units")
        quota_cost = 50
        
        self.logger.info(f"API call id: {ID}")
        
        request = self.service.videos().delete(id=ID)
        
        response = request.execute()
        
        result = {'response':response,'request':request}
        
        self.quota_usage += quota_cost
        
        self.logger.info(f"API call made.  Current Quota Usage: {self.quota_usage}")
        
        return result
    
    def api_thumbnails_set(self):
        """
        Method for making thumbnails.set api call
        Quota impact: A call to this method has a quota cost of approximately 50 units.
        """
        quota_cost = 50
        return
    
    def api_playlistitems_list(self, contentDetails : bool = False, snippet : bool = False, status : bool = False, ID : bool = False, ids : str = '', playlistId : str = '',
                               maxResults : int = 50, pageToken : str = '', videoId : str = ''):
        """
        Method for making playlistitems.list api call
        Quota impact: A call to this method has a quota cost of 1 unit.
        If the playlist is not found it will throw googleapiclient.errors.HttpError
        Example Call without pageToken: api_playlistitems_list(contentDetails=True, playlistId='UUidrHvFXBvyesh1hbOR2rTw', maxResults=3)
        Example Results without pageToken: {'kind': 'youtube#playlistItemListResponse', 'etag': 'tmoSEcMYkIzJ5mSfpKyhHz_6fxo', 'nextPageToken': 'EAAaBlBUOkNBTQ', 'items': [{'kind': 'youtube#playlistItem', 'etag': '3RVnrGFLI5QkgzRg7LbnUTtH62w', 'id': 'VVVpZHJIdkZYQnZ5ZXNoMWhiT1IyclR3Lmo2MXJxaDJxNktn', 'contentDetails': {'videoId': 'j61rqh2q6Kg', 'videoPublishedAt': '2022-02-11T23:13:19Z'}}, {'kind': 'youtube#playlistItem', 'etag': 'KbGLhEYOjfwxSQVdKE5Pf6Pp92Y', 'id': 'VVVpZHJIdkZYQnZ5ZXNoMWhiT1IyclR3LmROdFI2aWVrSTQw', 'contentDetails': {'videoId': 'dNtR6iekI40', 'videoPublishedAt': '2021-10-02T18:00:08Z'}}, {'kind': 'youtube#playlistItem', 'etag': 'QgGQdMYagwQGQm7i2hKZJ2X6tv4', 'id': 'VVVpZHJIdkZYQnZ5ZXNoMWhiT1IyclR3LmhBTXBfQlFEZjAw', 'contentDetails': {'videoId': 'hAMp_BQDf00', 'videoPublishedAt': '2021-10-02T12:00:32Z'}}], 'pageInfo': {'totalResults': 158, 'resultsPerPage': 3}}
        Example Call with pageToken: api_playlistitems_list(contentDetails=True, playlistId='UUidrHvFXBvyesh1hbOR2rTw', maxResults=3, pageToken='EAAaBlBUOkNBTQ')
        Example Results with pageToken: {'kind': 'youtube#playlistItemListResponse', 'etag': '2ixEvQy_1aHNH3YpSIv_nplMJvs', 'nextPageToken': 'EAAaBlBUOkNBWQ', 'prevPageToken': 'EAEaBlBUOkNBTQ', 'items': [{'kind': 'youtube#playlistItem', 'etag': 'QgGQdMYagwQGQm7i2hKZJ2X6tv4', 'id': 'VVVpZHJIdkZYQnZ5ZXNoMWhiT1IyclR3LmhBTXBfQlFEZjAw', 'contentDetails': {'videoId': 'hAMp_BQDf00', 'videoPublishedAt': '2021-10-02T12:00:32Z'}}, {'kind': 'youtube#playlistItem', 'etag': 'R4AzQocoTVqgoUIHkVGWMx7OtAA', 'id': 'VVVpZHJIdkZYQnZ5ZXNoMWhiT1IyclR3LkhZTTZRT1dKT0Q4', 'contentDetails': {'videoId': 'HYM6QOWJOD8', 'videoPublishedAt': '2021-10-01T18:00:05Z'}}, {'kind': 'youtube#playlistItem', 'etag': '42I4J4EAopmbwZ3p9VtanWygqlM', 'id': 'VVVpZHJIdkZYQnZ5ZXNoMWhiT1IyclR3LkkyVTB2SUZzc2lz', 'contentDetails': {'videoId': 'I2U0vIFssis', 'videoPublishedAt': '2021-10-01T12:00:10Z'}}], 'pageInfo': {'totalResults': 158, 'resultsPerPage': 3}}
        """
        if (playlistId == '' and ids == '') or (playlistId != '' and ids != ''):
            self.logger.error("ids (comma-separated list of one or more unique playlist item IDs.) or playlistId (unique ID of the playlist for which you want to retrieve playlist items) must be set but both can not be")
            return
        
        self.logger.info("Making YouTube API Call to playlistitems.list which costs 1 quota unit")
        quota_cost = 1
        
        parts = self.__get_parts(contentDetails=contentDetails, snippet=snippet, statistics=False, status=status, 
                        fileDetails=False, ID=ID, liveStreamingDetails=False, localizations=False,
                        player=False, processingDetails=False, recordingDetails=False, suggestions=False,
                        topicDetails=False, auditDetails=False, brandingSettings=False, contentOwnerDetails=False)
        
        if len(parts) == 0:
            self.logger.error("At least one part required api call will not be made")
            return None
        
        part = ','.join(parts)
        
        if playlistId == '':
            if videoId != '' and pageToken != '':
                request = self.service.playlistItems().list(part=part, maxResults=maxResults, id=ids, videoId=videoId, pageToken=pageToken)
            elif pageToken != '':
                request = self.service.playlistItems().list(part=part, maxResults=maxResults, id=ids, pageToken=pageToken)
            elif videoId != '':
                request = self.service.playlistItems().list(part=part, maxResults=maxResults, id=ids, videoId=videoId)
            else:
                request = self.service.playlistItems().list(part=part, maxResults=maxResults, id=ids)
        elif ids == '':
            if videoId != '' and pageToken != '':
                request = self.service.playlistItems().list(part=part, maxResults=maxResults, playlistId=playlistId, videoId=videoId, pageToken=pageToken)
            elif pageToken != '':
                request = self.service.playlistItems().list(part=part, maxResults=maxResults, playlistId=playlistId, pageToken=pageToken)
            elif videoId != '':
                request = self.service.playlistItems().list(part=part, maxResults=maxResults, playlistId=playlistId, videoId=videoId)
            else:
                request = self.service.playlistItems().list(part=part, maxResults=maxResults, playlistId=playlistId)
            
        
        
        
        self.logger.info(f"API call being made")        
        
        result = request.execute()
        
        self.quota_usage += quota_cost
        
        self.logger.info(f"API call made.  Current Quota Usage: {self.quota_usage}")
        
        return result
    
    def api_playlistitems_insert(self):
        """
        Method for making playlistitems.insert api call
        Quota impact: A call to this method has a quota cost of 50 units.
        """
        quota_cost = 50
        return
    
    def api_playlistitems_update(self):
        """
        Method for making playlistitems.update api call
        Quota impact: A call to this method has a quota cost of 50 units.
        """
        quota_cost = 50
        return
    
    def api_playlistitems_delete(self):
        """
        Method for making playlistitems.delete api call
        Quota impact: A call to this method has a quota cost of 50 units.
        """
        quota_cost = 50
        return
    
    def api_channels_list_mine(self, auditDetails: bool = False, brandingSettings: bool = False, contentDetails : bool = False, 
                               contentOwnerDetails : bool = False, ID : bool = False, localizations : bool = False, snippet : bool = False, 
                               statistics : bool = False, status : bool = False, topicDetails : bool = False):
        """
        Method for making channels.list api call
        Quota impact: A call to this method has a quota cost of 1 unit.
        Example Call: api_channels_list_mine(contentDetails=True)
        Example Result: {'kind': 'youtube#channelListResponse', 'etag': 'b4o7PvIgje6iZZ7iFDX25diGSSo', 'pageInfo': {'totalResults': 1, 'resultsPerPage': 5}, 'items': [{'kind': 'youtube#channel', 'etag': 'k87yoSbtKhfiY4D7eR6qtUEC7s8', 'id': 'UCidrHvFXBvyesh1hbOR2rTw', 'contentDetails': {'relatedPlaylists': {'likes': 'LL', 'uploads': 'UUidrHvFXBvyesh1hbOR2rTw'}}}]}
        """
        self.logger.info("Making YouTube API Call to channels.list with mine set to True which costs 1 quota unit")
        quota_cost = 1
        
        parts = self.__get_parts(contentDetails=contentDetails, snippet=snippet, statistics=statistics, status=status, 
                        fileDetails=False, ID=ID, liveStreamingDetails=False, localizations=localizations,
                        player=False, processingDetails=False, recordingDetails=False, suggestions=False,
                        topicDetails=topicDetails, auditDetails=auditDetails, brandingSettings=brandingSettings, contentOwnerDetails=contentOwnerDetails)
        
        if len(parts) == 0:
            self.logger.error("At least one part required api call will not be made")
            return None
        
        part = ','.join(parts)
        
        self.logger.info(f"API call part: {part} mine: True")
        
        request = self.service.channels().list(part=part, mine=True)
        
        result = request.execute()
        
        self.quota_usage += quota_cost
        
        self.logger.info(f"API call made.  Current Quota Usage: {self.quota_usage}")
        
        return result