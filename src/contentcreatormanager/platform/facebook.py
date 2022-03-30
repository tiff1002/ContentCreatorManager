"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.config as ccm_config
import contentcreatormanager.platform.platform as plat
import contentcreatormanager.media.post.facebook as fb_post
import facebook

class Facebook(plat.Platform):
    """
    classdocs
    """
    CLIENT_SECRETS_FILE = 'facebook_client_secret.json'               

    def __init__(self, settings : ccm_config.Settings):
        """
        Constructor takes a Settings object. 
        Facebook page to post to is determined by creds file
        """
        self.settings = settings
        data = self.read_json(Facebook.CLIENT_SECRETS_FILE)
        
        super(Facebook, self).__init__(settings=settings, ID=data['PAGE_ID'])
        
        self.logger = self.settings.Facebook_logger
        m="Initializing Platform Object as Facebook Platform object"
        self.logger.info(m)
        
        self.access_token = data['ACCESS_TOKEN']
        self.page_access_token = None
        self.graph = None
        
        self.__init_page_access_token()
        
        self.logger.info("Facebook Platform Object initialized")
        
    def __init_page_access_token(self):
        self.graph = facebook.GraphAPI(self.access_token)
        resp = self.graph.get_object('me/accounts')

        for page in resp['data']:
            if page['id'] == self.id:
                self.page_access_token = page['access_token']
                
    def re_init_token(self):
        """
        Method to re run the Method that inititalized the page_access_token
        on creation of the FB Platform
        """
        self.__init_page_access_token()
    
    def post(self, msg):
        """
        Method to create and send a Facebook post.
        """
        post = fb_post.FacebookPost(self, msg)
        
        try:
            result = post.upload()
        except facebook.GraphAPIError as e:
            if e.message == 'Duplicate status message':
                m="Posting Failed.  You are trying to make a duplicate post"
                self.logger.error(m)
                post.uploaded = False
                return post
            else:
                raise e
        
        #this should be changed to use a is_uploaded
        # method from the facebook post class
        m=f"Setting FB Post ID to {result['id']}, setting posted flag to true"
        self.logger.info(m)
        post.id = result['id']
        post.uploaded = True
        
        self.add_media(post)
        
        return post
        
    def api_post_feed(self, ID : str, message : str, page_access_token : str):
        """
        Method to Make Facebook API call to post to a page
        Example Call: api_post_feed(ID='101817019117465',
                                    message="Got a Test Post",
                                    page_access_token={page_access_token})
        Example Return: {'id': '101817019117465_108376858461481'}
        Duplicate Post Exception: facebook.GraphAPIError: Duplicate status message
        """
        self.logger.info(f"Making API Call to Facebook to post to page with id {ID}")
        
        graph = facebook.GraphAPI(page_access_token)
        
        return graph.put_object(ID, "feed", message=message)