'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.post.post
import facebook

class FacebookPost(contentcreatormanager.media.post.post.Post):
    '''
    classdocs
    '''
    def __post_init(self):
        """Private Method to initialize things to make a facebook post"""
        self.platform.graph = facebook.GraphAPI(self.platform.access_token)
        self.platform.resp = self.platform.graph.get_object('me/accounts')

        for page in self.platform.resp['data']:
            if page['id'] == self.platform.id:
                self.platform.page_access_token = page['access_token']
                
        self.platform.graph = facebook.GraphAPI(self.platform.page_access_token)

    def __init__(self, facebook, post : str):
        '''
        Constructor takes a Facebook Platform object as well as the body of the post as a string
        '''
        #Call super class constructor
        super(FacebookPost, self).__init__(platform=facebook,title='',body=post)
        
        
        self.logger = self.settings.Facebook_logger
        self.logger.info("Initializing Post object as a Facebook Post")
        
        self.logger.info("Facebook Post Object initialized")
        
    def upload(self):
        """Method to send this post to the facebook page tied to the Facebook Platform Object tied to this object"""
        self.__post_init()
        result = self.platform.graph.put_object(self.platform.id, "feed", message=self.body)
        return result