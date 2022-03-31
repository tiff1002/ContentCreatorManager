"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.config as ccm_config
import contentcreatormanager.platform.platform as plat
import contentcreatormanager.media.video.rumble as rumble_vid
import os
import json
import requests

class Rumble(plat.Platform):
    """
    classdocs
    """
    CLIENT_SECRETS_FILE = 'rumble_client_secret.json'
    
    UPLOAD_API_URL = "https://rumble.com/api/simple-upload.php"

    def __init__(self, settings : ccm_config.Settings,
                 init_videos : bool = False):
        """
        Constructor takes a Settings object.  ID set in credentials file. 
        Set flag init_videos to True to initialize all videos already on
        the Rumble Channel (not implemented yet)
        """
        super().__init__(settings=settings, ID='')
        self.logger = self.settings.Rumble_logger
        
        m="Initializing Platform Object as a Rumble Platform Object"
        self.logger.info(m)
        
        os.chdir(self.settings.original_dir)

        with open(Rumble.CLIENT_SECRETS_FILE) as f:
            creds = json.load(f)
            
        f.close()
        os.chdir(self.settings.folder_location)
        
        self.access_token = creds['ACCESS_TOKEN']
        self.id = creds['CHANNEL_ID']
        
        if init_videos:
            self.logger.info("Rumble init_videos is non functional")
        
        self.logger.info("Rumble Platform Object initialized")
          
    def add_video(self, vid : rumble_vid.RumbleVideo):
        """
        Method to add a Rumble video to media_objects list property
        """
        self.add_media(vid)
        
    def api_upload(self, access_token : str, title : str, description : str,
                   license_type : int, channel_id : str, guid : str,
                   video_file : str, thumbnail_file : str = ''):
        """
        Method to make Rumble Upload API call to upload a video to Rumble
        Example Call: api_upload(access_token=rumble.access_token,
                                 title='test title',
                                 description='test description',
                                 license_type=0, channel_id='1408326',
                                 video_file=os.path.join(os.getcwd(),
                                                         'upload_test.mp4'),
                                 guid="8932huf")
        Example Return's json() method: {'success': True, 'video_id': 'ttv81', 'video_id_int': 50102353, 'url_monetized': 'https://rumble.com/vwg19z-test-title.html?mref=zc4j3&mc=2xjkt', 'embed_url_monetized': 'https://rumble.com/embed/vttv81/?pub=zc4j3', 'embed_html_monetized': '<iframe class="rumble" width="640" height="360" src="https://rumble.com/embed/vttv81/?pub=zc4j3" frameborder="0" allowfullscreen></iframe>', 'embed_js_monetized': '<script>!function(r,u,m,b,l,e){r._Rumble=b,r[b]||(r[b]=function(){(r[b]._=r[b]._||[]).push(arguments);if(r[b]._.length==1){l=u.createElement(m),e=u.getElementsByTagName(m)[0],l.async=1,l.src="https://rumble.com/embedJS/uzc4j3"+(arguments[1].video?\'.\'+arguments[1].video:\'\')+"/?url="+encodeURIComponent(location.href)+"&args="+encodeURIComponent(JSON.stringify([].slice.apply(arguments))),e.parentNode.insertBefore(l,e)}})}(window, document, "script", "Rumble");</script>\n\n<div id="rumble_vttv81"></div>\n<script>\nRumble("play", {"video":"vttv81","div":"rumble_vttv81"});</script>'} 
        """
        m=f"Making Rumble API Call to upload video file: {video_file}"
        self.logger.info(m)
        if os.path.isfile(thumbnail_file):
            files = {
                'access_token': (None, access_token),
                'title': (None, title),
                'description': (None, description),
                'license_type': (None, license_type),
                'channel_id': (None, channel_id),
                'video': (os.path.basename(video_file),open(video_file,'rb')),
                'guid' : (None, guid),
                'thumb':(os.path.basename(thumbnail_file),
                         open(thumbnail_file,'rb'))
            }
        else:
            files = {
                'access_token': (None, access_token),
                'title': (None, title),
                'description': (None, description),
                'license_type': (None, license_type),
                'channel_id': (None, channel_id),
                'video': (os.path.basename(video_file),open(video_file,'rb')),
                'guid' : (None, guid)
            }
        
        response = requests.post(Rumble.UPLOAD_API_URL, files=files)
        
        return response
    
    def api_media_item(self, fid : str, access_token : str):
        """
        Method to make API call to get media item by id (NOT WORKING)
        """
        m="Media.Item API call implementation not working for Rumble"
        self.logger.warning(m)
        
        files = {
            'fid': (None, fid),
            'access_token' : (None, access_token)
        }
        
        response = requests.post("https://rumble.com/api/v0/Media.Item",
                                 files=files)
        
        return response