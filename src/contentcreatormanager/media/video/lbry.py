'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import requests
import contentcreatormanager.media.lbry
import contentcreatormanager.platform.lbry
import time
import shutil
import hashlib

class LBRYVideo(contentcreatormanager.media.lbry.LBRYMedia):
    '''
    classdocs
    '''
    
    
    def __check_file_hash(self):
        """Private method to calculate the file_hash of the video file and compare it to what is on LBRY blockchain.  Returns True if it matches."""
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
    
    def __request_file_save_data(self):
        """Private Method to run file_save api call and return results.  This should cause a file to be built from downloaded blobs.  The call uses claim_id to determine what video to run this call on"""
        file_name = os.path.basename(self.file)
        params = {
            "claim_id":self.id,
            "download_directory":self.settings.folder_location,
            "file_name":file_name
        }
        
        self.logger.info(f"Sending file_save call to API to get {file_name} from downloaded blobs")
        
        return requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "file_save", "params": params}).json() 
    
    def __request_get_data(self):
        """Private Method to run the get API call.  It uses uri (permanent_url) and returns the results of the call.  This will cause blobs to be downloaded if they are not."""
        file_name = os.path.basename(self.file)
        get_params = {
            "uri":self.permanent_url,
            "download_directory":self.settings.folder_location,
            "file_name":file_name
        }
        
        self.logger.info(f"Sending get call to API to download {file_name} blobs")
        
        return requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "get", "params": get_params}).json() 
        
    def __request_data(self):
        """
        Private method to request data via the claim_list api call using the claim_id stored in self.id.  
        This Method will raise an exception if no results are found or if there is an error in the results
        """
        params = {
            'claim_id':self.id
        }
        
        #Make the API call
        res = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "claim_list", "params": params}).json()
        
        #Check API call for errors
        if self.platform.check_request_for_error(res) or res['result']['total_items'] == 0:
            raise Exception()
        
        #return the result portion of the results
        return res['result']['items'][0]
    
    def __request_data_with_name(self):
        """
        Private method to get API request data for claim_list using the self.name property as the name for lookup.
        This Method will raise an exception if no results are found or if there is an error in the results
        """
        params = {
            'name':self.name
        }
        
        #Make API call
        res = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "claim_list", "params": params}).json()
        
        #Check for Errors
        if self.platform.check_request_for_error(res) or res['result']['total_items'] == 0:
            raise Exception()
        
        #return the result portion of the results
        return res['result']['items'][0]
    
    def __delete_from_lbry(self, do_not_download : bool = False):
        """Private Method to delete the Video object from LBRY."""
        params = {
            "claim_id":self.id
        }
        
        self.logger.info("Preparing to delete video from LBRY first running download()")
        
        if not do_not_download:
            self.logger.info("do_not_download flag not set.  Ensuring the video file is downloaded before removing from LBRY")
            self.download()
        
        self.logger.info("Running API call to delete blobs from the system")
        #Delete the blobs from system
        file_delete_result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "file_delete", "params": params}).json()
        if self.platform.check_request_for_error(file_delete_result):
            self.logger.error("Got error while running file_delete.  Exiting stream_abandon not run")
            return None
        
        self.logger.info("Running API call to remove the stream from LBRY")
        #Remove the claim from LBRY
        stream_abandon_result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "stream_abandon", "params": params}).json()
        if self.platform.check_request_for_error(stream_abandon_result):
            self.logger.error("Got error while running stream_abandon.  This means blobs were deleted but claim is still on LBRY. Exiting")
            return None
        
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
    
    def __upload_new(self):
        """
        Private Method for uploading a new video to LBRY.  This uses the stream_create api call.  This method will also set the id to the new claim_id from the upload.
        This method just makes the API call and does nothing to confirm it worked or is complete.
        """
        params = {
            "name":self.name,
            "bid":self.bid,
            "file_path":self.file,
            "title":self.title,
            "description":self.description,
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
        return result['result']
    
    def __update_lbry(self):
        """Private Method to update Video details on LBRY using the local object properties.  This uses the stream_update API call."""
        params = {
            "claim_id":self.id,
            "bid":self.bid,
            "title":self.title,
            "description":self.description,
            "tags":self.tags,
            "clear_tags":True,
            "languages":self.languages,
            "clear_languages":True,
            "thumbnail_url":self.thumbnail_url,
            "channel_id":self.platform.id
        }
        #Make stream_update API call
        result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "stream_update", "params": params}).json()
            
        #Check for errors
        if self.platform.check_request_for_error(result):
            self.logger.error("No Update Made")
            return
        
        #Return results of sucessfull API call
        self.logger.info("Update to LBRY successful")
        return result['result']

    def __update_from_request(self, request):
        """Private Method to update the local object from a provided request result (Only works with some API calls claim_list works for one)"""
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

    def __init__(self, lbry_channel, ID : str = '', tags : list = [], title : str = '',file_hash : str = '', file_name : str = '', name : str = '', 
                 thumbnail_url : str = '', bid : str = '0.001', address : str = '', description : str = '', permanent_url : str = '', 
                 languages : list = ['en'], request = None):
        '''
        Constructor takes LBRY Platform object as required parameter.  LBRY Video Object can be constructed with the results of an API call to claim_list just set the request parameter.
        All details can be manually set on creation.  bid defaults very low, language defaults to en
        '''
        super(LBRYVideo, self).__init__(lbry_channel=lbry_channel, file_name=file_name, thumbnail_url=thumbnail_url, 
                                        description=description, languages=languages, permanent_url=permanent_url, 
                                        tags=tags, bid=bid, title=title, name=name, ID=ID)
        self.logger = self.settings.LBRY_logger
        
        self.logger.info("Initializing Video Object as a LBRY Video Object")
        
        #Set various object properties
        self.address = address
        self.file_hash = file_hash
        
        #If request is supplied update the object with that
        if request is not None:
            self.__update_from_request(request)
        #If no request is present but an id is update with that
        elif self.id != '':
            self.update_local()
        #If all that fails but a name is given
        elif self.name != '':
            #Putting this in try block since you might set name on creation of a new video not yet uploaded
            try:
                self.update_local(use_name=True)
            except:
                self.logger.error("Could not update with name not found on LBRY")
        self.logger.info("LBRY Video Media Object initialized")
        
    def update_local(self, use_name : bool = False):
        """Method to update the local object properties from LBRY.  It will do the LBRY lookup with claim_id unless the use_name flag is set to True"""
        if use_name:
            self.__update_from_request(self.__request_data_with_name())
        else:
            self.__update_from_request(self.__request_data())
        
    def delete_web(self):
        """Method to remove Video from LBRY"""
        return self.__delete_from_lbry()
                
    def update_web(self):
        """Method to update data on LBRY based on the local values of the object's properties"""
        self.logger.info(f"Attmepting to update LBRY claim {self.id}")
        return self.__update_lbry()
    
    def download(self):
        """
        Method to download Video from LBRY to local machine.  This will call get to download blobs, file_save to make a file from the 
        blobs and then if the file is in the wrong location (due to LBRY API weirdness) this Method will put it in the right place
        """
        #Making API call to download the blob data
        get_result = self.__request_get_data()
        
        if self.platform.check_request_for_error(get_result):
            self.logger.error("Got error during get exiting download method")
            return
        
        #get streaming_url from results of the api call
        streaming_url = get_result['result']['streaming_url']
        
        self.logger.info(f"running a request on streaming_url: {streaming_url} to wait for blobs to finish downloading")
        requests.get(streaming_url)
        
        #Make API call to create file from saved blob data
        file_save_result = self.__request_file_save_data()
        
        if self.platform.check_request_for_error(file_save_result):
            self.logger.error("Got error during file_save exiting download method")
            return
        
        actual_file_path = file_save_result['result']['download_path']
        desired_file_path = self.file
        
        #If the file is already where we want it return the results and be done with it
        if actual_file_path == desired_file_path:         
            return get_result
        #Otherwise try moving it to where we want it
        try:
            shutil.move(actual_file_path, desired_file_path, copy_function = shutil.copy2)
        except Exception as e:
            self.logger.error(f"Got the following error while trying to move the file to the right place:\n{e}")
        else:
            self.logger.info("Move complete without exception")
        finally:
            return get_result
    
    def upload(self):
        """Method to upload the video to LBRY"""
        #Checks to make sure Video is not already uploaded
        if self.is_uploaded():
            self.logger.error("You already uploaded this Video to LBRY.  Exitting method")
            return
        
        #Gets the name of the file to upload
        file_name = os.path.basename(self.file)
        
        #Checks to make sure it is a file
        if not os.path.isfile(self.file):
            self.logger.error(f"Can not find file: {file_name}")
        
        #Runs the upload in the return statement
        self.logger.info(f"Attempting to upload {file_name}")
        result = self.__upload_new()
        
        #If there was an error then the results will be None and this will catch that
        if result is None:
            self.logger.error("No Upload made not updating any properties of LBRY Video Object")
        else:
            #loop through waiting 1 min at a time until we can confirm the upload is complete
            finished = False
            while not finished:
                self.logger.info("Sleeping for 1 min before checking for completion of upload")
                time.sleep(60)
                if self.is_uploaded():
                    self.update_local(use_name=True)
                    finished = True
        return result