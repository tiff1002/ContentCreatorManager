'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.platform.platform
import contentcreatormanager.media.post.reddit
import praw

class Reddit(contentcreatormanager.platform.platform.Platform):
    '''
    classdocs
    '''
    CLIENT_SECRETS_FILE = 'reddit_client_secret.json'

    def __init__(self, settings : contentcreatormanager.config.Settings):
        '''
        Constructor takes a Settings object.  No ID for Reddit Platform object.
        '''
        #Calls constructor of super class to set the settings and blank ID as that property is not needed for Twitter Object
        super(Reddit, self).__init__(settings=settings, ID='')
        
        #Set the right logger for the object
        self.logger = self.settings.Reddit_logger
        self.logger.info("Initializing Platform Object as Reddit Platform object")
        
        #load in creds
        data = self.read_json(Reddit.CLIENT_SECRETS_FILE)
        
        self.client_id = data['client_id']
        self.client_secret = data['client_secret']
        self.user_agent = data['user_agent']
        self.redirect_uri = data['redirect_uri']
        self.refresh_token = data['refresh_token']
        
        #set up praw
        self.praw = praw.Reddit(client_id=data['client_id'],client_secret=data['client_secret'],
                                user_agent=data['user_agent'],redirect_uri=data['redirect_uri'],
                                refresh_token=data['refresh_token'])
        
        self.logger.info("Reddit Platform Object initialized")
        
    def post(self, subr : str, title : str, body : str):
        """Method to create and send a Reddit post to a subreddit and add it to media_objects"""
        post = contentcreatormanager.media.post.reddit.RedditPost(reddit=self, title=title, body=body, subr=subr)
        
        result = post.upload()
        
        if result is None or result == '' or result == [] or result == {}:
            self.logger.error("Failed to upload post to reddit not setting posted but still adding to media_objects")
        else:      
            post.posted = True
        self.add_media(post)