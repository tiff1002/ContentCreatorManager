"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.media.media as media
import os.path
import ffmpeg

class Video(media.Media):
    """
    classdocs
    """
    MAX_RETRIES = 25

    def __init__(self, platform, ID : str = '', file_name : str = '',
                 title : str = "", description : str = "",
                 thumbnail_file_name : str = ''):
        """
        Constructor takes Platform object and ID, file_name, title,
        description, and thumbnail_file_name string.  The Strings
        are all optional but ID or file_name must be provided
        """
        if ID == '' and file_name == '':
            m="You must set either the file_name or ID to create a Video"
            platform.settings.Video_logger.error(m)
            raise Exception()
        
        super(Video, self).__init__(platform=platform, ID=ID)
        
        self.logger = self.settings.Video_logger
        self.logger.info("Initializing Media Object as a Video object")
        
        vid_dir = os.path.join(os.getcwd(), 'videos')
        if file_name == '':
            self.file = os.path.join(vid_dir, self.get_valid_video_file_name())
        else:
            self.file = os.path.join(vid_dir, file_name)
        self.thumbnail = os.path.join(os.getcwd(),
                                      self.get_valid_thumbnail_file_name(thumbnail_file_name))
        
        file_does_not_exist = not os.path.isfile(self.file)
        
        if file_does_not_exist and ID == '':
            m=f"no file found for file_name {file_name} and no ID set"
            self.logger.error(m)
        
        self.title = title
        self.description = description
    
    def is_downloaded(self):
        """
        Checks for downloaded file
        """
        return media.Media.is_downloaded(self)
    
    def make_thumb(self):
        """
        Method to create a Thumbnail File from video file
        """
        return media.Media.make_thumb(self)
    
    def get_valid_video_file_name(self, desired_file_name : str = ''):
        """
        Method to get a valid video filename either from title property
        or provided string.
        """
        v='`~!@#$%^&+=,-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        valid_chars = v
        file_name = desired_file_name
        if desired_file_name[-4:] == '.mp4':
            self.logger.info("file name given already has .mp4 in it")
            file_name = desired_file_name[:-4]
        if desired_file_name == '':
            file_name = self.title    
        
        getVals = list([val for val in f"{file_name}.mp4" if val in valid_chars])
        
        result = "".join(getVals)
        
        self.logger.info(f"returning the following file name: {result}")
            
        return result
    
    def combine_audio_and_video_files(self, video_file, audio_file):
        """
        Method to combine given audio and video file using FFMPEG
        """
        self.logger.info(f"Using FFMPEG to download {self.file}")
        file_name = os.path.basename(self.file)
        
        audFile = None
        vidFile = None
        source_audio = None
        source_video = None
        
        finished = False
        tries = 0
        while not finished and tries < Video.MAX_RETRIES + 2:
            try:
                m="Attempting to prep source audio and video to merge"
                self.logger.info(m)
                source_audio = ffmpeg.input(audio_file)
                source_video = ffmpeg.input(video_file)
                audFile = self.getInputFilename(source_audio)
                vidFile = self.getInputFilename(source_video)
                finished = True
            except Exception as e:
                if tries > self.MAX_RETRIES:
                    m="Too many failed attempts.  Raising new exception"
                    self.logger.error(m)
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                m=f"{tries} tries of a possible {Video.MAX_RETRIES}"
                self.logger.info(m)
                finished = False
        
        m=f"Attempting to merge {vidFile} and {audFile} as {file_name}"
        self.logger.info(m)
        finished = False
        tries = 0
        
        while not finished and tries < self.MAX_RETRIES + 2:
            try:
                self.logger.info("Attempting to merge audio and video")
                ffmpeg.concat(source_video, 
                              source_audio, 
                              v=1, a=1).output(self.file).run()
                finished = True
            except Exception as e:
                if tries > self.MAX_RETRIES:
                    m="Too many failed download attempts raising new exception"
                    self.logger.error(m)
                    raise Exception()
                self.logger.error(f"got error:\n{e}\nGoing to try again")
                tries += 1
                m=f"{tries} tries of a possible {Video.MAX_RETRIES}"
                self.logger.info(m)
                finished = False
                
        self.logger.info(f"Files merged as {file_name}")
        
        self.logger.info("Cleaning up source files....")
        self.logger.info(f"Removing {audFile}")
        os.remove(audFile)
        self.logger.info(f"Removing {vidFile}")
        os.remove(vidFile)
    
    def is_thumb_downloaded(self):
        """
        Method to determine if the Video Object's thumbnail file is downloaded
        """
        return os.path.isfile(self.thumbnail)
    
    def is_uploaded(self):
        """
        Method to return True if the video is uploaded to its platform and
        False otherwise.  This is intended to be overridden by Classes that
        extend this one
        """
        m="This is a skeleton method to be overridden and does nothing"
        self.logger.warning(m)