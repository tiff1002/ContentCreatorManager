'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.video.video
import pytube
import os.path
import random
import time
import contentcreatormanager.platform.youtube
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

class YouTubeVideo(contentcreatormanager.media.video.video.Video):
    '''
    classdocs
    '''
    
    BASE_URL = "https://www.youtube.com/watch?v="
    
    MAX_RETRIES = 25
    
    def __pytube_download_video(self):
        """Private Method to download the video portion of this YouTube Video Object"""
        self.logger.info(f"Attempting to download video portion of {self.title}")
        video_file = None
        finished = False
        tries = 0
       
        #pytube has weird transient failures that you just keep trying and things work so this loop does that to a point for the video
        while not finished and tries < YouTubeVideo.MAX_RETRIES + 2:
            try:
                video_file = self.pytube_obj.streams.order_by('resolution').desc().first().download(filename_prefix="video_")
                finished = True
            except Exception as e:
                if tries > YouTubeVideo.MAX_RETRIES:
                    self.logger.error("Too many failed download attempts raising new exception")
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                self.logger.info(f"Attempted {tries} time(s) of a possible {YouTubeVideo.MAX_RETRIES}")
                finished = False
        
    
        self.logger.info(f"Downloaded video for {self.title}")
        
        return video_file
        
        
    def __pytube_download_audio(self):
        """Private Method to download the audio portion of the YouTube Video Object"""
        self.logger.info(f"Attempting to download audio portion of {self.title}")
        #pytube has weird transient failures that you just keep trying and things work so this loop does that to a point for the audio
        finished = False
        tries = 0
        while not finished and tries < YouTubeVideo.MAX_RETRIES + 2:
            try:
                audio_file = self.pytube_obj.streams.filter(only_audio=True).order_by('abr').desc().first().download(filename_prefix="audio_") 
                finished = True
            except Exception as e:
                if tries > YouTubeVideo.MAX_RETRIES:
                    self.logger.error("Too many failed download attempts raising new exception")
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                self.logger.info(f"Attempted {tries} time(s) of a possible {YouTubeVideo.MAX_RETRIES}")
                finished = False
        
        self.logger.info(f"Downloaded audio for {self.title}")
        
        return audio_file
    
    def __pytube_download(self, overwrite : bool = False):
        """Private Method to download a video from YouTube using pytube.  Optional parameter overwrite is a bool that defaults to False.  If set to true an existing file will be overwritten."""
        #set variables for file name and path
        file_name = os.path.basename(self.file)
        file_path = self.file
        self.logger.info(f"Downloading {file_name}")
        
        #check for the file so redownload can be avoided unless overwrite is set to true
        if os.path.isfile(file_path):
            self.logger.info(f"File {file_name} already exists.")
            if overwrite:
                self.logger.info("Overwrite set removing file re-downloading")
                os.remove(self.file)
            else:
                self.logger.info("Overwrite not set not downloading")
                return
        
        video_file = self.__pytube_download_video()
        audio_file = self.__pytube_download_audio()
        
        self.combine_audio_and_video_files(video_file, audio_file)
    
    def __get_web_data(self):
        """Private Method to make a call method videos.list to the YouTube API and returns the results.  This is using self.id for the lookup"""
        request = self.channel.service.videos().list(
            part="snippet,contentDetails,statistics,status",
            id=self.id
        )
        result = request.execute()
        
        return result['items'][0]
    
    def __get_pytube(self, use_oauth=True):
        """Private method that returns the pytube.YouTube object for this YouTubeVideo"""
        url = f"{YouTubeVideo.BASE_URL}{self.id}"
        return pytube.YouTube(url, use_oauth=use_oauth)
    
    def __initialize_upload(self):
        """Private Method to initialize a resumable upload of the Video to Youtube using the videos.insert API call.  This is a modified version of the example found at https://developers.google.com/youtube/v3/guides/uploading_a_video"""
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
            media_body=MediaFileUpload(self.file, chunksize=-1, resumable=True)
        )
        self.logger.info("returning resumable_upload private method to create a resumable upload")
        return self.__resumable_upload(insert_request)
    
    def __resumable_upload(self, request):
        """Private Method to finish the 'resumable' upload that is initialized in the __initialize_upload method.  Slightly modified version of the example found here https://developers.google.com/youtube/v3/guides/uploading_a_video"""
        response = None
        error = None
        retry = 0
        vidID = None
        while response is None:
            try:
                self.logger.info('Uploading file...') 
                response = request.next_chunk()
                if(response is not None):
                    self.logger.info(f"Checking Response for id:\n{response}")
                    if('id' in response[1]):
                        self.logger.info(f"Video id \"{response[1]['id']}\" was successfully uploaded.")
                        vidID = response[1]['id']
                    else:
                        self.logger.warning(f"The upload failed with an unexpected response: {response}")
                        return
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
                if retry > YouTubeVideo.MAX_RETRIES:
                    exit('No longer attempting to retry.')

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                self.logger.info(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)
        self.logger.info(f"setting ID to {vidID}")
        self.id = vidID
    
    def __init__(self, channel, ID : str = None, favorite_count : str ='0', comment_count : str ='0', dislike_count : str ='0', like_count : str ='0',
                 view_count : str ='0', self_declared_made_for_kids : bool =False, made_for_kids : bool =False, public_stats_viewable : bool =True,
                 embeddable : bool =True, lic : str ='youtube', privacy_status : str ="public", upload_status : str ='notUploaded',
                 has_custom_thumbnail : bool =False, content_rating : dict ={}, licensed_content : bool =False, 
                 default_audio_language : str ='en-US', published_at=None, channel_id=None, title=None, description=None, file_name : str = '', update_from_web : bool = False,
                 thumbnails : dict ={}, channel_title=None, tags : list =[], category_id : int =22, live_broadcast_content=None, new_video : bool =False):
        '''
        Constructor takes a YouTube Platform object as its only parameter without a default value.  All properties can be set on creation of the Object.  
        If the object is a new video not yet on YouTube set the new_video flag to True, and if you want the object to be updated based on a web lookup
        with the ID set the update_local flag to True.
        '''
        self.title = title
        super(YouTubeVideo, self).__init__(platform=channel,ID=ID,file_name=file_name)
        self.logger = self.settings.YouTube_logger
        
        self.logger.info("Initializing Video Object as a YouTube Video Object")
        
        self.channel = channel
        
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
        
        #if the new_video flag is set we do not set the pytube object since we cant
        if new_video:
            self.logger.info("new_video flag set.  Not attempting to initialize pytube_obj variable")
            self.pytube_obj = None
        #if it is not new it should be uploaded and we can make the pytube object
        else:
            self.logger.info("new_video flag not set.  Attempting to initialize pytube_obj property")
            self.pytube_obj = self.__get_pytube()
            if update_from_web:
                self.logger.info("update_video flag set.  Grabbing Video details from YouTube")
                self.update_local()
            
        self.logger.info("YouTube Video Object initialized")
        
    def delete_web(self, do_not_download_before_delete : bool = False):
        """
        Method to make the videos.delete API call to youtube and return the results.  If the video is not downloaded and you do 
        not want to download it before removal from YouTube set the do_not_download_before_delete flag to True
        """
        self.logger.info(f"Preparing to delete video with ID {self.id} from YouTube")
        
        if not self.is_downloaded() and not do_not_download_before_delete:
            self.logger.warning("File for video not found.  Downloading before removal")
            self.download()
        
        self.logger.info("Making videos.delete api call")
        request = self.channel.service.videos().delete(
            id=self.id
        )
        result = request.execute()
        
        tries_left = YouTubeVideo.MAX_RETRIES
        while self.is_uploaded() and tries_left > 0:
            self.logger.warning(f"Video still found on YouTube.  Sleeping a minute and checking again.")
            time.sleep(60)
            tries_left -= 1
        
        if self.is_uploaded():
            self.logger.error(f"Video still found on YouTube.  Something must have gone wrong with the API delete call.  Results of the call:\n{result}")
        else:
            self.logger.info("Delete successful")
        
        return result

    def update_web(self, force_update : bool = False):
        """Method to update Video details on YouTube based on the local object's properties.  This makes a videos.update call.  
        This method checks to see if an update is needed by making a videos.list call and comparing the local and web properties 
        before sending the update call.  This is because a videos.list API call is one quota unit where as the update is 50.  
        Set force_update to ignore this check."""
        
        #prepare snippet and status dicts to use in update call
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
        
        #if force_update is set do not bother making the videos.list call and comparing local and web
        if not force_update:
            current_web_status = self.__get_web_data()
        
            current_web_snippet = current_web_status['snippet']
            current_web_status = current_web_status['status']
        
            need_to_update=False
            
            if not (update_snippet == current_web_snippet and update_status == current_web_status):
                need_to_update = True
            
            if not need_to_update:
                self.logger.info("No need to update returning None")
                return None

        self.logger.info("Making videos.update call to YouTube API to update Video details")
        request = self.channel.service.videos().update(
            part='snippet,status',
            body=dict(
                snippet=update_snippet,
                status=update_status,
                id=self.id
            )
        )
        #return the results of the API call
        return request.execute()
    
    def update_local(self):
        """Method to update the local properties based on the web properties"""
        self.logger.info(f"Updating Video Object with id {self.id} from the web")
        
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
        self.downloaded = self.is_downloaded()
        
        self.logger.info("Update from web complete")
        
    def upload(self):
        """Method to upload Video to YouTube"""
        file = self.file
        privStatus = self.privacy_status
        self.privacy_status = 'private'
        
        #Attempt to upload to the web
        try:
            self.logger.info(f"Attempting to upload {file}")
            self.__initialize_upload()
        except Exception as e:
            self.logger.error(f"Error during upload:\n{e}")
            return
        
        #set pytube_obj and update local object from the web to grab any new details
        self.pytube_obj = self.__get_pytube()
        self.update_local()
        
        #If private is desired status leave things as is otherwise set the correct status and update
        if self.privacy_status == privStatus:
            self.logger.info("Video Upload Complete")
            return
        self.logger.info(f"Setting privacy status to {privStatus} and running an update")
        self.privacy_status = privStatus
        self.update_web()
        
        self.logger.info("Video Upload Complete")
    
    def download(self, overwrite=False):
        """Method to download the video from YouTube.  Set overwrite to True if you want an existing file overwritten"""
        self.__pytube_download(overwrite=overwrite)
        
    def is_uploaded(self):
        """
        Method to check if the Video is uploaded to Youtube.  This should only have a quota cost of 1.  
        Returns True if the video is found on YouTube.  Check is done with API so that private users videos 
        will be found and checked appropriately.
        """
        #Make video.list api call with id just requesting contentDetails to determine if the Object is uploaded
        request = self.channel.service.videos().list(
            part="contentDetails",
            id=self.id
        )
        result = request.execute()
        
        
        if result['pageInfo']['totalResults'] == 0:
            return False
        return True
        