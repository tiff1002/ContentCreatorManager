'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.platform.platform
import contentcreatormanager.media.post.twitter
import os
import json
import tweepy

class Twitter(contentcreatormanager.platform.platform.Platform):
    '''
    classdocs
    '''
    CLIENT_SECRETS_FILE = 'twitter_client_secret.json'

    def __init__(self, settings : contentcreatormanager.config.Settings):
        '''
        Constructor
        '''
        super(Twitter, self).__init__(settings=settings, ID='')
        self.logger = self.settings.Twitter_logger
        self.logger.info("Initializing Platform Object as Twitter Platform object")
        
        self.logger.info("Loading Twitter Creds")
        
        os.chdir(self.settings.original_dir)
        
        f = open(Twitter.CLIENT_SECRETS_FILE)
        data = json.load(f)
        f.close()
        
        os.chdir(self.settings.folder_location)
        
        self.CONSUMER_KEY = data['API_KEY']
        self.CONSUMER_SECRET = data['API_KEY_SECRET']
        self.ACCESS_TOKEN = data['ACCESS_TOKEN']
        self.ACCESS_TOKEN_SECRET = data['ACCESS_TOKEN_SECRET']
        
        self.auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        self.auth.set_access_token(self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)
        try:
            self.api.verify_credentials()
            self.logger.info("Authentication OK")
        except:
            self.logger.error("Error during authentication")
        
        self.timeline = self.api.home_timeline()
        
    def update_all_media_local(self):
        self.logger.info("Tweets are not loaded in from the web")
        
    def update_media_local(self, ID:str):
        self.logger.info("Tweets are not loaded in from the web")
        
    def update_all_media_web(self):
        self.logger.info("Tweets are not sent with this function use tweet")
        
    def update_media_web(self):
        self.logger.info("Tweets are not sent with this function use tweet")
        
    def tweet(self, post : str):
        tweet = contentcreatormanager.media.post.twitter.Tweet(settings=self.settings, twitter=self, post=post)
        tweet.upload()
        self.add_media(tweet)