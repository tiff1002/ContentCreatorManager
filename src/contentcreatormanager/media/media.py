'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.config

class Media(object):
    '''
    classdocs
    '''


    def __init__(self, settings : contentcreatormanager.config.Settings, ID : str):
        '''
        Constructor
        '''
        self.settings = settings
        self.logger = settings.Media_logger
        
        self.logger.info(f"Initializing Media Object with id {ID}")
        self.id = ID
        
    def upload(self):
        return
    
    def update_web(self):
        return 
    
    def update_local(self):
        return 
    
    def delete_web(self):
        return
    
    def download(self):
        return