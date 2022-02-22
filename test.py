'''
Created on Feb 14, 2022

@author: tiff
'''
import config
import os
import lbry
import json
import youtube
import requests
import content

def json_print(value):
    print(json.dumps(value, sort_keys=True, indent=4))

settings = config.Settings(os.path.join(os.getcwd(),"test"))

yt_channel = youtube.Channel(settings=settings)
lbry_channel = lbry.Channel(settings=settings, claim_id='8be45e4ba05bd6961619489f6408a0dc62f4e650')

compare = content.lbry_youtube_channel_compare(lbry_channel, yt_channel)
print("Missing from lbry:")
for x in compare['lbry']['missing']:
    print(x.title)
print("Missing from youtube:")
for x in compare['youtube']['missing']:
    print(x.title)
    

#video = lbry.Video(channel=lbry_channel,claim_id="1d1e00753d9998505b2fb2542827e10823cc8ef3")

#video.update_local()

#json_print(requests.post(lbry.Channel.API_URL, json={"method": "claim_list", "params": {"claim_id":"4198f52bae62b8474b2cb65f59902c8378dcad4e"}}).json())