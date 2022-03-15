'''
Created on Mar 15, 2022

@author: tiff
'''
import contentcreatormanager.platform.lbry as lbry_plat
import contentcreatormanager.config as config
import os.path

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

lbry = lbry_plat.LBRY(settings=settings, ID=channel_claim_id, init_videos=True)

for v in lbry.media_objects:
    v.upload_thumbnail()