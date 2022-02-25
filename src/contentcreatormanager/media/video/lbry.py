'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import requests
import contentcreatormanager.media.video.video
import contentcreatormanager.platform.lbry
import time
import shutil
import hashlib

class LBRYVideo(contentcreatormanager.media.video.video.Video):
    '''
    classdocs
    '''
    #Private Method that calculates the local file hash and compares it to the stored file_hash property
    def __check_file_hash(self):
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
    
    #Private Method to run file_save api call and return results uses claim_id
    def __request_file_save_data(self):
        file_name = os.path.basename(self.file)
        params = {
            "claim_id":self.id,
            "download_directory":self.settings.folder_location,
            "file_name":file_name
        }
        
        self.logger.info(f"Sending file_save call to API to get {file_name} from downloaded blobs")
        
        return requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "file_save", "params": params}).json() 
    
    #Private Method to run get API call with uri and returns the results of the call
    def __request_get_data(self):
        #Parameters to be used with the get call (basically the uri and setting save_file to True this is being done to be 100% sure we do not remove a claim and blobs for a Video we do not have the video file for
        file_name = os.path.basename(self.file)
        get_params = {
            "uri":self.permanent_url,
            "download_directory":self.settings.folder_location,
            "file_name":file_name
        }
        
        self.logger.info(f"Sending get call to API to download {file_name} blobs")
        
        return requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "get", "params": get_params}).json() 
        
    #Private method to request data via the claim_list api call using the claim_id stored in self.id
    def __request_data(self):
        params = {
            'claim_id':self.id
        }
        
        #Make the API call
        res = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "claim_list", "params": params}).json()
        
        #Check API call for errors
        if self.channel.check_request_for_error(res) or res['result']['total_items'] == 0:
            raise Exception()
        
        #return the result portion of the results
        return res['result']['items'][0]
    
    #Private method to get API request data for claim_list using the self.name property as the name for lookup
    def __request_data_with_name(self):
        params = {
            'name':self.name
        }
        
        #Make API call
        res = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "claim_list", "params": params}).json()
        
        #Check for Errors
        if self.channel.check_request_for_error(res) or res['result']['total_items'] == 0:
            raise Exception()
        
        #return the result portion of the results
        return res['result']['items'][0]
    
    #Private method to check if the LBRY Video is uploaded
    def __is_uploaded(self):
        #First try looking up via claim_id
        try:
            self.__request_data()
        except:
            #Exception means this failed so try looking up by name
            self.logger.info(f"Could not find data looking up via ID: {self.id}")
            try:
                self.__request_data_with_name()
            except:
                #Exception means this also failed so return False
                self.logger.info(f"Could not find data looking up via name: {self.name}")
                return False
        self.logger.info("Was able to find video returning True")
        return True
    
    #Private Method to delete this Video from LBRY
    def __delete_from_lbry(self):
        params = {
            "claim_id":self.id
        }
        
        self.logger.info("Preparing to delete video from LBRY first running download()")
        self.download()
        
        self.logger.info("Running API call to delete blobs from the system")
        #Delete the blobs from system
        file_delete_result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "file_delete", "params": params}).json()
        if self.channel.check_request_for_error(file_delete_result):
            self.logger.error("Got error while running file_delete.  Exiting stream_abandon not run")
            return None
        
        self.logger.info("Running API call to remove the stream from LBRY")
        #Remove the claim from LBRY
        stream_abandon_result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "stream_abandon", "params": params}).json()
        if self.channel.check_request_for_error(stream_abandon_result):
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
            if not self.__is_uploaded():
                finished = True
        
        #finally return the data that was obtained from the final API call in the method
        return stream_abandon_result
    
    #Private Method for uploading a new video to LBRY
    def __upload_new(self):
        params = {
            "name":self.name,
            "bid":self.bid,
            "file_path":self.file,
            "title":self.title,
            "description":self.description,
            "tags":self.tags,
            "languages":self.languages,
            "thumbnail_url":self.thumbnail_url,
            "channel_id":self.channel.id
        }
        #Make stream_create API call with params
        result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "stream_create", "params": params}).json()
        
        #Check results for errors
        if self.channel.check_request_for_error(result):
            self.logger.error("No Upload Made")
            return None
        
        #Setting claim_id returned by the API call
        self.logger.info(f"Setting claim_id to {result['result']['outputs'][0]['claim_id']}")
        self.id = result['result']['outputs'][0]['claim_id']
        
        self.logger.info("stream_create API call complete without error")
        return result['result']
    
    #Private Method to update details of this Video's claim on LBRY
    def __update_lbry(self):
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
            "channel_id":self.channel.id
        }
        #Make stream_update API call
        result = requests.post(contentcreatormanager.platform.lbry.LBRY.API_URL, json={"method": "stream_update", "params": params}).json()
            
        #Check for errors
        if self.channel.check_request_for_error(result):
            self.logger.error("No Update Made")
            return
        
        #Return results of sucessfull API call
        self.logger.info("Update to LBRY successful")
        return result['result']

    #Private Method to update the local object from a provided request result (Only works with some API calls)
    def __update_from_request(self, request):
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

    #Constructor
    def __init__(self, settings : contentcreatormanager.config.Settings, lbry_channel, ID : str = '', tags : list = [], title : str = '',file_hash : str = '', file_name : str = '', name : str = '', thumbnail_url : str = '', bid : str = '0.001', normalized_name : str = '', address : str = '', description : str = '', permanent_url : str = '', languages : list = ['en'], request = None):
        '''
        Constructor
        '''
        super(LBRYVideo, self).__init__(settings=settings,ID=ID,file_name=file_name)
        self.logger = self.settings.LBRY_logger
        
        self.logger.info("Initializing Video Object as a LBRY Video Object")
        
        #set channel property as LBRY Platform object so it can be accessed from here
        self.channel = lbry_channel
        
        #Set various object properties
        self.name = name
        self.normalized_name = normalized_name
        self.address = address
        self.bid = bid
        self.title = title
        self.thumbnail_url = thumbnail_url
        self.description = description
        self.tags = tags
        self.permanent_url = permanent_url
        self.file_hash = file_hash
        self.languages = languages
        #Set up appropriate file_path to live in the file property
        self.file = os.path.join(os.getcwd(), file_name)
        
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
        
    #Method to update the local object properties from LBRY with name or claim_id dependinng on bool parameter defaults to claim_id
    def update_local(self, use_name : bool = False):
        if use_name:
            self.__update_from_request(self.__request_data_with_name())
        else:
            self.__update_from_request(self.__request_data())
        
    #Method to remove Video from LBRY
    def delete_web(self):
        return self.__delete_from_lbry()
            
    #Method to update data on LBRY based on the local values of the properties    
    def update_web(self):
        self.logger.info(f"Attmepting to update LBRY claim {self.id}")
        return self.__update_lbry()
    
    #Method to download Video from LBRY to local machine ultimately it should end up in the folder specified by the settings property
    def download(self):
        #Making API call to download the blob data
        get_result = self.__request_get_data()
        
        if self.channel.check_request_for_error(get_result):
            self.logger.error("Got error during get exiting download method")
            return
        
        #get streaming_url from results of the api call
        streaming_url = get_result['result']['streaming_url']
        
        self.logger.info(f"running a request on streaming_url: {streaming_url} to wait for blobs to finish downloading")
        requests.get(streaming_url)
        
        #Make API call to create file from saved blob data
        file_save_result = self.__request_file_save_data()
        
        if self.channel.check_request_for_error(file_save_result):
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
    
    #Method to upload video to LBRY
    def upload(self):
        #Checks to make sure Video is not already uploaded
        if self.__is_uploaded():
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
                if self.__is_uploaded():
                    self.update_local(use_name=True)
                    finished = True
        return result
        