'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.post.post

class LBRYTextPost(contentcreatormanager.media.post.post.Post):
    '''
    classdocs
    '''


    def __init__(self, lbry_channel, title : str, body : str):
        '''
        Constructor takes LBRY Platform object, title and body for the LBRY Post
        '''
        super(LBRYTextPost, self).__init__(platform=lbry_channel, body=body, title=title)
        self.logger = self.settings.LBRY_logger
        
        self.logger.info("Initializing Post Object as LBRY Post Object")
        
        self.channel = lbry_channel
        
        self.logger.info("LBRY Post Object Initialized")