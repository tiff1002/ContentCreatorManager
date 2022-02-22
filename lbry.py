'''
Created on Feb 21, 2022

@author: tiff
'''
import requests
import config
import os.path
import pathlib

def check_request_for_error(request, logger):
    if 'error' in request:
        logger.error("API call returned an error:")
        logger.error(f"Error Code: {request['error']['code']}")
        logger.error(f"Error Type: {request['error']['data']['name']}")
        logger.error(f"Error Message: {request['error']['message']}")
        return True
    return False

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
        if check_request_for_error(result, self.logger):
            raise Exception()
        
        return result

    def __set_videos(self):
        params = {
            "channel_id": [self.claim_id],
            "order_by":'name'
        }
        intial_result = requests.post(Channel.API_URL, json={"method": "claim_list", "params": params}).json()
        if check_request_for_error(intial_result, self.logger):
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
        self.title = result['result']['items'][0]['value']['title']
        
        if 'languages' in result['result']['items'][0]['value']:
            self.languages = result['result']['items'][0]['value']['languages']
        else:
            self.languages = ['en']
        if 'tags' in result['result']['items'][0]['value']:
            self.tags = result['result']['items'][0]['value']['tags']
        else:
            self.tags = []
        if 'thumbnail' in result['result']['items'][0]['value']:    
            self.thumbnail = result['result']['items'][0]['value']['thumbnail']
        else:
            self.thumbnail = None
            
        self.videos = []          
        if init_vids:
            self.__set_videos()
        
        
class Video(object):
    '''
    classdocs
    '''
    def __fix_name(self):
        self.logger.info(f"Fix Name running current name: {self.name}")
        valid_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-'
        getVals = list([val for val in self.name if val in valid_chars])
        self.name = "".join(getVals)
        self.logger.info(f"Fix Name ran name is now: {self.name}")
    
    def __file_path(self):
        return pathlib.Path(os.path.join(os.getcwd(), self.file_name))
    
    def __upload_new(self):
        params = {
            "name":self.name,
            "bid":self.bid,
            "file_path":str(self.__file_path().resolve()),
            "title":self.title,
            "description":self.description,
            "tags":self.tags,
            "languages":self.languages,
            "thumbnail_url":self.thumbnail_url,
            "channel_id":self.channel.claim_id
        }
        result = requests.post(Channel.API_URL, json={"method": "stream_create", "params": params}).json()
        
        if check_request_for_error(result, self.logger):
            self.logger.error("No Upload Made")
            return
        
        self.logger.info("Upload complete")
        return result['result']
    
    def __update_to_lbry(self):
        params = {
            "claim_id":self.claim_id,
            "bid":self.bid,
            "title":self.title,
            "description":self.description,
            "tags":self.tags,
            "clear_tags":True,
            "languages":self.languages,
            "clear_languages":True,
            "thumbnail_url":self.thumbnail_url,
            "channel_id":self.channel.claim_id
        }
        result = requests.post(Channel.API_URL, json={"method": "stream_update", "params": params}).json()
            
        if check_request_for_error(result, self.logger):
            self.logger.error("No Update Made")
            return
        
        self.logger.info("Update to LBRY successful")
        
        return result['result']
        
    def __update_from_request(self, request):
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
            if 'url' in request['value']['thumbnail']:
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
        
        if check_request_for_error(res, self.logger):
            raise Exception()
        
        result = res['result']['items'][0]
        
        self.__update_with_request(result)
        
    def __update_from_lbry_with_claim_id(self):    
        params = {
            'claim_id':self.claim_id
        }
        res = requests.post(Channel.API_URL, json={"method": "claim_list", "params": params}).json()
        
        if check_request_for_error(res, self.logger):
            raise Exception()
        
        result = res['result']['items'][0]
        
        self.__update_from_request(result)
        
    
    def __init__(self, channel: Channel, address=None,amount='0.02',claim_id=None,
                 name=None,normalized_name=None,description=None,permanent_url=None,
                 languages=['en'], file_name=None, tags=[],thumbnail_url='', 
                 title=None, request=None):
        self.logger = channel.settings.LBRY_logger
        self.logger.info("Initializing Video Object")
        self.settings = channel.settings
        self.channel = channel
        self.address = address
        self.bid = amount
        self.claim_id = claim_id
        self.name = name
        if self.name is not None:
            self.__fix_name()
        self.normalized_name = normalized_name
        self.permanent_url = permanent_url
        self.description = description
        self.languages = languages
        self.file_name = file_name
        self.tags = tags
        self.thumbnail_url = thumbnail_url
        self.title = title
        if request is not None:
            self.__update_from_request(request)
        elif self.claim_id is not None:
            self.__update_from_lbry_with_claim_id()
        elif self.name is not None:
            self.__update_from_lbry_with_name()
            
    def update_local(self):
        if self.claim_id is None:
            self.logger.error("claim_id required to update loca object from lbry")
            return
        self.__update_from_lbry_with_claim_id()
        
    def update_lbry(self):
        return self.__update_to_lbry()
    
    def upload(self):
        if pathlib.Path(os.path.join(os.getcwd(),self.file_name)).is_file() and self.claim_id is None:
            if self.name is None:
                self.logger.error("name required to upload stream")
            else:
                if self.title is None:
                    self.logger.error("title must be set to upload")
                else:
                    if self.description is None:
                        self.logger.error("description must be set to upload")
                    else:
                        self.__upload_new()
        else:
            self.logger.error("Upload requires there be a file_name set that points to a file and claim_id can not already be set")
        
