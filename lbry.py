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
        params = {
            'claim_id':self.claim_id
        }
        result = requests.post(Channel.API_URL, json={"method": "channel_list", "params": params}).json()
        if 'error' in result:
            self.logger.error("API call returned an error:")
            self.logger.error(f"Error Code: {result['error']['code']}")
            self.logger.error(f"Error Type: {result['error']['data']['name']}")
            self.logger.error(f"Error Message: {result['error']['message']}")
            raise Exception()
        
        return result

    def __set_videos(self):
        params = {
            "channel_id": [self.claim_id],
            "order_by":'name'
        }
        intial_result = requests.post(Channel.API_URL, json={"method": "claim_list", "params": params}).json()
        if 'error' in intial_result:
            self.logger.error("API call returned an error:")
            self.logger.error(f"Error Code: {intial_result['error']['code']}")
            self.logger.error(f"Error Type: {intial_result['error']['data']['name']}")
            self.logger.error(f"Error Message: {intial_result['error']['message']}")
            raise Exception()
        
        page_amount = intial_result['result']['total_pages']
        item_amount = intial_result['result']['total_items']
        
        self.logger.info(f"Found {item_amount} videos on channel {self.claim_id} with {page_amount} pages of data")
        
        pages = []
        claims = []
        
        self.logger.info("adding initial request as 1st page of data")
        pages.append(intial_result['result']['items'])
        
        for x in range(page_amount-1):
            params = {
                "page":x+2, 
                "channel_id": [self.claim_id],
                "order_by":'name'      
            }
            self.logger.info(f"getting page {x+2} of data and adding it")
            current_result = requests.post(Channel.API_URL, json={"method": "claim_list", "params": params}).json()
            pages.append(current_result['result']['items'])
            
        page = 0
        x = 0
        for p in pages:
            page += 1
            for i in p:
                x += 1
                if i['value']['stream_type'] == 'video':
                    self.logger.info(f"Adding claim with claim_id {i['claim_id']} and name {i['name']} from page {page} of the results")
                    claims.append(i)
                else:
                    self.logger.info(f"claim {i['name']} is a {i['value']['stream_type']} not a video.  Not adding it")
        
        for c in claims:
            v = Video(channel=self,request=c)
            
            self.videos.append(v)
        
    
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
    def __update_with_request(self, request):
        self.address = request['address']
        self.bid = request['amount']
        self.claim_id = request['claim_id']
        self.name = request['name']
        self.normalized_name = request['normalized_name']
        self.permanent_url = request['permanent_url']
        self.languages = request['value']['languages']
        self.file_name = request['value']['source']['name']
        self.title = request['value']['title']
        
        if 'thumbnail' in request['value']:
            self.thumbnail_url = request['value']['thumbnail']['url']
        if 'tags' in request['value']:
            self.tags = request['value']['tags']
        if 'description' in request['value']:
            self.description = request['value']['description']
    
    def __update_from_lbry_with_name(self):
        params = {
            'name':self.name
        }
        res = requests.post(Channel.API_URL, json={"method": "claim_list", "params": params}).json()
        
        if 'error' in res:
            self.logger.error("API call returned an error:")
            self.logger.error(f"Error Code: {res['error']['code']}")
            self.logger.error(f"Error Type: {res['error']['data']['name']}")
            self.logger.error(f"Error Message: {res['error']['message']}")
            raise Exception()
        
        result = res['result']['items'][0]
        
        self.__update_with_request(result)
        
    def __update_from_lbry_with_claim_id(self):    
        params = {
            'claim_id':self.claim_id
        }
        res = requests.post(Channel.API_URL, json={"method": "claim_list", "params": params}).json()
        
        if 'error' in res:
            self.logger.error("API call returned an error:")
            self.logger.error(f"Error Code: {res['error']['code']}")
            self.logger.error(f"Error Type: {res['error']['data']['name']}")
            self.logger.error(f"Error Message: {res['error']['message']}")
            raise Exception()
        
        result = res['result']['items'][0]
        
        self.__update_with_request(result)
        
    
    def __init__(self, channel: Channel, address=None,amount='.02',claim_id=None,
                 name=None,normalized_name=None,description=None,permanent_url=None,
                 languages=['en'], file_name=None, tags=[],thumbnail_url=None, 
                 title=None, request=None):
        self.logger = channel.settings.LBRY_logger
        self.logger.info("Initializing Video Object")
        self.settings = channel.settings
        self.channel = channel
        self.address = address
        self.bid = amount
        self.claim_id = claim_id
        self.name = name
        self.normalized_name = normalized_name
        self.permanent_url = permanent_url
        self.description = description
        self.languages = languages
        self.file_name = file_name
        self.tags = tags
        self.thumbnail_url = thumbnail_url
        self.title = title
        if request is not None:
            self.__update_with_request(request)
        elif self.claim_id is not None:
            self.__update_from_lbry_with_claim_id()
        elif self.name is not None:
            self.__update_from_lbry_with_name()
        
