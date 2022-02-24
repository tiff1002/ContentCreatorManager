'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.platform.platform
import contentcreatormanager.media.post.twitter
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
        #Calls constructor of super class to set the settings and blank ID as that property is not needed for Twitter Object
        super(Twitter, self).__init__(settings=settings, ID='')
        
        #Set the apropriate logger for the object
        self.logger = self.settings.Twitter_logger
        self.logger.info("Initializing Platform Object as Twitter Platform object")
        
        self.logger.info("Loading Twitter Creds")
        
        #Read in JSON auth info from file
        data = self.read_json(Twitter.CLIENT_SECRETS_FILE)
        
        #set some twitter specific properties for authentication
        self.CONSUMER_KEY = data['API_KEY']
        self.CONSUMER_SECRET = data['API_KEY_SECRET']
        self.ACCESS_TOKEN = data['ACCESS_TOKEN']
        self.ACCESS_TOKEN_SECRET = data['ACCESS_TOKEN_SECRET']
        
        #Set up and confirm Twitter Auth
        self.auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        self.auth.set_access_token(self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)
        try:
            self.api.verify_credentials()
            self.logger.info("Authentication OK")
        except:
            self.logger.error("Error during authentication")
            
        self.logger.info("Twitter Platform Object initialized")
    
    #Method to create and send a Tweet
    def tweet(self, post : str):
        #Create Tweet
        tweet = contentcreatormanager.media.post.twitter.Tweet(settings=self.settings, twitter=self, post=post)
        #Call upload() method which will call the Tweet's __post() method
        tweet.upload()
        #Add Tweet to self.media_objects that way if it failed to post and has a False posted flag a retry could be attempted
        self.add_media(tweet)
     
    #overriding of method to disable it for this type of object    
    def update_all_media_local(self):
        self.logger.info("Tweets are not loaded in from the web")
    
    #overriding of method to disable it for this type of object    
    def update_media_local(self, ID:str):
        self.logger.info("Tweets are not loaded in from the web")
        
    #overriding of method to disable it for this type of object
    def update_all_media_web(self):
        self.logger.info("Tweets are not sent with this function use tweet")
        
    #overriding of method to disable it for this type of object
    def update_media_web(self):
        self.logger.info("Tweets are not sent with this function use tweet")