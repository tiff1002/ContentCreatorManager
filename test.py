'''
Created on Feb 14, 2022

@author: tiff
'''
import config
import os
import lbry
import json

def json_print(value):
    print(json.dumps(value, sort_keys=True, indent=4))

settings = config.Settings(os.path.join(os.getcwd(),"test2"))


channel = lbry.Channel(settings=settings, claim_id='8be45e4ba05bd6961619489f6408a0dc62f4e650', init_vids=False)

video = lbry.Video(channel=channel,claim_id="1d1e00753d9998505b2fb2542827e10823cc8ef3")

video.update_local()

video.title = "LBRY Upload Test"
video.description = "Test upload and update with content creator manager dev project"

video.update_lbry()