'''
Created on Mar 4, 2022

@author: tiff
'''

import contentcreatormanager.platform.youtube
import contentcreatormanager.platform.lbry
import contentcreatormanager.config
import os.path

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "sync_test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)

youtube = contentcreatormanager.platform.youtube.YouTube(settings=settings, init_videos=True, current_quota_usage=45)
lbry = contentcreatormanager.platform.lbry.LBRY(settings=settings, ID='5e79dc0b3a00f643a0a964c87538ae2d66ddbbed', init_videos=True)

youtube_not_lbry = []
lbry_not_youtube = []

for yvid in youtube.media_objects:
    in_lbry = False
    for lvid in lbry.media_objects:
        if lvid.title == yvid.title:
            in_lbry = True
    if not in_lbry:
        youtube_not_lbry.append(yvid)
        
for lvid in lbry.media_objects:
    in_yt = False
    for yvid in youtube.media_objects:
        if lvid.title == yvid.title:
            in_yt = True
    if not in_yt:
        lbry_not_youtube.append(yvid)
print()
print()
print()
print()
print("Found the following in Youtube but not LBRY:")
for vid in youtube_not_lbry:
    print(vid.title)
    
print()
print()
print()
print()
print("Found the following in LBRY but not YouTube:")
for vid in lbry_not_youtube:
    print(vid.title)
    
running = True

#while running:
    
    
print(f"Current Quota usage: {youtube.quota_usage}")