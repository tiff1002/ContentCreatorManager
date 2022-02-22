'''
Created on Feb 14, 2022

@author: tiff
'''
import youtube
import config
import content
import os
import lbry
import json

def json_print(value):
    print(json.dumps(value, sort_keys=True, indent=4))

settings = config.Settings(os.path.join(os.getcwd(),"test"))


channel = lbry.Channel(settings=settings, claim_id='5e79dc0b3a00f643a0a964c87538ae2d66ddbbed')

print(len(channel.videos))