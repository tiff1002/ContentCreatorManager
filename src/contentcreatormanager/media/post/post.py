'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.media
from numpy.core.defchararray import title


class Post(contentcreatormanager.media.media.Media):
    '''
    classdocs
    '''
    def __post(self):
        self.logger.error("__post() in Post run this should not happen")

    def __init__(self, settings : contentcreatormanager.config.Settings, body : str, title : str):
        '''
        Constructor
        '''
        super(Post, self).__init__(settings=settings, ID='')
        self.logger = self.settings.Post_logger
        
        self.logger.info("Initializing Media object as a Post")
        
        self.title = title
        self.body = body
        self.posted = False
        
    def upload(self):
        self.__post()