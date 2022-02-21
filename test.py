'''
Created on Feb 14, 2022

@author: tiff
'''
import youtube
import config
import content
import os




settings = config.Settings(os.path.join(os.getcwd(),"test"))


channel = youtube.Channel(settings, init_vids=False)

test = youtube.Video(channel=channel, video_id="j61rqh2q6Kg")



test.update_from_web()


if not test.check_thumb():
    test.upload_thumbnail()
    
if test.check_thumb():
    print("Tears of Joy")