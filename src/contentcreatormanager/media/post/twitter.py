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
        try:
            self.platform.api.update_status(self.body)
            self.posted = True
        except Exception as e:
            self.logger.error(f"Failed to send Tweet got error:\n{e}")
            self.posted = False
    
    def __init__(self, twitter, post : str):
        '''
        Constructor takes a Twitter Platform object and a string to be the body of the Tweet
        '''
        #Super Class constructor called to set settings and body while blanking out title as Tweets have not title
        super(Tweet, self).__init__(platform=twitter,body=post,title='')
        
        #Set appropriate logger
        self.logger = self.settings.Twitter_logger
        
        self.logger.info("Initializing Post object as a Tweet")
        
        self.logger.info("Tweet Object initialized")
        
    def upload(self):
        """Public Method to send out the Tweet Object's body as a tweet"""
        self.__post()