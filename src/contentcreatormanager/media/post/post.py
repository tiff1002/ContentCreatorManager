"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.media.media as media
import contentcreatormanager.platform.platform as plat

class Post(media.Media):
    """
    classdocs
    """
    def __init__(self, platform : plat.Platform, body : str, title : str,
                 posted : bool = False):
        """
        Constructor for generic post to set the settings, body of the 
        post and title.  It will also initialize posted to False
        """
        super().__init__(platform=platform, ID='')
        
        self.logger = self.settings.Post_logger
        
        self.logger.info("Initializing Media object as a Post")
        
        self.title = title
        self.body = body
        self.uploaded = posted