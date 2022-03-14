#!/usr/bin/env python3
'''
Created on Mar 14, 2022

@author: tiff
'''
import contentcreatormanager.platform.lbry as lbry_plat
import contentcreatormanager.config as config
import contentcreatormanager.media.video.lbry as lbry_vid
import os.path
import contentcreatormanager.platform.youtube as yt_plat
import contentcreatormanager.media.video.youtube as yt_vid


settings = config.Settings(logging_config_file='logging.ini', folder_location=os.getcwd())



channels = lbry_plat.claim_list(claim_type=['channel'])

print(channels['result']['items'][0]['name'])
count = 1
choices = {}
for channel in channels['result']['items']:
    print(f"{count}. {channel['name']}")
    choices[f'{count}'] = channel
    count += 1

choice = input("Pick the channel you want to upload to (Just enter the number next to it above):")

while not (choice in choices):
    print(f"You entered {choice} which is not one of the options")
    choice = input("Pick the channel you want to upload to (Just enter the number next to it above):")
    
channel_claim_id = choices[choice]['claim_id']

lbry = lbry_plat.LBRY(settings=settings, ID=channel_claim_id, init_videos=True)

youtube = yt_plat.YouTube(settings=settings, init_videos=True)

on_both = []

for yvid in youtube.media_objects:
    for lvid in lbry.media_objects:
        if lvid.title == yvid.title:
            on_both.append({'yt':yvid,'lbry':lvid})
            
for vids in on_both:
    vids['lbry'].thumbnail_url = vids['yt'].get_thumb_url()
    vids['lbry'].logger.info(f"Setting Thumbnail url for {vids['lbry'].title} to {vids['lbry'].thumbnail_url}")
    
lbry.update_all_media_web()