'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.media
import contentcreatormanager.platform.platform

class Post(contentcreatormanager.media.media.Media):
    '''
    classdocs
    '''
    def __init__(self, platform : contentcreatormanager.platform.platform.Platform, body : str, title : str):
        '''
        Constructor for generic post to set the settings, body of the post and title.  It will also initialize posted to False
        '''
        #Super Class constructor run to set settings and blank out ID as posts will typically not need to store an ID
        super(Post, self).__init__(platform=platform, ID='')
        
        #Set appropriate logger
        self.logger = self.settings.Post_logger
        
        self.logger.info("Initializing Media object as a Post")
        
        #Se the properties for Posts (title, body, posted)
        self.title = title
        self.body = body
        self.posted = False #initially false as the Post has not been Posted yet :P