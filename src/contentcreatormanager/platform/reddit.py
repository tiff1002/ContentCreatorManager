'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.platform.platform

class Reddit(contentcreatormanager.platform.platform.Platform):
    '''
    classdocs
    '''


    def __init__(self, settings : contentcreatormanager.config.Settings):
        '''
        Constructor takes a Settings object.  No ID for Reddit Platform object.
        '''
        #Calls constructor of super class to set the settings and blank ID as that property is not needed for Twitter Object
        super(Reddit, self).__init__(settings=settings, ID='')
        
        #Set the apropriate logger for the object
        self.logger = self.settings.Facebook_logger
        self.logger.info("Initializing Platform Object as Reddit Platform object")
        
        #load in creds
        
        
        self.logger.info("Reddit Platform Object initialized")