"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.media.lbry as lbry_media
import os.path
import time

class LBRYTextPost(lbry_media.LBRYMedia):
    """
    classdocs
    """
    def __write_description_to_file(self):
        """
        Private Method to write the description property to a md file
        """
        if os.path.isfile(self.file):
            m=f"{self.file} already exists.  Removing before recreating it"
            self.logger.warning(m)
            os.remove(self.file)
        
        with open(self.file, 'w') as f:
            f.write(self.description)
        f.close()

    def __init__(self, lbry_channel, title : str, body : str, name : str,
                 tags : list = [], bid : float = .001, thumbnail_url : str ='',
                 languages : list = ['en']):
        """
        Constructor takes LBRY Platform object, title and body for the LBRY Post
        """
        super(LBRYTextPost, self).__init__(lbry_channel=lbry_channel,
                                           file_name='',
                                           thumbnail_url=thumbnail_url,
                                           description=body,
                                           languages=languages,
                                           permanent_url='', tags=tags,
                                           bid=bid, title=title,
                                           name=name, ID='')
        self.logger = self.settings.LBRY_logger
        
        self.logger.info("Initializing Media Object as LBRY Post Object")
        self.name = self.get_valid_name(title)
        self.file = os.path.join(os.getcwd(), f"{self.name}.md")

        self.logger.info("LBRY Post Object Initialized")
        
    def upload(self):
        """
        Method to send this post to the LBRY Channel tied to the 
        Platform object tied to the post
        """
        self.__write_description_to_file()
        
        result = self.platform.api_stream_create(name=self.name, bid=self.bid,
                                                 file_path=self.file,
                                                 title=self.title,
                                                 description=self.description,
                                                 channel_id=self.platform.id,
                                                 languages=self.languages,
                                                 tags=self.tags,
                                                 thumbnail_url=self.thumbnail_url)
        
        m=f"Setting claim_id to {result['result']['outputs'][0]['claim_id']}"
        self.logger.info(m)
        self.id = result['result']['outputs'][0]['claim_id']
        
        self.logger.info("stream_create API call complete without error")
        
        finished = False
        
        
        while not finished:
            m=f"Post {self.title} made."
            self.logger.info(m)
            m="Sleeping 1 min before checking for completion"
            self.logger.info(m)
            time.sleep(60)
            
            if self.is_uploaded():
                finished = True
                
        self.logger.info("Post made to LBRY")
        return result['result']
        