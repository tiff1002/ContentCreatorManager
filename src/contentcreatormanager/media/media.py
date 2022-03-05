"""
Created on Feb 24, 2022

@author: tiff
"""
import shortuuid

class Media(object):
    """
    classdocs
    """


    def __init__(self, platform, ID : str):
        """
        Constructor takes a Settings Object and an ID in the form of a string
        """
        self.settings = platform.settings
        self.logger = self.settings.Media_logger
        self.platform = platform
        
        self.logger.info(f"Initializing Media Object with id {ID}")
        self.id = ID
        self.uploaded = False
        
        if self.id == '' or self.id is None:
            self.set_unique_id()
        
        self.title = ''
        self.tags = []
        self.description = ''
        
    def getInputFilename(self, stream):
        """
        Method to get the filename from a ffmpeg.input stream
        """
        while stream.node._KwargReprNode__incoming_edge_map != {}:
            stream = stream.node._KwargReprNode__incoming_edge_map[None][0]
            if not hasattr(stream, 'node'):
                return stream.__dict__['kwargs']['filename']
        return stream.node.__dict__['kwargs']['filename']
    
    def set_unique_id(self, ID=None):
        """
        Method to set id property to a unique string.  The ID string can be provided, but if it is not a random one is generated
        """
        if ID is None:
            self.id = shortuuid.uuid()
            self.logger.info(f"Object is set to random unique ID ({self.id})")
        else:
            self.logger.info(f"ID provided setting object id to {ID}")
            self.id = ID
       
    def add_tag(self, tag : str):
        """
        Method to add a single tag to the tags property of the Media Object
        """
        self.tags.append(tag)
        
    def upload(self):
        """
        Method intended to be overridden to upload the Media Object to the Platform it is tied to
        """
        self.logger.error("Media.upload() is a skeleton method intended to be overridden by Classes that Extend this one")
    
    def update_web(self):
        """
        Method intended to be overridden to update the Media Object's details on the Platform it is tied to
        """
        self.logger.error("Media.update_web()This is a skeleton method intended to be overridden by Classes that Extend this one") 
    
    def update_local(self):
        """
        Method intended to be overridden to update the Media Object's local details based on the details on the Platform it is tied to
        """
        self.logger.error("Media.update_local() is a skeleton method intended to be overridden by Classes that Extend this one") 
    
    def delete_web(self):
        """
        Method intended to be overridden to remove the Media Object from the Platform it is tied to
        """
        self.logger.error("Media.delete_web() is a skeleton method intended to be overridden by Classes that Extend this one")
    
    def download(self):
        """
        Method intended to be overridden to download the Media Object from the Platform it is tied to
        """
        self.logger.error("Media.download() is a skeleton method intended to be overridden by Classes that Extend this one")
        
    def is_uploaded(self):
        """
        Method intended to be overridden to check if the Media Object is uploaded to the Platform it is tied to
        """
        self.logger.error("Media.is_uploaded() is a skeleton method intended to be overridden by Classes that Extend this one")