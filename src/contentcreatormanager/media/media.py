'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.config

class Media(object):
    '''
    classdocs
    '''


    def __init__(self, settings : contentcreatormanager.config.Settings, ID : str):
        '''
        Constructor
        '''
        #Set the settings and apropriate logger for the object
        self.settings = settings
        self.logger = settings.Media_logger
        
        #Set id property
        self.logger.info(f"Initializing Media Object with id {ID}")
        self.id = ID
        
        self.title = ''
        self.tags = []
        self.description = ''
        
    def getInputFilename(self, stream):
        while stream.node._KwargReprNode__incoming_edge_map != {}:
            stream = stream.node._KwargReprNode__incoming_edge_map[None][0]
            if not hasattr(stream, 'node'):
                return stream.__dict__['kwargs']['filename']
        return stream.node.__dict__['kwargs']['filename']
    
    #Method to add a single tag to Media Object    
    def add_tag(self, tag : str):
        self.tags.append(tag)
        
    #skeleton method to be overridden by Classes that extend this one
    def upload(self):
        self.logger.error("Media.upload() is a skeleton method intended to be overridden by Classes that Extend this one")
    
    #skeleton method to be overridden by Classes that extend this one
    def update_web(self):
        self.logger.error("Media.update_web()This is a skeleton method intended to be overridden by Classes that Extend this one") 
    
    #skeleton method to be overridden by Classes that extend this one
    def update_local(self):
        self.logger.error("Media.update_local() is a skeleton method intended to be overridden by Classes that Extend this one") 
    
    #skeleton method to be overridden by Classes that extend this one
    def delete_web(self):
        self.logger.error("Media.delete_web() is a skeleton method intended to be overridden by Classes that Extend this one")
    
    #skeleton method to be overridden by Classes that extend this one
    def download(self):
        self.logger.error("Media.download() is a skeleton method intended to be overridden by Classes that Extend this one")