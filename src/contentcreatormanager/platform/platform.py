'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.media

class Platform(object):
    '''
    classdocs
    '''


    def __init__(self, settings : contentcreatormanager.config.Settings, ID : str):
        '''
        Constructor
        '''
        self.settings = settings
        self.logger = settings.Base_logger
        self.media_objects = []
        
        self.logger.info(f"Initializing Platform Object with id {ID}")
        self.id = ID
        
    def add_media(self, media : contentcreatormanager.media.media.Media):
        self.media_objects.append(media)
        
    def upload_all_media(self):
        for media in self.media_objects:
            media.upload()
        
    def upload_media(self, ID : str):
        for media in self.media_objects:
            if media.id == ID:
                media.upload()
                
    def update_all_media_local(self):
        for media in self.media_objects:
            media.update_local()
            
    def update_all_media_web(self):
        for media in self.media_objects:
            media.update_web()
            
    def update_media_local(self, ID : str):
        for media in self.media_objects:
            if media.id == ID:
                media.update_local()
                
    def update_media_web(self, ID : str):
        for media in self.media_objects:
            if media.id == ID:
                media.update_web()
                
    def download_media(self, ID : str):
        for media in self.media_objects:
            if media.id == ID:
                media.download()
                
    def download_all_media(self):
        for media in self.media_objects:
            media.download()
            
            