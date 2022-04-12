"""
Created on Feb 24, 2022

@author: tiff
"""
import logging.config
import os.path
from threading import Thread
import contentcreatormanager.platform.youtube as yt
import contentcreatormanager.platform.lbry as lbry
import tkinter.messagebox as tk_mb

class LBRYGUIDataLoad(Thread):
    def __init__(self, settings, lbry_plat, ID = None):
        super().__init__()
        self.settings = settings
        self.logger = settings.Base_logger
        self.lbry_plat = lbry_plat
        self.ID = ID
        self.lbry_vid_not_dl = []
        self.lbry_vid_not_dl_titles = []
    
    def run(self):
        if self.lbry_plat is None:
            if self.ID is None:
                tk_mb.showerror("No ID", "No ID to initialize LBRY Platform")
                return
            self.logger.info("LBRY Platform is not initialized.  Initializing now")
            self.lbry_plat = lbry.LBRY(settings=self.settings, ID=self.ID, init_videos=True)
    
        for vid in self.lbry_plat.media_objects:
            if not os.path.isfile(vid.file):
                self.lbry_vid_not_dl.append(vid)
                self.lbry_vid_not_dl_titles.append(vid.title)
            

class YTGUICustomThumbsDownloader(Thread):
    def __init__(self, yt_plat):
        super().__init__()
        self.thumb_dir = os.path.join(os.getcwd(), 'thumbs')
        if not os.path.isdir(self.thumb_dir):
            os.mkdir(self.thumb_dir)
        self.yt_plat = yt_plat            
    def run(self):
        for vid in self.yt_plat.media_objects:
            if vid.has_custom_thumbnail:
                if not os.path.isfile(vid.thumbnail):
                    vid.download_thumb()

class YTGUIThumbGenerator(Thread):
    def __init__(self, settings, video):
        super().__init__()
        self.thumb_dir = os.path.join(os.getcwd(), 'thumbs')
        self.settings = settings
        self.logger = settings.Base_logger
        if not os.path.isdir(self.thumb_dir):
            os.mkdir(self.thumb_dir)
        self.video = video    

    def run(self):
        os.chdir(self.thumb_dir)
        
        self.logger.info(f"Generating Thumbnail for YouTube Video {self.video.title}")
        
        self.video.make_thumb()
        os.chdir(self.settings.folder_location)
        self.video.has_custom_thumbnail = True

class YTGUIThumbUploader(Thread):
    def __init__(self, settings, yt_no_custom_thumb_vids, yt_no_custom_thumb_vid_titles):
        super().__init__()
        self.settings = settings
        self.logger = settings.Base_logger
        self.thumb_dir = os.path.join(os.getcwd(), 'thumbs')
        
        self.yt_no_custom_thumb_vids = yt_no_custom_thumb_vids
        self.yt_no_custom_thumb_vid_titles = yt_no_custom_thumb_vid_titles
        
        if not os.path.isdir(self.thumb_dir):
            os.mkdir(self.thumb_dir)
        
    def run(self):
        os.chdir(self.thumb_dir)
        for vid in self.yt_no_custom_thumb_vids:
            if not vid.has_custom_thumbnail:
                vid.make_thumb()
                vid.has_custom_thumbnail = True
        
        os.chdir(self.settings.folder_location)
        
        for vid in self.yt_no_custom_thumb_vids:
            self.logger.info(f"Attempting to upload thumb for {vid.title}")
            res = vid.upload_thumb()
            if res is not None:
                self.logger.info("Thumb uploaded removing from LB list")
                self.yt_no_custom_thumb_vids.remove(vid)
                self.yt_no_custom_thumb_vid_titles.remove(vid.title)
                self.yt_custom_thumb_var.set(self.yt_no_custom_thumb_vid_titles)

class LBRYGUIUploader(Thread):
    def __init__(self, settings, lbry_upload_vids, lbry_upload_titles):
        super().__init__()
        self.logger = settings.Base_logger
        self.settings = settings
        self.lbry_upload_vids = lbry_upload_vids
        self.lbry_upload_titles = lbry_upload_titles
        
        
    def run(self):
        for vid in self.lbry_upload_vids:
            self.logger.info(f"Attempting to upload {vid.file} to LBRY")
            vid.upload()
            if vid.is_uploaded():
                self.logger.info("Video Uploaded")
                self.lbry_upload_vids.remove(vid)
                self.lbry_upload_titles.remove(vid.title)
                self.lbry_plat.add_video(vid)
            else:
                self.logger.error("LBRY Upload Failed")

