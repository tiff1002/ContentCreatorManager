'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.post.post


class RedditPost(contentcreatormanager.media.post.post.Post):
    '''
    classdocs
    '''


    def __init__(self, reddit, title : str, body : str, subr : str):
        '''
        Constructor takes a Reddit Platform Object as well as title and body strings for the post
        '''
        super(RedditPost, self).__init__(platform=reddit, body=body, title=title)
        self.logger = self.settings.Reddit_logger
        
        self.logger.info("Initializing Post Object as a Reddit Post")
        
        self.subr = subr
        
        self.logger.info("Reddit Post initialized")
        
        
    def upload(self):   
        """Method to send this Post to it subreddit""" 
        self.logger.info(f"Attempting to make a post to subreddit {self.subr}")
        
        subreddit = self.platform.praw.subreddit(self.subr)
        result = subreddit.submit(self.title,selftext=self.body)
        
        return result