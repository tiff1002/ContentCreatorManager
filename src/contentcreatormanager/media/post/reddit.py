"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.media.post.post as media_post
import contentcreatormanager.platform.reddit as reddit_plat
import requests

class RedditTextPost(media_post.Post):
    """
    classdocs
    """

    def __init__(self, reddit, title : str, body : str, subr : str):
        """
        Constructor takes a Reddit Platform Object as well as title and body strings for the post
        """
        super(RedditTextPost, self).__init__(platform=reddit, body=body, title=title)
        self.logger = self.settings.Reddit_logger
        
        self.logger.info("Initializing Post Object as a Reddit Post")
        
        self.subr = subr
        self.permalink = ''
        self.url = ''
        
        self.logger.info("Reddit Post initialized")
        
    def upload(self):   
        """
        Method to send this Post to it subreddit
        """ 
        self.logger.info(f"Attempting to make a post to subreddit {self.subr} with title {self.title}")
        
        self.logger.info("Checking to see if post is a valid URL")
        try:
            requests.get(self.body)
            url = True
        except requests.ConnectionError:
            url = False
        except requests.exceptions.InvalidSchema:
            url = False
        
        if url:
            self.logger.info(f"Post is a URL post: {self.body}")
            result = self.platform.api_submit_url(subreddit=self.subr, title=self.title, url=self.body)
        else:
            self.logger.info(f"Post is a Text post: {self.body}")
            result = self.platform.api_submit_text(subreddit=self.subr, title=self.title, selftext=self.body)
        
        self.logger.info(f"Set Post id to {result.id} permalink to {result.permalink} and url to {result.url}")
        self.id = result.id
        self.permalink = result.permalink
        self.url = result.url
        
        return result
    
    def is_uploaded(self):
        """
        Method to check if the Post is uploaded and set flag for it
        """
        response = requests.get(self.get_post_url)
        if response.status_code == 200:
            self.uploaded = True
            return True
        else:
            self.uploaded = False
            return False 
    
    def get_post_url(self):
        """
        Method to get the URL of the post
        """       
        if reddit_plat.Reddit.URL in self.url:
            return self.url
        else:        
            return f"{reddit_plat.Reddit.URL}{self.permalink}"