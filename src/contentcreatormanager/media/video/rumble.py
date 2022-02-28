'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.video.video
import os.path
import requests

class RumbleVideo(contentcreatormanager.media.video.video.Video):
    '''
    classdocs
    '''
    UPLOAD_API_URL = "https://rumble.com/api/simple-upload.php"
    
    NOT_FOR_SALE = 0 # This is like an unlisted video on youtube as I understand it
    
    RUMBLE_LICENSE = 6 # I Think this is what a standard Rumble upload is

    def __upload_without_thumbnail(self):   
        """Private Method to upload Video to Rumble without a thumbnail file"""
        files = {
            'access_token': (None, self.platform.access_token),
            'title': (None, self.title),
            'description': (None, self.description),
            'license_type': (None, self.license_type),
            'channel_id': (None, self.platform.id),
            'video': (os.path.basename(self.file), open(self.file, 'rb'))
        }
        
        response = requests.post(RumbleVideo.UPLOAD_API_URL, files=files)
        
        self.logger.info(f"Made Request to Rumble API to upload video got response:\n{response}")
        
        return response
    
    def __upload_with_thumbnail(self):
        """Private Method to upload Video to Rumble with a thumbnail file"""
        files = {
            'access_token': (None, self.platform.access_token),
            'title': (None, self.title),
            'description': (None, self.description),
            'license_type': (None, self.license_type),
            'channel_id': (None, self.platform.id),
            'thumb':(os.path.basename(self.thumbnail), open(self.thumbnail, 'rb')),
            'video': (os.path.basename(self.file), open(self.file, 'rb'))
        }
        
        response = requests.post(RumbleVideo.UPLOAD_API_URL, files=files)
        
        self.logger.info(f"Made Request to Rumble API to upload video got response:\n{response}")
        
        return response
    
    #Constructor
    def __init__(self, rumble_channel, guid : str = '', title : str = '', description : str = '', thumbnail_file_name : str = '',
                 video_file_name : str = '', license_type : int = RUMBLE_LICENSE):
        '''
        Constructor take a Rumble Platform Object as a required parameter.  guid will be the ID of the video and is set by the user.  
        If it is not set a unique random one will be generated.  file_name and thumbnail_file_name can be provided with or without the mp4 or jpg file extension.
        '''
        super(RumbleVideo, self).__init__(platform=rumble_channel, ID='', title=title, description=description,file_name=video_file_name, thumbnail_file_name=thumbnail_file_name)
        self.logger = self.settings.Rumble_logger
        self.logger.info("Initializing Video Object as Rumble Video Object")
        
        #if a guid is not set then generate one otherwise set id to guid
        if guid == '':
            self.set_unique_id()
        else:
            self.set_unique_id(guid)
            
        self.license_type = license_type
        
        self.logger.info(f"Rumble Video Object initialized with ID {self.id}")

    def upload(self):
        """Method to upload a video to Rumble"""
        #Check for the video file
        if not self.is_downloaded():
            self.logger.error("Can not find video file no upload will be made")
            return 
        #Check for thumbnail file to determine if upload should be done with or without one
        if not self.is_thumb_downloaded():
            self.logger.warning("No Thumbnail Found uploading without one")
            self.__upload_without_thumbnail()
        else:
            self.logger.info("Starting upload")
            self.__upload_with_thumbnail()
            
    def delete_web(self):
        """Method to delete video from Rumble"""
        self.logger.warning("No Method to delete video from rumble yet")
        return
    
    def download(self):
        """Method to download video from Rumble"""
        self.logger.warning("No Method to download video from rumble yet")
        return
    
    def update_web(self):
        """Method to update video details on Rumble from the local object properties"""
        self.logger.warning("No Method to update data to rumble yet")
        return
    
    def update_local(self):
        """Method to update local object properties from Rumble"""
        self.logger.warning("No Method to get data from rumble yet")
        return