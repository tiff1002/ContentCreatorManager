'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.media
import contentcreatormanager.media.video.video
import os
import json

class Platform(object):
    '''
    classdocs
    '''
    def __init__(self, settings : contentcreatormanager.config.Settings, ID : str):
        '''
        Constructor
        '''
        #Sets up some base properties that should be useful to most Platforms that will extend this class
        self.settings = settings
        self.logger = settings.Base_logger
        self.media_objects = []
        
        self.logger.info(f"Initializing Platform Object with id {ID}")
        self.id = ID
    
    #Method for reading in JSON files
    def read_json(self, file):
        #Change back to original_dir to grab credentials file
        os.chdir(self.settings.original_dir)
        
        #Open the file and read the JSON data in then close the file
        f = open(file)
        data = json.load(f)
        f.close()
        
        #Changes back to the folder_location dictated by settings object
        os.chdir(self.settings.folder_location)
        
        return data
    
    #Add a video to Media Objects
    def add_video(self, video : contentcreatormanager.media.video.video.Video):
        self.add_media(video)
    
    #Method to add a Media object to the self.media_objects list    
    def add_media(self, media : contentcreatormanager.media.media.Media):
        self.media_objects.append(media)
        
    #Method to call upload() on all Media objects in self.media_objects
    def upload_all_media(self):
        for media in self.media_objects:
            media.upload()
        
    #Method to call upload() on the media object with ID provided       
    def upload_media(self, ID : str):
        for media in self.media_objects:
            if media.id == ID:
                media.upload()
    
    #Method to call update_local() on all Media objects in self.media_objects            
    def update_all_media_local(self):
        for media in self.media_objects:
            media.update_local()
            
    #Method to call update_web() on all Media objects in self.media_objects
    def update_all_media_web(self):
        for media in self.media_objects:
            media.update_web()
    
    #Method to call update_local() on the media object with ID provided        
    def update_media_local(self, ID : str):
        for media in self.media_objects:
            if media.id == ID:
                media.update_local()
                
    #Method to call update_web() on the media object with ID provided       
    def update_media_web(self, ID : str):
        for media in self.media_objects:
            if media.id == ID:
                media.update_web()
                
    #Method to call download() on the media object with ID provided       
    def download_media(self, ID : str):
        for media in self.media_objects:
            if media.id == ID:
                media.download()
                
    #Method to call download() on all Media objects in self.media_objects
    def download_all_media(self):
        for media in self.media_objects:
            media.download()
            
    #Method to remove specific Media from the web
    def delete_media_from_web(self, ID):
        for media in self.media_objects:
            if media.id == ID:
                media.delete_web()
            
            