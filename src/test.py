'''
Created on Feb 24, 2022

@author: tiff
'''
import os.path
import contentcreatormanager.config
import contentcreatormanager.platform.reddit

logging_config_file = os.path.join(os.getcwd(), "logging.ini")
test_folder = os.path.join(os.getcwd(), "test")

settings = contentcreatormanager.config.Settings(logging_config_file=logging_config_file, folder_location=test_folder)
logger = settings.Base_logger

reddit = contentcreatormanager.platform.reddit.Reddit(settings=settings)

post = reddit.post_text("Test", "This be another Text post", "Made by CCM: https://odysee.com/@TechGirlTiff:5/ContentCreatorManager_Dev_Project_Update_00004:4")

print(post.get_post_url())

post = reddit.post_text('test', "This be Another URL CCM Test", "https://odysee.com/@TechGirlTiff:5/ContentCreatorManager_Dev_Project_Update_00004:4")

print(post.get_post_url())