class LBRYGUIDownload(Thread):
    def __init__(self, settings, vid, lbry_vid_not_dl, lbry_vid_not_dl_titles):
        super().__init__()
        self.settings = settings
        self.logger = settings.Base_logger
        self.vid = vid
        self.lbry_vid_not_dl = lbry_vid_not_dl
        self.lbry_vid_not_dl_titles = lbry_vid_not_dl_titles
        
    def run(self):
        vid_dir = os.path.join(self.settings.folder_location, 'videos')
        if not os.path.isdir(vid_dir):
            os.mkdir(vid_dir)
        self.logger.info(f"Downloading LBRY Vid {self.vid.title}")
        self.vid.download()
        if os.path.isfile(self.vid.file):
            self.logger.info("Video Downloaded")
            self.lbry_vid_not_dl.remove(self.vid)
            self.lbry_vid_not_dl_titles.remove(self.vid.title)
        else:
            self.logger.error("Can not find video file download failed")

class YTGUIDownload(Thread):
    def __init__(self, settings, vid, yt_vid_not_dl, yt_vid_not_dl_titles):
        super().__init__()
        self.settings = settings
        self.logger = settings.Base_logger
        self.vid = vid
        self.yt_vid_not_dl = yt_vid_not_dl
        self.yt_vid_not_dl_titles = yt_vid_not_dl_titles
        
    def run(self):
        vid_dir = os.path.join(self.settings.folder_location, 'videos')
        if not os.path.isdir(vid_dir):
            os.mkdir(vid_dir)
        self.logger.info(f"Downloading YT Vid {self.vid.title}")
        self.vid.download()
        if os.path.isfile(self.vid.file):
            self.logger.info("Video Downloaded")
            self.yt_vid_not_dl.remove(self.vid)
            self.yt_vid_not_dl_titles.remove(self.vid.title)
        else:
            self.logger.error("Can not find video file download failed")
        
class YTGUIDataLoad(Thread):
    def __init__(self, settings, yt_plat, yt_private_cb, yt_unlisted_cb):
        super().__init__()
        self.settings = settings
        self.logger = settings.Base_logger
        self.yt_plat = yt_plat
        self.yt_no_custom_thumb_vids = []
        self.yt_no_custom_thumb_vid_titles = []
        self.yt_vid_not_dl = []
        self.yt_vid_not_dl_titles = []
        self.yt_private_cb = yt_private_cb
        self.yt_unlisted_cb = yt_unlisted_cb
    
    def run(self):
        if self.yt_plat is None:
            self.logger.info("YouTube Platform is not initialized.  Initializing now")
            self.yt_plat = yt.YouTube(settings=self.settings, init_videos=True,private_vids=self.yt_private_cb, unlisted_vids=self.yt_unlisted_cb)
    
    
        self.logger.info("Sorting through YouTube Videos")
        
        for vid in self.yt_plat.media_objects:
            if not vid.has_custom_thumbnail:
                self.logger.info(f"{vid.title} {vid.id} has no custom thumbnail")
                self.yt_no_custom_thumb_vids.append(vid)
                self.yt_no_custom_thumb_vid_titles.append(vid.title)
                self.yt_custom_thumb_var.set(self.yt_no_custom_thumb_vid_titles)
            else:
                self.logger.info(f"{vid.title} {vid.id} Already has a custom Thumbnail")
            if not os.path.isfile(vid.file):
                self.logger.info(f"{vid.title} not found locally")
                self.yt_vid_not_dl.append(vid)
                self.yt_vid_not_dl_titles.append(vid.title)
                self.yt_vid_not_var.set(self.yt_vid_not_dl_titles)

class Settings(object):
    """
    classdocs
    """
    def __init__(self, folder_location : str, logging_config_file : str):
        """
        Constructor
        """
        self.folder_location = folder_location
        self.original_dir = os.getcwd()
        os.chdir(self.folder_location)
        
        logging.config.fileConfig(logging_config_file)
        self.logger = logging.getLogger('SettingsLogger')
        self.root_logger = logging.getLogger()
        
        self.YouTube_logger = logging.getLogger('YouTubeLogger')
        self.LBRY_logger = logging.getLogger('LBRYLogger')
        self.Rumble_logger = logging.getLogger('RumbleLogger')
        self.Base_logger = logging.getLogger('BaseLogger')
        self.Twitter_logger = logging.getLogger('TwitterLogger')
        self.Reddit_logger = logging.getLogger('RedditLogger')
        self.Facebook_logger = logging.getLogger('FacebookLogger')
        self.Minds_logger = logging.getLogger('MindsLogger')
        self.Instagram_logger = logging.getLogger('InstagramLogger')
        self.Media_logger = logging.getLogger('MediaLogger')
        self.Platform_logger = logging.getLogger('PlatformLogger')
        self.Video_logger = logging.getLogger('VideoLogger')
        self.Post_logger = logging.getLogger('PostLogger')
        self.logger.info("Loggers initialized")

