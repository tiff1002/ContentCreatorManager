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

    #Private Method to upload a video without a thumbnail
    def __upload_without_thumbnail(self):   
        files = {
            'access_token': (None, self.channel.access_token),
            'title': (None, self.title),
            'description': (None, self.description),
            'license_type': (None, self.license_type),
            'channel_id': (None, self.channel.id),
            'video': (os.path.basename(self.file), open(self.file, 'rb'))
        }
        
        response = requests.post(RumbleVideo.UPLOAD_API_URL, files=files)
        
        self.logger.info(f"Made Request to Rumble API to upload video got response:\n{response}")
        
        return response
    
    #Private Method to upload a video with a thumbnail
    def __upload_with_thumbnail(self):
        files = {
            'access_token': (None, self.channel.access_token),
            'title': (None, self.title),
            'description': (None, self.description),
            'license_type': (None, self.license_type),
            'channel_id': (None, self.channel.id),
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
        Constructor
        '''
        super(RumbleVideo, self).__init__(settings=rumble_channel.settings, ID=guid, title=title, description=description,file_name=video_file_name, thumbnail_file_name=thumbnail_file_name)
        self.logger = self.settings.Rumble_logger
        self.logger.info("Initializing Video Object as Rumble Video Object")
        
        self.channel = rumble_channel
        
        #if a guid is not set then generate one otherwise set id to guid
        if guid == '':
            self.set_unique_id()
        else:
            self.set_unique_id(guid)

        self.license_type = license_type

    #Method to upload video
    def upload(self):
        if not os.path.isfile(self.file):
            self.logger.error("Can not find video file no upload will be made")
            return 
        if not os.path.isfile(self.thumbnail):
            self.logger.warning("No Thumbnail Found uploading without one")
            self.__upload_without_thumbnail()
        else:
            self.logger.info("Starting upload")
            self.__upload_with_thumbnail()