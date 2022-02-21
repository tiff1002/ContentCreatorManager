'''
Created on Feb 14, 2022

@author: tiff
'''
import youtube
import config
import os




settings = config.Settings(os.path.join(os.getcwd(),"test"))


channel = youtube.Channel(settings)

test = youtube.Video(channel=channel, new_video=True, description="upload test description", tags=['test1', 'test2'], self_declared_made_for_kids=False, category_id=22, privacy_status="private", title='upload_test')



test.upload()

test.update_from_web()

print(f"videos ID is {test.id}")

test.description = "New test upload description"

test.update_to_web()