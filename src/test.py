'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import contentcreatormanager.config
import contentcreatormanager.platform.youtube
import contentcreatormanager.media.video.youtube

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)
logger = settings.Base_logger

logger.info("Starting Youtube Platform Test:")
logger.info("Creating a YouTube Platform Object without initializing videos")
yt = contentcreatormanager.platform.youtube.YouTube(settings=settings, init_videos=False)

logger.info("Creating YouTube Video Object to add to Platform object to test add_media and add_video")
vid2 = contentcreatormanager.media.video.youtube.YouTubeVideo(channel=yt, privacy_status='private', title="The Upload Test Via Content Creator Manager", description="THe super test description for the test upload", file_name="upload_test.mp4", update_from_web=False, tags=['testtag'], new_video=True)


logger.info("Testing add_video")
yt.add_video(vid2)


logger.info("Testing upload_all_media")
yt.upload_all_media()


logger.info("Testing delete_media_from_web")

yt.delete_media_from_web(vid2.id)

logger.info("Re-uploading for further tests")

vid2.upload()


vid2.title = "The new and improved title"

logger.info("Changing a title now testing update_all_media_local")

yt.update_all_media_local()


logger.info(f"if the title you see here is not The new and improved title it worked: {vid2.title}")

vid2.title = "The new and improved title"

logger.info("Changing a title now testing update_all_media_web (running update_all_media_local again after just to confirm change hit the web)")

yt.update_all_media_web()


yt.update_all_media_local()



logger.info(f"if the title is the new and improved title it worked: {vid2.title}")

vid2.title = "The second new and improved title"

logger.info("Testing update_media_local")

yt.update_media_local(vid2.id)


logger.info(f"If it worked this will not be the second new and improved title: {vid2.title}")

vid2.title = "The second new and improved title"

logger.info("Testing update_media_web")

yt.update_media_web(vid2.id)


logger.info(f"If it worked this will be the second new and improved title: {vid2.title}")

logger.info("Testing download_media so first deleting file")

os.remove(vid2.file)

yt.download_media(vid2.id)


logger.info("Testing download_all_media so first deleting file")

os.remove(vid2.file)

yt.download_all_media()


logger.info("YouTube Platform Test over")