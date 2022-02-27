'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.media
import os.path
import shortuuid

class Video(contentcreatormanager.media.media.Media):
    '''
    classdocs
    '''


    def __init__(self, settings, ID : str = '', file_name : str = '', title : str = "", description : str = "", thumbnail_file_name : str = ''):
        '''
        Constructor
        '''
        if ID == '' and file_name == '':
            settings.Video_logger.error("You must set either the file_name or ID to create a Video Object")
            raise Exception()
        
        super(Video, self).__init__(settings=settings, ID=ID)
        
        self.logger = self.settings.Video_logger
        self.logger.info("Initializing Media Object as a Video object")
        
        
        self.file = os.path.join(os.getcwd(), file_name)
        self.thumbnail = os.path.join(os.getcwd(), thumbnail_file_name)
        
        file_does_not_exist = not os.path.isfile(self.file)
        
        if file_does_not_exist and ID == '':
            self.logger.error(f"no file found for file_name {file_name} and no ID set")
        
        self.title = title
        self.description = description
        
    def set_unique_id(self, ID=None):
        if ID is None:
            self.id = shortuuid.uuid()
            self.logger.info(f"Object is set to random unique ID ({self.id})")
        else:
            self.logger.info(f"ID provided setting object id to {ID}")
            self.id = ID
        
    
    
        
        
        