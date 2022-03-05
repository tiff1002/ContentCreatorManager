"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.media.video.video

class RumbleVideo(contentcreatormanager.media.video.video.Video):
    """
    classdocs
    """
    NOT_FOR_SALE = 0 # This is like an unlisted video on YouTube as I understand it
    
    RUMBLE_LICENSE = 6 # I Think this is what a standard Rumble upload is similar to a standard YouTube upload on YouTube (youtube license)
    
    def __init__(self, rumble_channel, guid : str = '', title : str = '', description : str = '', thumbnail_file_name : str = '',
                 video_file_name : str = '', license_type : int = RUMBLE_LICENSE, uploaded : bool = False):
        """
        Constructor take a Rumble Platform Object as a required parameter.  guid will be the ID of the video and is set by the user.  
        If it is not set a unique random one will be generated.  file_name and thumbnail_file_name can be provided with or without the mp4 or jpg file extension.
        """
        super(RumbleVideo, self).__init__(platform=rumble_channel, ID='', title=title, description=description,file_name=video_file_name, thumbnail_file_name=thumbnail_file_name)
        self.logger = self.settings.Rumble_logger
        self.logger.info("Initializing Video Object as Rumble Video Object")
        
        if guid == '':
            self.set_unique_id()
        else:
            self.set_unique_id(guid)
            
        #The method sets id to a unique random so setting guid with it (rumble id will be set on upload)
        self.guid = self.id
        self.url = ''
            
        self.license_type = license_type
        self.uploaded = uploaded
        
        self.logger.info(f"Rumble Video Object initialized with ID {self.id}")

    def upload(self):
        """
        Method to upload a video to Rumble
        """
        if not self.is_downloaded():
            self.logger.error("Can not find video file not uploading")
            return
        
        result = self.platform.api_upload(access_token=self.platform.access_token, title=self.title, description=self.description, license_type=self.license_type, channel_id=self.platform.id, guid=self.guid, video_file=self.file, thumbnail_file=self.thumbnail)

        if 'success' in result.json():
            if result.json()['success']:
                url = result.json()['url_monetized']
                self.logger.info(f"Video Uploaded to: {url}")
                self.uploaded = True
                self.id = result.json()['video_id']
                self.url = url
                return result
            
        self.logger.info(f"Upload failed response: {result.json()}")
        self.uploaded = False

        return result
            
    def delete_web(self):
        """
        Method to delete video from Rumble
        """
        self.logger.warning("No Method to delete video from rumble yet")
        return
    
    def download(self):
        """
        Method to download video from Rumble
        """
        self.logger.warning("No Method to download video from rumble yet")
        return
    
    def update_web(self):
        """
        Method to update video details on Rumble from the local object properties
        """
        self.logger.warning("No Method to update data to rumble yet")
        return
    
    def update_local(self):
        """
        Method to update local object properties from Rumble
        """
        self.logger.warning("No Method to get data from rumble yet")
        return