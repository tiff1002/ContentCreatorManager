#!/usr/bin/env python3
'''
Created on Mar 11, 2022

@author: tiff
'''

import contentcreatormanager.platform.lbry as lbry_plat
import contentcreatormanager.config as config
import contentcreatormanager.media.video.lbry as lbry_vid
import os

folder = input("Enter Folder Location:")

settings = config.Settings(logging_config_file='logging.ini', folder_location=folder)



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

lbry = lbry_plat.LBRY(settings=settings, ID=channel_claim_id, init_videos=False)

bid = input("Please enter default bid:")

bid = float(bid)

description = input("If you would like a stock description for all videos enter it now:")

lic = input("Please Enter the name of the license for the content:")

license_url = input("Please enter a URL for the license:")

adding_tags = True
tags = []

while adding_tags:
    tag = input("Enter Tag:")
    another_tag = input("Would you like to add another tag?(y/n):")
    if not ('y' in another_tag or 'Y' in another_tag):
        adding_tags = False
    tags.append(tag)
    if not adding_tags:
        print(f"You are about to quit adding tags.  Here they are so far:\n{tags}")
        sure = input("Are you sure you are done?(y/n):")
        if not ('y' in sure or 'Y' in sure):
            adding_tags = True

files = os.listdir('.')

mp4_files = []

for f in files:
    if f[-4:] == '.mp4':
        mp4_files.append(f)

for v in mp4_files:
    lbry_video = lbry_vid.LBRYVideo(lbry_channel=lbry,title=v[:-4],tags=tags,file_name=v,name=v[:-4],bid=bid,description=description,new_video=True,lic=lic,license_url=license_url)
    
    lbry.add_video(lbry_video)
    
count = 1

for v in lbry.media_objects:
    print(f"\nVideo {count}")
    print(f"file: {v.file}")
    print(f"name: {v.name}")
    print(f"title: {v.title}")
    print(f"description: {v.description}")
    print(f"tags: {v.tags}")
    print(f"license: {v.license}")
    print(f"license url: {v.license_url}")
    print(f"bid: {v.bid}\n")
    count += 1
    
upload = False

should_upload = input("Would you like to make the uploads listed above(y/n)?")

if not ('n' in should_upload or 'N' in should_upload):
    if 'y' in should_upload or 'Y' in should_upload:
        upload = True
        
if upload:
    print("Starting upload")
    for v in lbry.media_objects:
        v.upload_thumbnail(update_video=False)
    lbry.upload_all_media()