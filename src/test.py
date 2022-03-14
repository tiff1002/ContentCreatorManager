'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import contentcreatormanager.config
import contentcreatormanager.platform.lbry
import contentcreatormanager.media.video.lbry

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "sync_test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)
logger = settings.Base_logger

lbry = contentcreatormanager.platform.lbry.LBRY(settings=settings, ID='ff2c8d717c1de3c55ebd4659e2cd85e2d32209f8', init_videos=True)