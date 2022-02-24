'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import requests
import contentcreatormanager.media.video.video
import contentcreatormanager.platform.lbry

class LBRYVideo(contentcreatormanager.media.video.video.Video):
    '''
    classdocs
    '''
    def __request_data(self):
        params = {
            'claim_id':self.id
        }
        res = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "claim_list", "params": params}).json()
        
        if self.channel.check_request_for_error(res):
            raise Exception()
        
        result = res['result']['items'][0]
        
        return result
    
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
        
        result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "stream_create", "params": params}).json()
        
        if self.channel.check_request_for_error(result):
            self.logger.error("No Upload Made")
            return
        
        self.logger.info("Upload complete")
        return result['result']
    
    def __update_lbry(self):
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
        result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "stream_update", "params": params}).json()
            
        if self.channel.check_request_for_error(result):
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
        self.file = os.path.join(os.getcwd(), request['value']['source']['name'])
        self.title = request['value']['title']
        
        if 'thumbnail' in request['value']:
            if 'url' in request['value']['thumbnail']:
                self.thumbnail_url = request['value']['thumbnail']['url']
        if 'tags' in request['value']:
            self.tags = request['value']['tags']
        if 'description' in request['value']:
            self.description = request['value']['description']

    def __init__(self, settings : contentcreatormanager.config.Settings, lbry_channel, ID : str = '', file_name : str = '', request = None):
        '''
        Constructor
        '''
        super(LBRYVideo, self).__init__(settings=settings,ID=ID,file_name=file_name)
        self.logger = self.settings.LBRY_logger
        
        self.logger.info("Initializing Video Object as a LBRY Video Object")
        
        self.channel = lbry_channel
        
        if request is not None:
            self.__update_from_request(request)
        elif self.id != '':
            self.update_local()
        
    def update_local(self):
        self.__update_from_request(self.__request_data())
        
    def update_web(self):
        self.logger.info(f"Attmepting to update LBRY claim {self.ID}")
        return self.__update_contentcreatormanager.platform.lbry()
    
    def upload(self):
        file_name = os.path.basename(self.file)
        self.loger.info(f"Attempting to upload {file_name}")
        return self.__upload_to_contentcreatormanager.platform.lbry(self)
        