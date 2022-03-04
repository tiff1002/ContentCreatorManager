'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.post.post

class Tweet(contentcreatormanager.media.post.post.Post):
    '''
    classdocs
    '''
    def __post(self):
        """Private Method to send out the Tweet Object's body property"""
        self.logger.info(f"Sending out tweet: {self.body}")
        
        #Makes API call with Tweepy object from the Twitter object stored in self.twitter and store the results
        result = self.platform.api_update_status(status_text=self.body, possibly_sensitive=self.sensitive)
        
        self.logger.info(f"Setting Tweet ID to {result._json['id']}")
        self.id = result._json['id']
            
    
    def __init__(self, twitter, post : str, sensitive : bool = False):
        '''
        Constructor takes a Twitter Platform object and a string to be the body of the Tweet
        '''
        #Super Class constructor called to set settings and body while blanking out title as Tweets have not title
        super(Tweet, self).__init__(platform=twitter,body=post,title='')
        
        #Set appropriate logger
        self.logger = self.settings.Twitter_logger
        
        self.sensitive = sensitive
        
        self.logger.info("Initializing Post object as a Tweet")
        
        self.logger.info("Tweet Object initialized")
        
    def upload(self):
        """Public Method to send out the Tweet Object's body as a tweet"""
        return self.__post()