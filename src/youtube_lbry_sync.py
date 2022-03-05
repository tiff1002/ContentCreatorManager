'''
Created on Mar 4, 2022

@author: tiff
'''
import contentcreatormanager.media.video.youtube as yt_vid
import contentcreatormanager.media.video.lbry as lbry_vid
import contentcreatormanager.platform.youtube as yt_plat
import contentcreatormanager.platform.lbry as lbry_plat
import contentcreatormanager.config as ccm_config
import os.path

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "sync_test")

settings = ccm_config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)

youtube = yt_plat.YouTube(settings=settings, init_videos=True, current_quota_usage=0)
lbry = lbry_plat.LBRY(settings=settings, ID='5e79dc0b3a00f643a0a964c87538ae2d66ddbbed', init_videos=True)

youtube_not_lbry = []
lbry_not_youtube = []
youtube_to_dl = []
lbry_to_dl = []

for yvid in youtube.media_objects:
    in_lbry = False
    for lvid in lbry.media_objects:
        #settings.Base_logger.info(f"Checking {lvid.title} against {yvid.title}")
        if lvid.title == yvid.title:
            #settings.Base_logger.info("They are the same")
            in_lbry = True
    if not in_lbry:
        #settings.Base_logger.info(f"Adding {yvid.title} since it is not on LBRY")
        if yvid.privacy_status != 'private':
            youtube_not_lbry.append(yvid)
        
for lvid in lbry.media_objects:
    in_yt = False
    for yvid in youtube.media_objects:
        #settings.Base_logger.info(f"Checking {lvid.title} against {yvid.title}")
        if yvid.title == lvid.title:
            #settings.Base_logger.info("They are the same")
            in_yt = True
    if not in_yt:
        #settings.Base_logger.info(f"Adding {yvid.title} since it is not on LBRY")
        lbry_not_youtube.append(lvid)
        
for v in youtube_not_lbry:
    if not v.is_downloaded():
        youtube_to_dl.append(v)
        
for v in lbry_not_youtube:
    if not v.is_downloaded():
        lbry_to_dl.append(v)

for v in lbry_to_dl:
    v.download()
    
for v in youtube_to_dl:
    v.download()
    
for v in lbry_not_youtube:
    yvid = yt_vid.YouTubeVideo(channel=youtube, self_declared_made_for_kids=False, made_for_kids=False, public_stats_viewable=True, embeddable=True, privacy_status='unlisted', title=v.title, description=v.description, file_name=os.path.basename(v.file), update_from_web=False, tags=v.tags, new_video=True)
    youtube.add_media(yvid)
    yvid.upload()

for v in youtube_not_lbry:
    lvid = lbry_vid.LBRYVideo(lbry_channel=lbry, tags=v.tags, title=v.title, file_name=os.path.basename(v.file), description=v.description)
    lbry.add_media(lvid)
    lvid.upload()


    