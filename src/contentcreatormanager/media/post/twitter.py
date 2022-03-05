"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.media.post.post as media_post

class Tweet(media_post.Post):
    """
    classdocs
    """
    def __post(self):
        """
        Private Method to send out the Tweet Object's body property
        """
        
            
    def __init__(self, twitter, post : str, sensitive : bool = False):
        """
        Constructor takes a Twitter Platform object and a string to be the body of the Tweet
        """
        super(Tweet, self).__init__(platform=twitter,body=post,title='')
        
        self.logger = self.settings.Twitter_logger
        
        self.sensitive = sensitive
        
        self.logger.info("Initializing Post object as a Tweet")
        
        self.logger.info("Tweet Object initialized")
        
    def is_uploaded(self): # this needs proper implementation
        """
        
        """
        self.uploaded = True
        return True
        
    def upload(self):
        """
        Public Method to send out the Tweet Object's body as a Tweet
        """
        self.logger.info(f"Sending out tweet: {self.body}")
        
        result = self.platform.api_update_status(status_text=self.body, possibly_sensitive=self.sensitive)
        
        self.logger.info(f"Setting Tweet ID to {result._json['id']}")
        self.id = result._json['id']
        
        return result