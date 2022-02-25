'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path

import contentcreatormanager.platform.lbry
import contentcreatormanager.platform.twitter
import contentcreatormanager.platform.youtube

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)


yt = contentcreatormanager.platform.youtube.YouTube(settings=settings, init_videos=True)

'''twitter = contentcreatormanager.platform.twitter.Twitter(settings=settings)

twitter.tweet("And this is yet another Test tweet from the new class structure of content creator manager")

print(twitter.media_objects[0].posted)

lbry_channel = contentcreatormanager.platform.lbry.LBRY(settings=settings, ID='8be45e4ba05bd6961619489f6408a0dc62f4e650', init_videos=True) # test channel
#lbry_channel = contentcreatormanager.platform.lbry.LBRY(settings=settings, ID='5e79dc0b3a00f643a0a964c87538ae2d66ddbbed', init_videos=False) # prod channel

lbry_channel.media_objects[0].delete_web()

lbry_channel.media_objects[0].upload()
'''
#lbry_channel.add_video("0053AnHourSpentFailingtoPickNasweks10CLFML", "file_name", True, False, "title", "description", [], "")

#print(lbry_channel.media_objects[0].description)

#lbry_channel.media_objects[0].description = "I think the title says it all"

#lbry_channel.media_objects[0].update_web()

#lbry_channel.media_objects[0].download()

'''lbry_channel.media_objects[0].download()

print(lbry_channel.media_objects[0].sd_hash)

lbry_channel.media_objects[0].delete_web()

lbry_channel.upload_all_media()


print(lbry_channel.media_objects[0].sd_hash)


#lbry_channel.media_objects[0].delete_web()

#lbry_channel.upload_all_media()





#lbry_channel.add_video("ContentCreatorVideoTest", "upload_test.mp4", False, True, "Test Upload For Content Creator Manager", "Test description", ['testtag1','testtag2'])

print(lbry_channel.delete_media_from_web('1d1e00753d9998505b2fb2542827e10823cc8ef3'))
print(lbry_channel.upload_media('1d1e00753d9998505b2fb2542827e10823cc8ef3'))
print(lbry_channel.media_objects[0].id)'''