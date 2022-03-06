"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.media.post.post as media_post

class FacebookPost(media_post.Post):
    """
    classdocs
    """

    def __init__(self, facebook, post : str):
        """
        Constructor takes a Facebook Platform object as well
        as the body of the post as a string
        """
        super(FacebookPost, self).__init__(platform=facebook,title='',
                                           body=post)
        
        
        self.logger = self.settings.Facebook_logger
        self.logger.info("Initializing Post object as a Facebook Post")
        
        self.logger.info("Facebook Post Object initialized")
        
    def is_uploaded(self):
        """
        
        """
        self.uploaded = True
        return True
    
    def upload(self):
        """
        Method to send this post to the facebook page tied to the 
        Facebook Platform Object tied to this object
        """
        result = self.platform.api_post_feed(ID=self.platform.id,
                                             message=self.body,
                                             page_access_token=self.platform.page_access_token)
        
        return result