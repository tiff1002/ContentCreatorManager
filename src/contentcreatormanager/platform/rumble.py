'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.platform.platform
import os
import json

class Rumble(contentcreatormanager.platform.platform.Platform):
    '''
    classdocs
    '''
    CLIENT_SECRETS_FILE = 'rumble_client_secret.json'

    def __init__(self, settings : contentcreatormanager.config.Settings, init_videos : bool = False):
        '''
        Constructor
        '''
        super(Rumble, self).__init__(settings=settings, ID='')
        self.logger = self.settings.Rumble_logger
        
        self.logger.info("Initializing Platform Object as a Rumble Platform Object")
        
        #change to the directory with the cred files
        os.chdir(self.settings.original_dir)

        #opent the rumble cred file and read with json
        with open(Rumble.CLIENT_SECRETS_FILE) as f:
            creds = json.load(f)
            
        #close file and move back to proper directory
        f.close()
        os.chdir(self.settings.folder_location)
        
        #set the access token and id from the creds file
        self.access_token = creds['ACCESS_TOKEN']
        self.id = creds['CHANNEL_ID']
        
        if init_videos:
            #init vids
            self.logger.info("Grabbing video data from Rumble")
        
        self.logger.info("Rumble Platform Object initialized")