'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.post.post

class Tweet(contentcreatormanager.media.post.post.Post):
    '''
    classdocs
    '''
    #Private method to send self.body as a Tweet out to twitter from the account that was authed during the Twitter Platform object creation
    def __post(self):
        self.logger.info(f"Sending out tweet: {self.body}")
        
        #Makes API call with Tweepy object from the Twitter object stored in self.twitter and store the results
        try:
            self.twitter.api.update_status(self.body)
            self.posted = True
        except Exception as e:
            self.logger.error(f"Failed to send Tweet got error:\n{e}")
            self.posted = False
    
    def __init__(self, settings : contentcreatormanager.config.Settings, twitter, post : str):
        '''
        Constructor
        '''
        #Super Class constructor called to set settings and body while blanking out title as Tweets have not title
        super(Tweet, self).__init__(settings=settings,body=post,title='')
        
        #Set appropriate logger
        self.logger = self.settings.Twitter_logger
        
        self.logger.info("Initializing Post object as a Tweet")
        
        #Setting self.twitter to the provided Twiter object
        self.twitter = twitter
        
        self.logger.info("Tweet Object initialized")
        
    #Overriding the upload method so that this Tweet.__post() is run and not Post.__post()
    def upload(self):
        self.__post()