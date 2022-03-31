"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.config as ccm_config
import contentcreatormanager.platform.platform as plat
import contentcreatormanager.media.post.twitter as twitter_post
import tweepy

class Twitter(plat.Platform):
    """
    classdocs
    """
    CLIENT_SECRETS_FILE = 'twitter_client_secret.json'

    def __init__(self, settings : ccm_config.Settings):
        """
        Constructor takes a Settings object.  No ID for Twitter Platform
        """
        super().__init__(settings=settings, ID='')
        
        self.logger = self.settings.Twitter_logger
        m="Initializing Platform Object as Twitter Platform object"
        self.logger.info(m)
        
        self.logger.info("Loading Twitter Creds")
        
        data = self.read_json(Twitter.CLIENT_SECRETS_FILE)
        
        self.CONSUMER_KEY = data['API_KEY']
        self.CONSUMER_SECRET = data['API_KEY_SECRET']
        self.ACCESS_TOKEN = data['ACCESS_TOKEN']
        self.ACCESS_TOKEN_SECRET = data['ACCESS_TOKEN_SECRET']
        
        self.auth = tweepy.OAuthHandler(self.CONSUMER_KEY,self.CONSUMER_SECRET)
        self.auth.set_access_token(self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)
        try:
            self.api.verify_credentials()
            self.logger.info("Authentication OK")
        except:
            self.logger.error("Error during authentication")
            
        self.logger.info("Twitter Platform Object initialized")
    
    def tweet(self, post : str):
        """
        Method to create and send a Tweet.
        """
        tweet = twitter_post.Tweet(twitter=self, post=post)
        
        result = tweet.upload()
        
        if tweet.is_uploaded():
            self.logger.info("Tweet made it online")
        else:
            self.logger.error("Can not find Tweet online")
        
        self.add_media(tweet)
        
        return result
         
    def update_all_media_local(self):
        """
        Method overridden to disable it for this type of object
        """
        self.logger.info("Tweets are not loaded in from the web")
    
    def update_media_local(self):
        """
        Method overridden to disable it for this type of object
        """
        self.logger.info("Tweets are not loaded in from the web")
        
    def update_all_media_web(self):
        """
        Method overridden to disable it for this type of object
        """
        self.logger.info("Tweets are not sent with this function use tweet")
        
    def update_media_web(self):
        """
        Method overridden to disable it for this type of object
        """
        self.logger.info("Tweets are not sent with this function use tweet")
        
    def api_update_status(self, status_text : str, attachment_url:str='',
                          media_ids:list=[],possibly_sensitive:bool=False):
        """
        Method to make the update_status api call to twitter
        Example Call: api_update_status("Yet another Test Tweet")
        Example Return: Status(_api=<tweepy.api.API object at 0x000001C28CFCEE30>, _json={'created_at': 'Fri Mar 04 13:49:10 +0000 2022', 'id': 1499743756244955139, 'id_str': '1499743756244955139', 'text': 'Yet another Test Tweet', 'truncated': False, 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}, 'source': '<a href="https://odysee.com/@TechGirlTiff:5" rel="nofollow">ContentCreatorManager</a>', 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'user': {'id': 1496249725359730695, 'id_str': '1496249725359730695', 'name': 'TechGirlTiff', 'screen_name': 't_girl_tiff', 'location': '', 'description': 'Tech Girl Tiff', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': False, 'followers_count': 1, 'friends_count': 1, 'listed_count': 0, 'created_at': 'Tue Feb 22 22:25:13 +0000 2022', 'favourites_count': 0, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 12, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': True, 'default_profile': True, 'default_profile_image': False, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none', 'withheld_in_countries': []}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': False, 'retweet_count': 0, 'favorite_count': 0, 'favorited': False, 'retweeted': False, 'lang': 'en'}, created_at=datetime.datetime(2022, 3, 4, 13, 49, 10, tzinfo=datetime.timezone.utc), id=1499743756244955139, id_str='1499743756244955139', text='Yet another Test Tweet', truncated=False, entities={'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}, source='ContentCreatorManager', source_url='https://odysee.com/@TechGirlTiff:5', in_reply_to_status_id=None, in_reply_to_status_id_str=None, in_reply_to_user_id=None, in_reply_to_user_id_str=None, in_reply_to_screen_name=None, author=User(_api=<tweepy.api.API object at 0x000001C28CFCEE30>, _json={'id': 1496249725359730695, 'id_str': '1496249725359730695', 'name': 'TechGirlTiff', 'screen_name': 't_girl_tiff', 'location': '', 'description': 'Tech Girl Tiff', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': False, 'followers_count': 1, 'friends_count': 1, 'listed_count': 0, 'created_at': 'Tue Feb 22 22:25:13 +0000 2022', 'favourites_count': 0, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 12, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': True, 'default_profile': True, 'default_profile_image': False, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none', 'withheld_in_countries': []}, id=1496249725359730695, id_str='1496249725359730695', name='TechGirlTiff', screen_name='t_girl_tiff', location='', description='Tech Girl Tiff', url=None, entities={'description': {'urls': []}}, protected=False, followers_count=1, friends_count=1, listed_count=0, created_at=datetime.datetime(2022, 2, 22, 22, 25, 13, tzinfo=datetime.timezone.utc), favourites_count=0, utc_offset=None, time_zone=None, geo_enabled=False, verified=False, statuses_count=12, lang=None, contributors_enabled=False, is_translator=False, is_translation_enabled=False, profile_background_color='F5F8FA', profile_background_image_url=None, profile_background_image_url_https=None, profile_background_tile=False, profile_image_url='http://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', profile_image_url_https='https://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', profile_link_color='1DA1F2', profile_sidebar_border_color='C0DEED', profile_sidebar_fill_color='DDEEF6', profile_text_color='333333', profile_use_background_image=True, has_extended_profile=True, default_profile=True, default_profile_image=False, following=False, follow_request_sent=False, notifications=False, translator_type='none', withheld_in_countries=[]), user=User(_api=<tweepy.api.API object at 0x000001C28CFCEE30>, _json={'id': 1496249725359730695, 'id_str': '1496249725359730695', 'name': 'TechGirlTiff', 'screen_name': 't_girl_tiff', 'location': '', 'description': 'Tech Girl Tiff', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': False, 'followers_count': 1, 'friends_count': 1, 'listed_count': 0, 'created_at': 'Tue Feb 22 22:25:13 +0000 2022', 'favourites_count': 0, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 12, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': True, 'default_profile': True, 'default_profile_image': False, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none', 'withheld_in_countries': []}, id=1496249725359730695, id_str='1496249725359730695', name='TechGirlTiff', screen_name='t_girl_tiff', location='', description='Tech Girl Tiff', url=None, entities={'description': {'urls': []}}, protected=False, followers_count=1, friends_count=1, listed_count=0, created_at=datetime.datetime(2022, 2, 22, 22, 25, 13, tzinfo=datetime.timezone.utc), favourites_count=0, utc_offset=None, time_zone=None, geo_enabled=False, verified=False, statuses_count=12, lang=None, contributors_enabled=False, is_translator=False, is_translation_enabled=False, profile_background_color='F5F8FA', profile_background_image_url=None, profile_background_image_url_https=None, profile_background_tile=False, profile_image_url='http://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', profile_image_url_https='https://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', profile_link_color='1DA1F2', profile_sidebar_border_color='C0DEED', profile_sidebar_fill_color='DDEEF6', profile_text_color='333333', profile_use_background_image=True, has_extended_profile=True, default_profile=True, default_profile_image=False, following=False, follow_request_sent=False, notifications=False, translator_type='none', withheld_in_countries=[]), geo=None, coordinates=None, place=None, contributors=None, is_quote_status=False, retweet_count=0, favorite_count=0, favorited=False, retweeted=False, lang='en')
        you can access just json results with ._json
        Example JSON Return: {'created_at': 'Fri Mar 04 13:49:10 +0000 2022', 'id': 1499743756244955139, 'id_str': '1499743756244955139', 'text': 'Yet another Test Tweet', 'truncated': False, 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}, 'source': '<a href="https://odysee.com/@TechGirlTiff:5" rel="nofollow">ContentCreatorManager</a>', 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'user': {'id': 1496249725359730695, 'id_str': '1496249725359730695', 'name': 'TechGirlTiff', 'screen_name': 't_girl_tiff', 'location': '', 'description': 'Tech Girl Tiff', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': False, 'followers_count': 1, 'friends_count': 1, 'listed_count': 0, 'created_at': 'Tue Feb 22 22:25:13 +0000 2022', 'favourites_count': 0, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 12, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1496249789423529986/i3ySVh1C_normal.png', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': True, 'default_profile': True, 'default_profile_image': False, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none', 'withheld_in_countries': []}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': False, 'retweet_count': 0, 'favorite_count': 0, 'favorited': False, 'retweeted': False, 'lang': 'en'}
        Possible Exceptions: 
        tweepy.errors.BadRequest: 
        400 Bad Request 
        (This is if you provide an invalid attachment_url as this must be a Tweet permalink or Direct Message deep link)
        """
        self.logger.info("Making update_status Twitter API Call")
        
        if attachment_url == '' or attachment_url is None:
            api=self.api
            ps=possibly_sensitive
            return api.update_status(status=status_text,media_ids=media_ids,
                                          possibly_sensitive=ps)
        else:
            ps=possibly_sensitive
            return self.api.update_status(status=status_text,
                                          media_ids=media_ids,
                                          possibly_sensitive=ps,
                                          attachment_url=attachment_url)