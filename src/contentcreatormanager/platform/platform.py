'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.media
import contentcreatormanager.media.video.video
import contentcreatormanager.config
import os
import json

class Platform(object):
    '''
    classdocs
    '''
    def __init__(self, settings : contentcreatormanager.config.Settings, ID : str):
        '''
        Constructor takes a Settings object and an ID as string
        '''
        #Sets up some base properties that should be useful to most Platforms that will extend this class
        self.settings = settings
        self.logger = settings.Base_logger
        self.media_objects = []
        
        self.logger.info(f"Initializing Platform Object with id {ID}")
        self.id = ID
    
    def get_media(self, ID : str):
        """Returns the Media Object with the given ID"""
        for media in self.media_objects:
            if media.id == ID:
                return media
    
    def read_json(self, file):
        """Method for reading in JSON files and returning a dict with the json data in it"""
        #Change back to original_dir to grab credentials file
        os.chdir(self.settings.original_dir)
        
        #Open the file and read the JSON data in then close the file
        f = open(file)
        data = json.load(f)
        f.close()
        
        #Changes back to the folder_location dictated by settings object
        os.chdir(self.settings.folder_location)
        
        return data
    
    def add_video(self, video : contentcreatormanager.media.video.video.Video):
        """Method to add a video to Media Objects"""
        self.add_media(video)
       
    def add_media(self, media : contentcreatormanager.media.media.Media):
        """Method to add a Media object to the media_objects list property"""
        self.media_objects.append(media)
        
        
        
    def upload_all_media(self):
        """Method to call upload() on all Media objects in self.media_objects"""
        self.logger.info("Running upload Method for all media objects")
        for media in self.media_objects:
            media.upload()
               
    def upload_media(self, ID : str):
        """Method to call upload() on the media object in media_objects with ID provided"""
        for media in self.media_objects:
            if media.id == ID:
                self.logger.info(f"Running upload Method for {media.id}")
                media.upload()
                
    def update_all_media_local(self):
        """Method to call update_local() on all Media objects in the media_objects list property"""
        self.logger.info("Running update local Method for all media objects")
        for media in self.media_objects:
            media.update_local()
            
    def update_all_media_web(self):
        """Method to call update_web() on all Media objects in self.media_objects"""
        self.logger.info("Running update web Method for all media objects")
        for media in self.media_objects:
            media.update_web()
            
    def update_media_local(self, ID : str):
        """Method to call update_local() on the media object in media_objects with ID provided"""
        for media in self.media_objects:
            if media.id == ID:
                self.logger.info(f"Running Update local Method for {media.id}")
                media.update_local()
                       
    def update_media_web(self, ID : str):
        """Method to call update_web() on the media object in media_objects with ID provided"""
        for media in self.media_objects:
            if media.id == ID:
                self.logger.info(f"Running Upadte Web Method for {media.id}")
                media.update_web()
                       
    def download_media(self, ID : str):
        """Method to call download() on the media object in media_objects with ID provided"""
        for media in self.media_objects:
            if media.id == ID:
                self.logger.info(f"Running Download Method for {media.id}")
                media.download()
                
    def download_all_media(self):
        """Method to call download() on all Media objects in media_objects list property"""
        self.logger.info("Running Download Method for all media_objects")
        for media in self.media_objects:
            media.download()
            
    def delete_media_from_web(self, ID):
        """Method to call delete_web() on a Media Object in media_objects with the given ID"""
        for media in self.media_objects:
            if media.id == ID:
                self.logger.info(f"Running Delete Method for {media.id}")
                media.delete_web()
                
            
            