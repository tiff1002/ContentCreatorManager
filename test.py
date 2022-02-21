'''
Created on Feb 14, 2022

@author: tiff
'''
import youtube
import config
import os




settings = config.Settings(os.path.join(os.getcwd(),"test"))


test = youtube.Channel(settings)



test.download_videos()