'''
Created on Mar 15, 2022

@author: tiff
'''
import contentcreatormanager.platform.lbry as lbry_plat
import contentcreatormanager.config as config
import os.path

folder = os.path.join(os.getcwd(), 'test')
settings = config.Settings(logging_config_file='logging.ini', folder_location=folder)

lbry = lbry_plat.LBRY(settings=settings, ID='8be45e4ba05bd6961619489f6408a0dc62f4e650', init_videos=True)

vid1 = lbry.media_objects[1]
vid2 = lbry.media_objects[0]

vid1.download()
vid2.download()
try:
    vid1.make_thumb()
    vid2.make_thumb()
except Exception as e:
    print(e.args)