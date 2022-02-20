'''
Created on Feb 14, 2022

@author: tiff
'''
import youtube
import config
import os



settings = config.Settings(f"{os.getcwd()}\\test")


test = youtube.Channel(settings).videos()

print(len(test))