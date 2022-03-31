"""
Created on Feb 24, 2022

@author: tiff
"""
import shortuuid
import os.path
import ffmpeg
from PIL import ImageChops

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
        self.file = None
        
        if self.id == '' or self.id is None:
            self.set_unique_id()
        
        self.title = ''
        self.tags = []
        self.description = ''
        
        self.thumbnail = os.path.join(os.getcwd(), self.get_valid_thumbnail_file_name())
    
    def compare_thumbs(self, other_obj):
        """
        Method to compare thumbnails for two objects
        """
        thumb1 = self.thumbnail
        thumb2 = other_obj.thumbnail
        return ImageChops.difference(thumb1, thumb2).getbbox() is None
    
    def make_thumb(self):
        """
        Method to make a thumbnail file
        """
        self.logger.info("Attempting to Generate Thumbnail file from video")
        step_one = ffmpeg.input(self.file)
        step_two = step_one.filter('scale')
        step_three = step_two.output(self.get_valid_thumbnail_file_name(),
                                     vframes=1)
        step_four = step_three.overwrite_output()
        result = step_four.run(capture_stdout=False,capture_stderr=False)
        return result
    
    def get_valid_thumbnail_file_name(self, desired_file_name : str = ''):
        """
        Method to get a valid thumbnail filename either from title property or
        provided string.
        """
        v='`~!@#$%^&+=,-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        valid_chars = v
        
        if desired_file_name == '':    
            getVals = list([val for val in f"{self.title}.jpg" if val in valid_chars])
        else:
            if desired_file_name[-4:] == '.jpg':
                file_name = desired_file_name[:-4]   
            else:
                file_name = desired_file_name 
            getVals = list([val for val in f"{file_name}.jpg" if val in valid_chars])
    
        return "".join(getVals)
    
    def is_downloaded(self):
        """
        Method to determine if the Video Object is downloaded
        """
        return os.path.isfile(self.file)
        
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
        Method to set id property to a unique string. 
        The ID string can be provided, but if it is
        not a random one is generated
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
        Method intended to be overridden to upload the
        Media Object to the Platform it is tied to
        """
        m="Media.upload() is a skeleton method should be overridden"
        self.logger.error(m)
    
    def update_web(self):
        """
        Method intended to be overridden to update the
        Media Object's details on the Platform it is tied to
        """
        m="Media.update_web() is a skeleton method should be overridden"
        self.logger.error(m)
        
    def update_local(self):
        """
        Method intended to be overridden to update the Media Object's
        local details based on the details on the Platform it is tied to
        """
        m="Media.update_local() is a skeleton method should be overridden"
        self.logger.error(m)
        
    def delete_web(self):
        """
        Method intended to be overridden to remove the
        Media Object from the Platform it is tied to
        """
        m="Media.delete_web() is a skeleton method should be overridden"
        self.logger.error(m)
        
    def download(self):
        """
        Method intended to be overridden to download the
        Media Object from the Platform it is tied to
        """
        m="Media.download() is a skeleton method should be overridden"
        self.logger.error(m)
        
    def is_uploaded(self):
        """
        Method intended to be overridden to check if the
        Media Object is uploaded to the Platform it is tied to
        """
        m="Media.is_uploaded() is a skeleton method should be overridden"
        self.logger.error(m)