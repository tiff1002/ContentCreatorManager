'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import requests
import contentcreatormanager.media.lbry
import time
import shutil

class LBRYVideo(contentcreatormanager.media.lbry.LBRYMedia):
    '''
    classdocs
    '''  
    def __upload_new_video(self):
        """
        Private Method for uploading a new video to LBRY.  This uses the stream_create api call.  This method will also set the id to the new claim_id from the upload.
        This method just makes the API call and does nothing to confirm it worked or is complete.
        """
        #Make stream_create API call with params
        result = self.platform.api_stream_create(name=self.name, bid=self.bid, file_path=self.file, title=self.title, description=self.description, channel_id=self.platform.id, languages=self.languages, tags=self.tags, thumbnail_url=self.thumbnail_url)
        
        #Setting claim_id returned by the API call
        self.logger.info(f"Setting claim_id to {result['result']['outputs'][0]['claim_id']}")
        self.id = result['result']['outputs'][0]['claim_id']
        
        self.logger.info("stream_create API call complete without error")
        return result['result']

    def __init__(self, lbry_channel, ID : str = '', tags : list = [], title : str = '',file_hash : str = '', file_name : str = '', name : str = '', 
                 thumbnail_url : str = '', bid : float = .001, address : str = '', description : str = '', permanent_url : str = '', 
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
            self.update_from_request(request)
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
    
    def download(self):
        """
        Method to download Video from LBRY to local machine.  This will call get to download blobs, file_save to make a file from the 
        blobs and then if the file is in the wrong location (due to LBRY API weirdness) this Method will put it in the right place
        """
        #Making API call to download the blob data
        get_result = self.platform.api_get(uri=self.permanent_url, download_directory=self.settings.folder_location, file_name=os.path.basename(self.file))
        
        
        #get streaming_url from results of the api call
        try:
            streaming_url = get_result['result']['streaming_url']
        except KeyError as e:
            if e.args[0] == 'streaming_url':
                self.logger.error("The Video You are trying to download is either not on LBRY or is not on LBRY yet")
                return 'get_error'
            else:
                raise e
        
        self.logger.info(f"running a request on streaming_url: {streaming_url} to wait for blobs to finish downloading")
        requests.get(streaming_url)
        
        #prevent extra copies of the file being created
        if os.path.isfile(self.file):
            os.remove(self.file)
        
        #Make API call to create file from saved blob data
        file_save_result = self.platform.api_file_save(claim_id=self.id, download_directory=self.settings.folder_location, file_name=os.path.basename(self.file))
        
        actual_file_path = file_save_result['result']['download_path']
        desired_file_path = self.file
        
        #If the file is already where we want it return the results and be done with it
        if actual_file_path == desired_file_path:         
            return get_result
        #Otherwise try moving it to where we want it
        shutil.move(actual_file_path, desired_file_path, copy_function = shutil.copy2)
        
    
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
        result = self.__upload_new_video()
        
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