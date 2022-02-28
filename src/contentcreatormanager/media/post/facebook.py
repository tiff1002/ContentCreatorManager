'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.post.post

class FacebookPost(contentcreatormanager.media.post.post.Post):
    '''
    classdocs
    '''


    def __init__(self, facebook, post : str):
        '''
        Constructor takes a Facebook Platform object as well as the body of the post as a string
        '''
        #Call super class constructor
        super(FacebookPost, self).__init__(platform=facebook,title='',body=post)
        
        
        self.logger = self.settings.Facebook_logger
        self.logger.info("Initializing Post object as a Facebook Post")
        
        self.logger.info("Facebook Post Object initialized")