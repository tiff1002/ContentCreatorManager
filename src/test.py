'''
Created on Mar 15, 2022

@author: tiff
'''
import contentcreatormanager.config as config
import contentcreatormanager.platform.youtube as yt_plat
import os.path
settings = config.Settings(folder_location=os.path.join(os.getcwd(), 'test'), logging_config_file='logging.ini')
yt = yt_plat.YouTube(settings=settings, init_videos=True)

yt.media_objects[5].download_thumb()