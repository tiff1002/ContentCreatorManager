'''
Created on Feb 20, 2022

@author: tiff
'''
import logging.config
import os

class Settings(object):
    '''
    classdocs
    '''


    def __init__(self, folder_location : str):
        '''
        Constructor
        '''
        logging.config.fileConfig("logging.ini")
        self.logger = logging.getLogger('SettingsLogger')

        
        self.YouTube_logger = logging.getLogger('YouTubeLogger')
        self.LBRY_logger = logging.getLogger('LBRYLogger')
        self.Rumble_logger = logging.getLogger('RumbleLogger')
        self.Base_Method_logger = logging.getLogger('BaseMethodsLogger')
        self.logger.info("Loggers initialized")
        
        
        
        self.logger.info(f"setting folder_location:{folder_location}")
        self.logger.info("Changing to that folder")
        self.folder_location = folder_location
        self.original_dir = os.getcwd()
        os.chdir(self.folder_location)
        
        