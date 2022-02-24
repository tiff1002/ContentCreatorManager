'''
Created on Feb 24, 2022

@author: tiff
'''
import contentcreatormanager.media.media

class Post(contentcreatormanager.media.media.Media):
    '''
    classdocs
    '''
    #skeleton method to be overridden by Classes that extend this one
    def __post(self):
        self.logger.error("Post.__post() is a skeleton method intended to be overridden by Classes that Extend this one")

    def __init__(self, settings : contentcreatormanager.config.Settings, body : str, title : str):
        '''
        Constructor
        '''
        #Super Class constructor run to set settings and blank out ID as tweets will not store an ID
        super(Post, self).__init__(settings=settings, ID='')
        
        #Set appropriate logger
        self.logger = self.settings.Post_logger
        
        self.logger.info("Initializing Media object as a Post")
        
        #Se the properties for Posts (title, body, posted)
        self.title = title
        self.body = body
        self.posted = False #initially false as the Post has not been Posted yet :P
        
    #Overidden upload() method to call the __post() method 
    #(Note: Clases that extend this one will need to override both upload() and __post() if only __post() is overridden the Post.__post() method is called instead of its overridden one when upload() is called)
    def upload(self):
        self.__post()