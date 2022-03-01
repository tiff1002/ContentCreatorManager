'''
Created on Feb 28, 2022

@author: tiff
'''
import contentcreatormanager.media.media
import os.path

class LBRYMedia(contentcreatormanager.media.media.Media):
    '''
    classdocs
    '''
    def __init__(self, lbry_channel, file_name : str = "", thumbnail_url : str = '', description : str = "", languages : list = ['en'], 
                 permanent_url : str = '', tags : list = [], bid : str = "0.001", title : str = '', name : str = "", ID : str=''):
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
        