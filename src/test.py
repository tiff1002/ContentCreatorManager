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

lbry = contentcreatormanager.platform.lbry.LBRY(settings=settings, ID='5e79dc0b3a00f643a0a964c87538ae2d66ddbbed')

vid = contentcreatormanager.media.video.lbry.LBRYVideo(lbry_channel=lbry, ID='83c4aeffed289b5c4d01018088c7e1c6f34396d2')
vid.download()