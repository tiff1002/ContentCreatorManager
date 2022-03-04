'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import contentcreatormanager.config
import contentcreatormanager.platform.rumble
import contentcreatormanager.media.video.rumble

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)
logger = settings.Base_logger

rumble = contentcreatormanager.platform.rumble.Rumble(settings=settings)

vid = contentcreatormanager.media.video.rumble.RumbleVideo(rumble_channel=rumble, title='Test Title', description='Test Description',video_file_name='upload_test.mp4', license_type=0)

print(vid.id)
print(vid.guid)

rumble.add_media(vid)

rumble.upload_all_media()

print(vid.id)
print(vid.guid)
print(vid.url)