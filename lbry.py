'''
Created on Feb 21, 2022

@author: tiff
'''
import requests
import config

class Channel(object):
    '''
    classdocs
    '''
    API_URL = "http://localhost:5279"

    def __get_channel(self):
        return requests.post(Channel.API_URL, json={"method": "channel_list", "params": {'claim_id':self.claim_id}}).json()

    def __set_videos(self):
        return
    def __init__(self, claim_id, settings : config.Settings, init_vids=True):
        '''
        Constructor
        '''
        self.logger = settings.LBRY_logger
        self.settings = settings
        self.claim_id = claim_id
        
        result = self.__get_channel()
        
        self.address = result['result']['items'][0]['address']
        self.bid = result['result']['items'][0]['amount']
        self.name = result['result']['items'][0]['name']
        self.normalized_name = result['result']['items'][0]['normalized_name']
        self.permanent_url = result['result']['items'][0]['permanent_url']
        self.description = result['result']['items'][0]['value']['description']
        self.email = result['result']['items'][0]['value']['email']
        self.languages = result['result']['items'][0]['value']['languages']
        self.tags = result['result']['items'][0]['value']['tags']
        self.thumbnail = result['result']['items'][0]['value']['thumbnail']
        self.title = result['result']['items'][0]['value']['title']
        self.videos = []          
        if init_vids:
            self.__set_videos()
        
        
class Video(object):
    '''
    classdocs
    '''
    
    
    def __init__(self):
        self.test = ''