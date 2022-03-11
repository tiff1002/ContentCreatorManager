"""
Created on Feb 28, 2022

@author: tiff
"""
import contentcreatormanager.media.media as media
import os.path
import time
import hashlib

class LBRYMedia(media.Media):
    """
    classdocs
    """
    def __init__(self, lbry_channel, file_name : str = "",
                 thumbnail_url : str = '', description : str = "",
                 languages : list = ['en'], permanent_url : str = '',
                 tags : list = [], bid : float = .001, title : str = '',
                 name : str = "", ID : str='', new_media : bool = False,
                 lic : str = '', license_url : str = ''):
        """
        Constructor
        """
        super(LBRYMedia, self).__init__(platform=lbry_channel, ID=ID)
        self.logger = self.settings.LBRY_logger
        
        self.logger.info("Initializing Media Object as an LBRY Media Object")
        
        self.file = os.path.join(os.getcwd(), file_name)
        self.thumbnail_url = thumbnail_url
        self.description = description
        self.languages = languages
        self.permanent_url = permanent_url
        self.tags = tags
        self.bid = bid
        self.title = title
        self.name = self.get_valid_name(name)
        self.license = lic
        self.license_url = license_url
        
        if not new_media:
            self.update_local()
    
    def get_valid_name(self, name : str):
        """
        Method to get a valid LBRY stream name from provided input
        """
        v='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-'
        valid_chars = v
        getVals = list([val for val in name if val in valid_chars])
        return "".join(getVals)
    
    def is_uploaded(self):
        """
        Method to determine if the LBRY Media Object is uploaded to the LBRY.
        It tries to find the video both via name and claim_id.  
        If neither returns a result the method returns False.
        Otherwise it returns True
        """
        id_result = self.platform.api_claim_list(claim_id=self.id,
                                                 resolve=False)
        name_result = self.platform.api_claim_list(claim_id=self.id,
                                                   resolve=False)
        
        cond1 = id_result['result']['total_items'] == 0
        cond2=name_result['result']['total_items'] == 0
        if cond1 and cond2:
            self.logger.info('Could Not Find Media on LBRY.  Returning False')
            self.uploaded = False
            return False
        self.uploaded = True
        return True
    
    def set_file_based_on_title(self):
        v='`~!@#$%^&+=,-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        valid_chars = v
        file_name = self.title    
        
        getVals = list([val for val in f"{file_name}" if val in valid_chars])
        
        result = "".join(getVals)
        
        m=f"returning and setting the following file name: {result}"
        self.logger.info(m)
        self.file = os.path.join(os.getcwd(), result)
            
        return result
        
    def update_from_request(self, request):
        """
        Method to update the local object from a provided request result
        (Only works with some API calls claim_list works for one)
        """
        if 'result' in request:
            if 'items' in request['result']:
                request = request['result']['items'][0]
        
        self.bid = request['amount']
        self.id = request['claim_id']
        self.name = request['name']
        self.normalized_name = request['normalized_name']
        self.permanent_url = request['permanent_url']
        self.languages = ['en']
        self.file = os.path.join(os.getcwd(), request['value']['source']['name'])
        self.title = request['value']['title']
        self.file_hash = request['value']['source']['sd_hash']
        
        if 'languages' in request['value']:
            self.languages = request['value']['languages']
        if 'address' in request:
            self.address = request['address']
        if 'thumbnail' in request['value']:
            if 'url' in request['value']['thumbnail']:
                self.thumbnail_url = request['value']['thumbnail']['url']
        if 'tags' in request['value']:
            self.tags = request['value']['tags']
        if 'description' in request['value']:
            self.description = request['value']['description']
 
        return request
            
    def update_lbry(self):
        """
        Method to update Media details on LBRY using the local object
        properties.  This uses the stream_update API call.
        """
        if not self.is_uploaded():
            self.logger.error("Can not update as Media if it is not on LBRY")
            
        result = self.platform.api_stream_update(claim_id=self.id,bid=self.bid,
                                                 title=self.title,
                                                 description=self.description, 
                                                 tags=self.tags, replace=True,
                                                 languages=self.languages,
                                                 thumbnail_url=self.thumbnail_url,
                                                 channel_id=self.platform.id,
                                                 file_path=self.file,
                                                 lic=self.license,
                                                 license_url=self.license_url)
        
        self.logger.info("Update to LBRY successful")
        return result
    
    def delete_web(self, do_not_download : bool = False):
        """
        Method to remove Media from LBRY
        """
        if not self.is_uploaded():
            m="Can not delete media from LBRY if it is not on LBRY"
            self.logger.error(m)
            return
            
        m="Preparing to delete Media from LBRY first running download()"
        self.logger.info(m)
        
        if not do_not_download:
            m="do_not_download not set.  downloading before removing from LBRY"
            self.logger.info(m)
            if self.download() == 'get_error':
                self.logger.error("Could Not Download.  Not Going to delete")
                return 'download_error'
        
        self.logger.info("Running API call to delete blobs from the system")
        file_delete_result = self.platform.api_file_delete(claim_id=self.id)
        
        if file_delete_result['result']:
            self.logger.info("file_delete returned True.  Blobs deleted")
        else:
            m="file_delete returned False."
            self.logger.warning(m)
        
        m="Running API call to remove the stream from LBRY"
        self.logger.info(m)
        stream_abandon_result=self.platform.api_stream_abandon(claim_id=self.id)
        
        file_name = os.path.basename(self.file)
        
        finished = False
        while not finished:
            m=f"Video file {file_name} removed from LBRY."
            self.logger.info(m)
            m="Sleeping 1 min before checking for completion"
            self.logger.info(m)
            time.sleep(60)
            
            if not self.is_uploaded():
                finished = True
        
        return stream_abandon_result
    
    def update_local(self, use_name : bool = False):
        """
        Method to update the local object properties from LBRY.
        It will do the LBRY lookup with claim_id unless the use_name
        flag is set to True
        """
        if not self.is_uploaded():
            m="Video not found can not update local from LBRY"
            self.logger.error(m)
            return 
        
        if use_name:
            request = self.platform.api_claim_list(name=[self.name],resolve=True,claim_type=['stream'])
        else:
            request = self.platform.api_claim_list(claim_id=[self.id],resolve=True,claim_type=['stream'])
        
        if request['result']['total_items'] > 0:
            response = self.update_from_request(request)
        else:
            self.logger.warning("Not on LBRY can not update from there")
            response = request
        
        self.set_file_based_on_title()
        
        return response
            
    def update_web(self):
        """
        Method to update data on LBRY based on the local
        values of the object's properties
        """
        if not self.is_uploaded():
            self.logger.error("Video not on LBRY can not update it")
            return 
        
        self.logger.info(f"Attmepting to update LBRY claim {self.id}")
        return self.update_lbry()
    
    
    
    def check_file_hash(self):
        """
        Method to calculate the file_hash of the video file and compare
        it to what is on LBRY blockchain.  Returns True if it matches.
        """
        BUF_SIZE = 65536  #lets read stuff in 64kb chunks (arbitrary)!
        
        sha384 = hashlib.sha384()#this is the hash type lbry uses for file hash
        
        with open(self.file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha384.update(data)
                
        if sha384.hexdigest() == self.file_hash:
            self.logger.info("Hash matches file.  Returning True")
            return True
        
        m="File hash and sd_hash do not match.  Returning False"
        self.logger.error(m)
        return False  