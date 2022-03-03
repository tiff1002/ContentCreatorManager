'''
Created on Feb 28, 2022

@author: tiff
'''
import contentcreatormanager.media.media
import contentcreatormanager.platform.lbry
import os.path
import requests
import time
import hashlib

class LBRYMedia(contentcreatormanager.media.media.Media):
    '''
    classdocs
    '''
    def __init__(self, lbry_channel, file_name : str = "", thumbnail_url : str = '', description : str = "", languages : list = ['en'], 
                 permanent_url : str = '', tags : list = [], bid : float = .001, title : str = '', name : str = "", ID : str=''):
        '''
        Constructor
        '''
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
        
    def get_valid_name(self, name : str):
        """Method to get a valid LBRY stream name from provided input"""
        valid_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-'
        getVals = list([val for val in name if val in valid_chars])
        return "".join(getVals)
    
    def is_uploaded(self):
        """
        Method to determine if the LBRY Media Object is uploaded to the LBRY.  It tries to find the video both via name and claim_id.  
        If neither returns a result the method returns False.  Otherwise it returns True
        """
        #First try looking up via claim_id
        try:
            self.request_data()
        except:
            #Exception means this failed so try looking up by name
            self.logger.info(f"Could not find data looking up via ID: {self.id}")
            try:
                self.request_data_with_name()
            except:
                #Exception means this also failed so return False
                self.logger.info(f"Could not find data looking up via name: {self.name}")
                return False
        self.logger.info("Was able to find Media returning True")
        return True
        
    def request_data(self):
        """
        Method to request data via the claim_list api call using the claim_id stored in self.id.  
        This Method will raise an exception if no results are found or if there is an error in the results
        """
        #Make the API call
        result = self.platform.api_claim_list(claim_id=self.id)
        #Check API call for errors
        if self.platform.check_request_for_error(result) or result['result']['total_items'] == 0:
            self.logger.error("Can not get object data")
            return result
        
        #return the result portion of the results
        return result['result']['items'][0]
    
    def request_data_with_name(self):
        """
        Method to get API request data for claim_list using the self.name property as the name for lookup.
        This Method will raise an exception if no results are found or if there is an error in the results
        """
        params = {
            'name':self.name
        }
        
        #Make API call
        result = self.platform.api_claim_list(name=self.name)
        
        #Check for Errors
        if self.platform.check_request_for_error(result) or result['result']['total_items'] == 0:
            self.logger.error("Can not get object data")
            return result
        
        #return the result portion of the results
        return result['result']['items'][0]
    
    def request_get_data(self):
        """Method to run the get API call.  It uses uri (permanent_url) and returns the results of the call.  This will cause blobs to be downloaded if they are not."""
        file_name = os.path.basename(self.file)
        
        self.logger.info(f"Sending get call to API to download {file_name} blobs")
        
        return self.platform.api_get(uri=self.permanent_url, download_directory=self.settings.folder_location, file_name=file_name)
        
    def update_from_request(self, request):
        """Method to update the local object from a provided request result (Only works with some API calls claim_list works for one)"""
        #Set all the object properties
        self.bid = request['amount']
        self.id = request['claim_id']
        self.name = request['name']
        self.normalized_name = request['normalized_name']
        self.permanent_url = request['permanent_url']
        self.languages = request['value']['languages']
        self.file = os.path.join(os.getcwd(), request['value']['source']['name'])
        self.title = request['value']['title']
        self.file_hash = request['value']['source']['sd_hash']
        
        #Set optional properties if they are found
        if 'address' in request:
            self.address = request['address']
        if 'thumbnail' in request['value']:
            if 'url' in request['value']['thumbnail']:
                self.thumbnail_url = request['value']['thumbnail']['url']
        if 'tags' in request['value']:
            self.tags = request['value']['tags']
        if 'description' in request['value']:
            self.description = request['value']['description']
            
    def update_lbry(self):
        """Method to update Video details on LBRY using the local object properties.  This uses the stream_update API call."""
        #Make stream_update API call
        result = self.platform.api_stream_update(claim_id=self.id, bid=self.bid, title=self.title, description=self.description, 
                                                 tags=self.tags, replace=True, languages=self.languages, thumbnail_url=self.thumbnail_url,
                                                 channel_id=self.platform.id)
            
        #Check for errors
        if self.platform.check_request_for_error(result):
            self.logger.error("No Update Made")
            return
        
        #Return results of sucessfull API call
        self.logger.info("Update to LBRY successful")
        return result['result']
    
    def delete_web(self):
        """Method to remove Media from LBRY"""
        return self.delete_from_lbry()
    
    def update_local(self, use_name : bool = False):
        """Method to update the local object properties from LBRY.  It will do the LBRY lookup with claim_id unless the use_name flag is set to True"""
        if use_name:
            self.update_from_request(self.request_data_with_name())
        else:
            self.update_from_request(self.request_data())
            
    def update_web(self):
        """Method to update data on LBRY based on the local values of the object's properties"""
        self.logger.info(f"Attmepting to update LBRY claim {self.id}")
        return self.update_lbry()
    
    def request_file_save_data(self):
        """Method to run file_save api call and return results.  This should cause a file to be built from downloaded blobs.  The call uses claim_id to determine what video to run this call on"""
        file_name = os.path.basename(self.file)
        
        self.logger.info(f"Sending file_save call to API to get {file_name} from downloaded blobs")
        
        return self.platform.api_file_save(claim_id=self.id, download_directory=self.settings.folder_location, file_name=file_name)
    
    def delete_from_lbry(self, do_not_download : bool = False):
        """Method to delete the Video object from LBRY."""
        self.logger.info("Preparing to delete video from LBRY first running download()")
        
        if not do_not_download:
            self.logger.info("do_not_download flag not set.  Ensuring the video file is downloaded before removing from LBRY")
            self.download()
        
        self.logger.info("Running API call to delete blobs from the system")
        #Delete the blobs from system
        file_delete_result = self.platform.api_file_delete(claim_id=self.id)
        
        if self.platform.check_request_for_error(file_delete_result):
            self.logger.error("Got error while running file_delete.  Exiting stream_abandon not run")
            return file_delete_result
        
        self.logger.info("Running API call to remove the stream from LBRY")
        #Remove the claim from LBRY
        stream_abandon_result = self.platform.api_stream_abandon(claim_id=self.id)
        if self.platform.check_request_for_error(stream_abandon_result):
            self.logger.error("Got error while running stream_abandon.  This means blobs were deleted but claim is still on LBRY. Exiting")
            return stream_abandon_result
        
        #Store filename for use in string later
        file_name = os.path.basename(self.file)
        #Set finished variable to False indicating the deletion is not finished
        finished = False
        
        #Loop until finished is set to True
        while not finished:
            self.logger.info(f"Video file {file_name} removed from LBRY.  Sleeping 1 min before checking for completion")
            time.sleep(60)
            
            #Once this no longer registers as uploaded set finished to True
            if not self.is_uploaded():
                finished = True
        
        #finally return the data that was obtained from the final API call in the method
        return stream_abandon_result
    
    def check_file_hash(self):
        """Method to calculate the file_hash of the video file and compare it to what is on LBRY blockchain.  Returns True if it matches."""
        BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
        
        sha384 = hashlib.sha384()
        
        with open(self.file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha384.update(data)
                
        if sha384.hexdigest() == self.file_hash:
            self.logger.info("Hash matches file.  Returning True")
            return True
        
        self.logger.error("File hash and sd_hash do not match.  Returning False")
        return False  