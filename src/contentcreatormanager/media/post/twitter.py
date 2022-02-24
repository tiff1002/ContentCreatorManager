'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.post.post
import contentcreatormanager.platform.twitter

class Tweet(contentcreatormanager.media.post.post.Post):
    '''
    classdocs
    '''
    def __post(self):
        self.logger.info(f"Sending out tweet: {self.body}")
        result = self.twitter.api.update_status(self.body)
        
        if True: #needs to be changed to check for successful posting of tweet
            self.posted = True

    def __init__(self, settings : contentcreatormanager.config.Settings, twitter, post : str):
        '''
        Constructor
        '''
        super(Tweet, self).__init__(settings=settings,body=post,title='')
        self.logger = self.settings.Twitter_logger
        
        self.logger.info("Initializing Post object as a Tweet")
        self.twitter = twitter
        
    def upload(self):
        self.__post()