'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import contentcreatormanager.platform.rumble
import contentcreatormanager.media.video.rumble


logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)


rumble_channel = contentcreatormanager.platform.rumble.Rumble(settings=settings)
rumble_video = contentcreatormanager.media.video.rumble.RumbleVideo(rumble_channel=rumble_channel, title='Video To Test Video Upload', description='with a test description', thumbnail_file_name='', video_file_name='upload_test.mp4')

rumble_channel.add_video(rumble_video)

rumble_channel.upload_all_media()