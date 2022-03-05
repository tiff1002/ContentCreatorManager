"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.platform.platform
import contentcreatormanager.media.post.reddit
import praw
import requests

class Reddit(contentcreatormanager.platform.platform.Platform):
    """
    classdocs
    """
    CLIENT_SECRETS_FILE = 'reddit_client_secret.json'
    
    URL = 'https://www.reddit.com'

    def __init__(self, settings : contentcreatormanager.config.Settings):
        """
        Constructor takes a Settings object.  No ID for Reddit Platform object.
        """
        super(Reddit, self).__init__(settings=settings, ID='')
        
        self.logger = self.settings.Reddit_logger
        self.logger.info("Initializing Platform Object as Reddit Platform object")
        
        data = self.read_json(Reddit.CLIENT_SECRETS_FILE)
        
        self.client_id = data['client_id']
        self.client_secret = data['client_secret']
        self.user_agent = data['user_agent']
        self.redirect_uri = data['redirect_uri']
        self.refresh_token = data['refresh_token']
        
        self.praw = praw.Reddit(client_id=data['client_id'],client_secret=data['client_secret'],
                                user_agent=data['user_agent'],redirect_uri=data['redirect_uri'],
                                refresh_token=data['refresh_token'])
        
        self.logger.info("Reddit Platform Object initialized")
        
    def post_text(self, subr : str, title : str, body : str):
        """
        Method to create and send a Reddit post to a subreddit and add it to media_objects
        """
        self.logger.info("Creating Reddit Post")
        
        post = contentcreatormanager.media.post.reddit.RedditTextPost(reddit=self, title=title, body=body, subr=subr)
        
        post.upload()
        
        if post.is_uploaded():
            self.logger.info("Post found online")
        else:
            self.logger.error("Could not find post online")
        
        self.add_media(post)
        self.logger.info("Added post to media_objects")
        
        return post
        
    def api_submit_text(self, subreddit : str, title : str, selftext : str = '', flair_id : str = '', flair_text : str = '', send_replies : bool = True, nsfw : bool = False):
        """
        Method to make an API call to reddit to post text to a subreddit returns a praw submission object that url and id can be retrieved from as properties
        Example Call: api_submit_text(subreddit='test', title='CCC Test Post', selftext='posted with this project: https://odysee.com/@TechGirlTiff:5/ContentCreatorManager_Dev_Project_Update_00004:4')
        Example Return ID (plain old return or use the id property): t6l0o2
        Example Return URL (the url property): https://www.reddit.com/r/test/comments/t6l0o2/ccc_test_post/
        """
        self.logger.info("Making Reddit API call to post text to a subreddit")
        
        subreddit = self.praw.subreddit(subreddit)
        
        
        if not (flair_id == '' or flair_id is None):
            if not(flair_text == '' or flair_text is None):
                result = subreddit.submit(title=title, selftext=selftext, flair_id=flair_id, flair_text=flair_text, send_replies=send_replies, nsfw=nsfw)  
            else:
                result = subreddit.submit(title=title, selftext=selftext, flair_id=flair_id, send_replies=send_replies, nsfw=nsfw)
        elif not(flair_text == '' or flair_text is None):
            result = subreddit.submit(title=title, selftext=selftext, flair_text=flair_text, send_replies=send_replies, nsfw=nsfw)                          
        else:
            result = subreddit.submit(title=title, selftext=selftext, send_replies=send_replies, nsfw=nsfw)       
        
        return result
    
    def api_submit_url(self, subreddit : str, title : str, url : str = '', flair_id : str = '', flair_text : str = '', send_replies : bool = True, nsfw : bool = False):
        """
        Method to make an API call to reddit to post a url to a subreddit a praw submission object that url and id can be retrieved from as properties
        Example Call: api_submit_url(subreddit='test', title='CCC Test URL Post', url='https://odysee.com/@TechGirlTiff:5/ContentCreatorManager_Dev_Project_Update_00004:4')
        Example Return ID (plain old return or use the id property): t6l1ou
        Example Return URL (the url property): https://odysee.com/@TechGirlTiff:5/ContentCreatorManager_Dev_Project_Update_00004:4 (note this returns the URL the post links to but the link to the comments could be constructed https://www.reddit.com/r/test/comments/t6l1ou/ccc_test_url_post/)
        """
        self.logger.info("Making Reddit API call to post a URL to a subreddit")
        
        subreddit = self.praw.subreddit(subreddit)
        
        if not (flair_id == '' or flair_id is None):
            if not(flair_text == '' or flair_text is None):
                result = subreddit.submit(title=title, url=url, flair_id=flair_id, flair_text=flair_text, send_replies=send_replies, nsfw=nsfw)  
            else:
                result = subreddit.submit(title=title, url=url, flair_id=flair_id, send_replies=send_replies, nsfw=nsfw)
        elif not(flair_text == '' or flair_text is None):       
            result = subreddit.submit(title=title, url=url, flair_text=flair_text, send_replies=send_replies, nsfw=nsfw)      
        else:
            result = subreddit.submit(title=title, url=url, send_replies=send_replies, nsfw=nsfw) 
        
        return result
    