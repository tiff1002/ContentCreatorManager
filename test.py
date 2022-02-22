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

test = youtube.Video(channel=channel, video_id="uFEOds5gfVo")

test.update_from_web()

test.download(overwrite=True)