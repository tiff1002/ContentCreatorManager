'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.lbry
import contentcreatormanager.platform.lbry
import os.path
import requests
import time

class LBRYTextPost(contentcreatormanager.media.lbry.LBRYMedia):
    '''
    classdocs
    '''
    def __write_description_to_file(self):
        """Private Method to write the description property to a md file"""
        if os.path.isfile(self.file):
            self.logger.warning(f"{self.file} already exists.  Removing before recreating it")
            os.remove(self.file)
        
        with open(self.file, 'w') as f:
            f.write(self.description)
        f.close()

    def __init__(self, lbry_channel, title : str, body : str, name : str, tags : list = [], 
                 bid : str = "0.001", thumbnail_url : str = '', languages : list = ['en']):
        '''
        Constructor takes LBRY Platform object, title and body for the LBRY Post
        '''
        super(LBRYTextPost, self).__init__(lbry_channel=lbry_channel, file_name='', thumbnail_url=thumbnail_url, description=body, 
                                           languages=languages, permanent_url='', tags=tags, bid=bid, title=title, name=name, ID='')
        self.logger = self.settings.LBRY_logger
        
        self.logger.info("Initializing Media Object as LBRY Post Object")
        self.name = self.get_valid_name(title)
        self.file = os.path.join(os.getcwd(), f"{self.name}.md")

        self.logger.info("LBRY Post Object Initialized")
        
    def upload(self):
        """Method to send this post to the LBRY Channel tied to the Platform object tied to the post"""
        self.__write_description_to_file()
        
        params = {
            "name":self.name,
            "bid":self.bid,
            "file_path":self.file,
            "title":self.title,
            "tags":self.tags,
            "languages":self.languages,
            "thumbnail_url":self.thumbnail_url,
            "channel_id":self.platform.id
        }
        #Make stream_create API call with params
        result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "stream_create", "params": params}).json()
        
        #Check results for errors
        if self.platform.check_request_for_error(result):
            self.logger.error("No Upload Made")
            return None
        
        #Setting claim_id returned by the API call
        self.logger.info(f"Setting claim_id to {result['result']['outputs'][0]['claim_id']}")
        self.id = result['result']['outputs'][0]['claim_id']
        
        self.logger.info("stream_create API call complete without error")
        
        finished = False
        
        #Loop until finished is set to True
        while not finished:
            self.logger.info(f"Post {self.title} made to LBRY.  Sleeping 1 min before checking for completion")
            time.sleep(60)
            
            #Once this is uploaded set finished to True
            if self.is_uploaded():
                finished = True
                
        self.logger.info("Post made to LBRY")
        return result['result']
        