'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import contentcreatormanager.config
import contentcreatormanager.platform.lbry

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)
logger = settings.Base_logger

logger.info("Starting LBRY Platform Test:")
logger.info("Creating a LBRY Platform Object of main channel initializing videos")
lbry_main = contentcreatormanager.platform.lbry.LBRY(settings=settings, init_videos=True, ID='5e79dc0b3a00f643a0a964c87538ae2d66ddbbed')

for vid in lbry_main.media_objects:
    print(vid.title)
    
logger.info("Creating LBRY Platform object for test channel")



print(vid.title)