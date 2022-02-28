'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.post.post

class MindsPost(contentcreatormanager.media.post.post.Post):
    '''
    classdocs
    '''


    def __init__(self, minds, post : str):
        '''
        Constructor takes a Minds Platform Object and post body as a string
        '''
        super(MindsPost, self).__init__(platform=minds, body=post, title='')
        self.logger = self.settings.Minds_logger
        
        self.logger.info("Initializing Post Object as a Minds Post")
        
        self.logger.info("Minds Post Object Initialized")