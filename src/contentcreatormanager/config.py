"""
Created on Feb 24, 2022

@author: tiff
"""
import logging.config
import os

class Settings(object):
    """
    classdocs
    """
    def __init__(self, folder_location : str, logging_config_file : str):
        """
        Constructor
        """
        logging.config.fileConfig(logging_config_file)
        self.logger = logging.getLogger('SettingsLogger')

        
        self.YouTube_logger = logging.getLogger('YouTubeLogger')
        self.LBRY_logger = logging.getLogger('LBRYLogger')
        self.Rumble_logger = logging.getLogger('RumbleLogger')
        self.Base_logger = logging.getLogger('BaseLogger')
        self.Twitter_logger = logging.getLogger('TwitterLogger')
        self.Reddit_logger = logging.getLogger('RedditLogger')
        self.Facebook_logger = logging.getLogger('FacebookLogger')
        self.Minds_logger = logging.getLogger('MindsLogger')
        self.Instagram_logger = logging.getLogger('InstagramLogger')
        self.Media_logger = logging.getLogger('MediaLogger')
        self.Platform_logger = logging.getLogger('PlatformLogger')
        self.Video_logger = logging.getLogger('VideoLogger')
        self.Post_logger = logging.getLogger('PostLogger')
        self.logger.info("Loggers initialized")
        
        self.logger.info(f"setting folder_location:{folder_location}")
        self.logger.info("Changing to that folder")
        self.folder_location = folder_location
        self.original_dir = os.getcwd()
        os.chdir(self.folder_location)