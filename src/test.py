'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import contentcreatormanager.platform.youtube


logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)


yt = contentcreatormanager.platform.youtube.YouTube(settings=settings, init_videos=True)

for v in yt.media_objects:
    print(v.title)
    
print(f"There are {len(yt.media_objects)} uploads to this YouTube")