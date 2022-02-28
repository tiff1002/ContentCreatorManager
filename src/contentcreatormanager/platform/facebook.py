'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.platform.platform
import contentcreatormanager.media.post.facebook

class Facebook(contentcreatormanager.platform.platform.Platform):
    '''
    classdocs
    '''
    CLIENT_SECRETS_FILE = 'facebook_client_secret.json'

    def __init__(self, settings : contentcreatormanager.config.Settings):
        '''
        Constructor takes a Settings object.  Facebook page to post to is determined by creds file
        '''
        #load in creds
        self.settings = settings
        data = self.read_json(Facebook.CLIENT_SECRETS_FILE)
        #Calls constructor of super class to set the settings object as well as the ID for the facebook page this object will post to (found in the credentials file)
        super(Facebook, self).__init__(settings=settings, ID=data['PAGE_ID'])
        
        #Set the apropriate logger for the object
        self.logger = self.settings.Facebook_logger
        self.logger.info("Initializing Platform Object as Facebook Platform object")
        
        #sets access token from cred file
        self.access_token = data['ACCESS_TOKEN']
        self.page_access_token = None
        self.graph = None
        self.resp = None
        
        self.logger.info("Facebook Platform Object initialized")
        
    def post(self, msg):
        post = contentcreatormanager.media.post.facebook.FacebookPost(self, msg)
        result = None
        try:
            result = post.upload()
        except Exception as e:
            self.logger.error(f"Failed to send post to Facebook got error:\n{e}")
            self.logger.info("Leaving posted set to False and adding to media_objects")
            self.add_media(post)
            return
        
        '''
        if result has error:
            self.logger.error(f"Failed to send post to Facebook got error:\n{e}")
            self.logger.info("Leaving posted set to False and adding to media_objects")
            self.add_media(post)
            return
        '''
        post.posted = True
        self.add_media(post)
        
        self.logger.info(f"Post sent to Facebook:\n{post.body}")
        
        