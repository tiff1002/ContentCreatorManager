'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import contentcreatormanager.platform.youtube
import contentcreatormanager.platform.twitter
import contentcreatormanager.platform.lbry
import contentcreatormanager.platform.rumble
import contentcreatormanager.media.video.rumble
import contentcreatormanager.media.video.youtube
import contentcreatormanager.platform.facebook
import contentcreatormanager.platform.reddit

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)

#fb = contentcreatormanager.platform.facebook.Facebook(settings=settings)

#reddit = contentcreatormanager.platform.reddit.Reddit(settings=settings)

#reddit.post(subr='lbry', title='One More Test Post From Content Creator Manager', body="Sorry for the noise here is the latest update: https://odysee.com/@TechGirlTiff:5/ContentCreatorManager_Dev_Project_Update_00004:4")

#test = fb.post("Test Post")

#print(test)

'''
yt = contentcreatormanager.platform.youtube.YouTube(settings=settings, init_videos=True)

#yvid = contentcreatormanager.media.video.youtube.YouTubeVideo(channel=yt, self_declared_made_for_kids=False, made_for_kids=False, public_stats_viewable=True, embeddable=True, privacy_status='unlisted', title='THis is a unlisted video for content creator manager', description='initial description', file_name='upload_test.mp4', update_from_web=False, tags=['initialtag'], new_video=True)

#yt.add_video(yvid)

yvid = yt.get_media("9tHc0FDjE80")

yvid.privacy_status = 'unlisted'

yvid.title = "This is a cool upload from Content Creator Manager"

yvid.description = "This is a cool new description"

yvid.add_tag("newtesttag1")
yvid.add_tag("Anotherone")

#yvid.upload()

yvid.description = "We have to modify it tho"

yvid.update_web()
'''
lbry = contentcreatormanager.platform.lbry.LBRY(ID='8be45e4ba05bd6961619489f6408a0dc62f4e650', settings=settings, init_videos=True)
vid = lbry.get_media("9df6f11c4581dc4deb48246582c638e4c7576af2")
post = lbry.make_post(title="Another Test LBRY Post About Test Video", body=f"This is a test post so it may as well talk about a test video {vid.title} at {vid.permanent_url}", tags=['testposttag'])

print(post.file)
print(post.description)
print(post.id)


'''
rumble = contentcreatormanager.platform.rumble.Rumble(settings=settings)

rvid = contentcreatormanager.media.video.rumble.RumbleVideo(rumble_channel=rumble, title="Test Upload From Content Creator Manager", description="With its very own test description", video_file_name='upload_test.mp4', license_type=0)

rumble.add_video(rvid)

rumble.upload_all_media()

twitter = contentcreatormanager.platform.twitter.Twitter(settings=settings)

twitter.tweet("If this gets tweeted that means lunch time testing worked and things are going smoothly.")'''