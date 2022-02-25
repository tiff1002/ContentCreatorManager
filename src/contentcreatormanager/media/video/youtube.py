'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.video
import pytube
import os.path

class YouTubeVideo(contentcreatormanager.media.video.video.Video):
    '''
    classdocs
    '''
    
    BASE_URL = "https://www.youtube.com/watch?v="
    
    MAX_RETRIES = 25
  
    def __is_downloaded(self):
        return os.path.isfile(self.file)
    
    def __file_name(self):
        valid_chars = '`~!@#$%^&+=,-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        getVals = list([val for val in f"{self.title}.mp4" if val in valid_chars])
        return "".join(getVals)
    
    def __get_pytube(self, use_oauth=True):
        url = f"{YouTubeVideo.BASE_URL}{self.id}"
        return pytube.YouTube(url, use_oauth=use_oauth)
    
    def __init__(self, channel, ID : str = None, favorite_count : str ='0', comment_count : str ='0', dislike_count : str ='0', like_count : str ='0',
                 view_count : str ='0', self_declared_made_for_kids : bool =False, made_for_kids : bool =False, public_stats_viewable : bool =True,
                 embeddable : bool =True, lic : str ='youtube', privacy_status : str ="public", upload_status : str ='notUploaded',
                 has_custom_thumbnail : bool =False, content_rating : dict ={}, licensed_content : bool =False, 
                 default_audio_language : str ='en-US', published_at=None, channel_id=None, title=None, description=None, 
                 thumbnails : dict ={}, channel_title=None, tags : list =[], category_id : int =22, live_broadcast_content=None, new_video : bool =False):
        '''
        Constructor
        '''
        self.title = title
        super(YouTubeVideo, self).__init__(settings=channel.settings,ID=ID,file_name=self.__file_name())
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
        self.downloaded = self.__is_downloaded()
        if new_video:
            self.pytube_obj = None
        else:
            self.pytube_obj = self.__get_pytube()
            
        self.logger.info("YouTube Video Object initialized")