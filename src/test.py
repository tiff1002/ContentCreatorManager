'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import contentcreatormanager.config
import contentcreatormanager.platform.youtube
import contentcreatormanager.media.video.youtube

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)
logger = settings.Base_logger

logger.info("Starting Youtube Platform Test:")
logger.info("Creating a YouTube Platform Object without initializing videos")
yt = contentcreatormanager.platform.youtube.YouTube(settings=settings, init_videos=True)

for vid in yt.media_objects:
    print(vid.title)