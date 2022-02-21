'''
Created on Feb 14, 2022

@author: tiff
'''
import youtube
import config
import os
import pytube



settings = config.Settings(f"{os.getcwd()}\\test")


test = pytube.YouTube('https://www.youtube.com/watch?v=cHV0V_mEbMU', use_oauth=True)



def download():
    video_file = test.streams.order_by('resolution').desc().first().download(filename_prefix="video_")
    
        
download()