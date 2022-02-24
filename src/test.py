'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path

import contentcreatormanager.platform.twitter

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)

twitter = contentcreatormanager.platform.twitter.Twitter(settings=settings)

twitter.tweet("And another Test tweet from the new class structure of content creator manager")

print(twitter.media_objects[0].posted)

#lbry_channel = contentcreatormanager.platform.lbry.LBRY(settings=settings, ID='5e79dc0b3a00f643a0a964c87538ae2d66ddbbed', init_videos=True)

#print(lbry_channel.description)