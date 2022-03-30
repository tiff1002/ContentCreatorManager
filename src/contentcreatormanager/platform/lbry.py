"""
Created on Feb 24, 2022

@author: tiff
"""
import contentcreatormanager.config as ccm_config
import contentcreatormanager.platform.platform as plat
import contentcreatormanager.media.video.lbry as lbry_vid
import contentcreatormanager.media.post.lbry as lbry_post
import requests
import shortuuid
import os.path

def claim_list(claim_type : list = [], claim_id : list = [],
                       channel_id: list = [], name : list = [],
                       account_id : str = '', order_by : str = '',
                       page : int = 0, resolve : bool = True,
                       page_size: int = 20):
    parameters = dict(
        claim_type=claim_type,
        claim_id=claim_id,
        channel_id=channel_id,
        name=name,
        page_size=page_size,
        resolve=resolve,
    )
        
    if not (account_id == '' or account_id is None):
        parameters['account_id']=account_id
        
    if not (page == 0 or page is None):
        parameters['page']=page
        
    if not (order_by == '' or order_by is None):
        parameters['order_by']=order_by
        
        
    result = requests.post(LBRY.API_URL,
                           json={"method": "claim_list",
                                 "params": parameters}).json()
        
    
    return result

class LBRY(plat.Platform):
    """
    classdocs
    """
    API_URL = "http://localhost:5279"
    
    PAGE_RESULT_LENGTH = 20
    
    LBRY_THUMB_API_URL = 'https://spee.ch/api/claim/publish'

    def __init__(self, settings : ccm_config.Settings, ID : str,
                 init_videos : bool = False):
        """
        Constructor takes a Settings object.  ID string required 
        (claim_id of the channel to be used).  Set init_videos flag
        to True to grab all video data from LBRY on creation of
        LBRY Platform Object.
        """
        super(LBRY, self).__init__(settings=settings, ID=ID)
        
        self.logger = self.settings.LBRY_logger
        self.logger.info("Initializing Platform Object as LBRY Platform")
        
        result = self.__get_channel()
        
        m="Setting local values based on API call results"
        self.logger.info(m)
        self.address = result['result']['items'][0]['address']
        self.bid = result['result']['items'][0]['amount']
        self.name = result['result']['items'][0]['name']
        self.normalized_name = result['result']['items'][0]['normalized_name']
        self.permanent_url = result['result']['items'][0]['permanent_url']
        
        if 'title' in result['result']['items'][0]['value']:
            self.title = result['result']['items'][0]['value']['title']
        if 'description' in result['result']['items'][0]['value']:
            self.description = result['result']['items'][0]['value']['description']
        if 'email' in result['result']['items'][0]['value']:
            self.email = result['result']['items'][0]['value']['email']
        if 'languages' in result['result']['items'][0]['value']:
            self.languages = result['result']['items'][0]['value']['languages']
        else:
            self.languages = ['en']
        if 'tags' in result['result']['items'][0]['value']:
            self.tags = result['result']['items'][0]['value']['tags']
        else:
            self.tags = []
        if 'thumbnail' in result['result']['items'][0]['value']:    
            self.thumbnail = result['result']['items'][0]['value']['thumbnail']
        else:
            self.thumbnail = None
            
        if init_videos:
            m="init_videos set to true grabbing video data"
            self.logger.info(m)
            self.__add_channel_videos()
            
        self.logger.info("LBRY Platform object initialized")
    
    def __get_channel(self):
        """
        Private method to make api call to get channel info based on claim_id
        (which is the id property) and return the results
        """
        result = self.api_channel_list(claim_id=[self.id])
            
        return result
    
    def __add_channel_videos(self):
        """
        Private method to grab all videos for the channel via api and then use
        that data to create LBRYVideo objects and add them to media_objects
        list property
        """       
        intial_result = self.api_claim_list(claim_type=['stream'],
                                            channel_id=[self.id],
                                            order_by='name', resolve=False,
                                            page_size=LBRY.PAGE_RESULT_LENGTH)
        
        page_amount = intial_result['result']['total_pages']
        item_amount = intial_result['result']['total_items']
        
        self.logger.info(f"Found {item_amount} claims on channel")
        
        pages = []
        claims = []
        
        self.logger.info("adding initial request as 1st page of data")
        pages.append(intial_result['result']['items'])
        
        if page_amount > 1:
            for x in range(page_amount-1):
                self.logger.info(f"getting page {x+2} of data and adding it")
                current_result = self.api_claim_list(claim_type=['stream'],
                                                     channel_id=[self.id],
                                                     order_by='name', page=x+2,
                                                     resolve=False,
                                                     page_size=LBRY.PAGE_RESULT_LENGTH)
                pages.append(current_result['result']['items'])
        
        page = 0
        x = 0
        for p in pages:
            page += 1
            for i in p:
                x += 1
                if i['value']['stream_type'] == 'video':
                    self.logger.info(f"Adding claim with name {i['name']}")
                    claims.append(i)
                else:
                    m=f"claim {i['name']} is not a video.  Not adding it"
                    self.logger.info(m)
        
        num_claims_before = len(self.media_objects)
        
        for c in claims:
            v = lbry_vid.LBRYVideo(ID=c['claim_id'], lbry_channel=self,
                                   request=c)
            v.set_file_based_on_title()
            thumb_dir = os.path.join(os.getcwd(), 'thumbs')
            v.thumbnail = os.path.join(thumb_dir, v.get_valid_thumbnail_file_name())
            self.add_media(v)
        
        num_vids_added = len(self.media_objects) - num_claims_before
        m=f"{num_vids_added} LBRY Video Objects added to media_objects"
        self.logger.info(m)
    
    def add_video(self, vid : lbry_vid.LBRYVideo):
        """
        Method to add a LBRY Video Object to the media_objects list property
        """
        self.add_media(vid)
     
    def add_video_with_name(self, name : str, file_name : str,
                            update_from_web : bool = True,
                            upload : bool = False, title : str = '',
                            description : str = '', tags : list = [],
                            bid : str = '0.001'):
        """
        Method to add a LBRY Video Object to the media_objects list property.
        This uses the name provided to lookup other details about the video
        to add if the update_from_web flag is set to True which is the default.
        If the upload flag is set to True (default is False) the video will be
        uploaded after the object is created. upload and update_from_web can
        not both be True.
        """
        if update_from_web and upload:
            m="Either update from web or upload to it not both :P"
            self.logger.error(m)
            return None
        
        vid = lbry_vid.LBRYVideo(settings=self.settings,
                                 lbry_channel=self,
                                 file_name=file_name)
        vid.name = name
        vid.tags = tags
        vid.title = title
        vid.description = description
        vid.bid = bid
        
        if update_from_web:
            vid.update_local(use_name=True)
        elif upload:
            if title == '' or description == '':
                m="Title and Description Required for new upload."
                self.logger.error(m)
            else:
                vid.upload()
        self.add_video(vid)
        
    def make_post(self, title : str, body : str, tags : list = [],
                  languages : list = ['en'], bid : str = "0.001",
                  thumbnail_url : str = ''):
        post = lbry_post.LBRYTextPost(lbry_channel=self, title=title,
                                      body=body, name=title, tags=tags,
                                      bid=bid, thumbnail_url=thumbnail_url,
                                      languages=languages)
        
        post.upload()
        
        self.add_media(post)
        
        return post
    
    def api_get(self, uri : str, 
                download_directory : str = '',
                file_name : str = ''):
        """
        Method to make a get call to the LBRY API
        Example Call: api_get(uri='lbry://@ComputingForever#9/hitat-2-3-2022-Broadband-High#1',
                              download_directory=os.getcwd())
        Example Return: {'jsonrpc': '2.0', 'result': {'added_on': 1646318291, 'blobs_completed': 9, 'blobs_in_stream': 139, 'blobs_remaining': 130, 'channel_claim_id': '92b7f813e4210a06fc55968dbea36e5f1f095e6d', 'channel_name': '@ComputingForever', 'claim_id': '1ef601ec82b58b457214acf167583fc3fad079bd', 'claim_name': 'hitat-2-3-2022-Broadband-High', 'completed': False, 'confirmations': 470, 'content_fee': None, 'download_directory': None, 'download_path': None, 'file_name': None, 'height': 1120356, 'is_fully_reflected': True, 'key': '9e6ec5180383afa0ce8cf6647e0465bb', 'metadata': {'description': 'Sign-up to Nord VPN here: http://nordvpn.org/computingforever\n\nSupport my work on Subscribe Star: https://www.subscribestar.com/dave-cullen\nSupport my work via crypto: https://computingforever.com/donate/\nFollow me on Bitchute: https://www.bitchute.com/channel/hybM74uIHJKg/\n\nThomas Sheridan’s video: Some Curious Observations: https://www.youtube.com/watch?v=eV6ZPjyZI_0\n\nSources: https://computingforever.com/2022/03/02/how-is-this-a-thing-2nd-march-2022/\n\nhttp://www.computingforever.com\nKEEP UP ON SOCIAL MEDIA:\nGab: https://gab.ai/DaveCullen\nSubscribe on Gab TV: https://tv.gab.com/channel/DaveCullen\nMinds.com: https://www.minds.com/davecullen\nSubscribe on Odysee: https://odysee.com/@TheDaveCullenShow:7\nTelegram: https://t.me/ComputingForeverOfficial\n\nThis video contains images and videos sourced from pixabay.com:\n\nhttps://pixabay.com/photos/woman-face-mask-protection-5693746/\nhttps://pixabay.com/photos/mask-protection-virus-pandemic-4934337/\nhttps://pixabay.com/photos/coronavirus-covid-covid-19-pandemic-4947210/\nhttps://pixabay.com/photos/mouth-guard-infection-purchasing-5068146/\nhttps://pixabay.com/videos/heart-medical-treatment-ecg-health-32264/\nhttps://pixabay.com/photos/bowl-breakfast-fruits-healthy-food-1844894/\nhttps://pixabay.com/photos/joint-blunt-smoke-ashtray-cannabis-6535558/\nhttps://pixabay.com/videos/snowfall-snow-snowflakes-2362/\nhttps://pixabay.com/videos/ireland-athletics-sea-running-22913/\nhttps://pixabay.com/photos/shoveling-man-snow-work-male-tool-17328/\nhttps://pixabay.com/photos/vaccination-syringe-mask-vaccine-6576827/\nhttps://pixabay.com/videos/flag-russia-flag-of-russia-tricolor-41903/\nhttps://pixabay.com/videos/ukraine-flag-ukraine-flag-kiev-109053/\nhttps://pixabay.com/videos/earth-globe-country-africa-asia-1393/\n', 'languages': ['en'], 'license': 'None', 'release_time': '1646240461', 'source': {'hash': 'b17cf22cb42351f77300c100f5f348a336335fc693cc84266000eea7af2e0d4791b80c26e2e3b0db3878e21f34492f5b', 'media_type': 'video/mp4', 'name': 'hitat-2-3-2022-Broadband High.mp4', 'sd_hash': '2a3ff07adabe0086a67bd3dac69435d224bdd4dd691cca216dc91fd9aa7b9f80875dcab3041c9d26c70a53eafde10b89', 'size': '289797482'}, 'stream_type': 'video', 'tags': ['computing forever', 'dave cullen'], 'thumbnail': {'url': 'https://thumbs.odycdn.com/8d3d6a0076cb09ad7478eb8bc7097a0e.jpg'}, 'title': 'How is This a Thing? 2nd March 2022', 'video': {'duration': 751, 'height': 720, 'width': 1280}}, 'mime_type': 'video/mp4', 'nout': 0, 'outpoint': '5bd19409c7b9cfbc3ac5a33d8928c766db061620336d1d955fe082ea38fb64f5:0', 'points_paid': 0.0, 'protobuf': '016d5e091f5f6ea3be8d9655fc060a21e413f8b79226f86f0ef1419dbd6ba19930aca6ba907e4438119d5776da11c6dde391551ab1f00cf37f7a6bc20d7ce334e95b6757ac9fd786f21449aee75d95ac8386a33cc20ab2010a98010a30b17cf22cb42351f77300c100f5f348a336335fc693cc84266000eea7af2e0d4791b80c26e2e3b0db3878e21f34492f5b122168697461742d322d332d323032322d42726f616462616e6420486967682e6d703418eaea978a012209766964656f2f6d703432302a3ff07adabe0086a67bd3dac69435d224bdd4dd691cca216dc91fd9aa7b9f80875dcab3041c9d26c70a53eafde10b891a044e6f6e6528cdc5fe90065a0908800a10d00518ef054223486f7720697320546869732061205468696e673f20326e64204d6172636820323032324ae90d5369676e2d757020746f204e6f72642056504e20686572653a20687474703a2f2f6e6f726476706e2e6f72672f636f6d707574696e67666f72657665720a0a537570706f7274206d7920776f726b206f6e2053756273637269626520537461723a2068747470733a2f2f7777772e737562736372696265737461722e636f6d2f646176652d63756c6c656e0a537570706f7274206d7920776f726b207669612063727970746f3a2068747470733a2f2f636f6d707574696e67666f72657665722e636f6d2f646f6e6174652f0a466f6c6c6f77206d65206f6e2042697463687574653a2068747470733a2f2f7777772e62697463687574652e636f6d2f6368616e6e656c2f6879624d37347549484a4b672f0a0a54686f6d617320536865726964616ee280997320766964656f3a20536f6d6520437572696f7573204f62736572766174696f6e733a2068747470733a2f2f7777772e796f75747562652e636f6d2f77617463683f763d6556365a506a795a495f300a0a536f75726365733a2068747470733a2f2f636f6d707574696e67666f72657665722e636f6d2f323032322f30332f30322f686f772d69732d746869732d612d7468696e672d326e642d6d617263682d323032322f0a0a687474703a2f2f7777772e636f6d707574696e67666f72657665722e636f6d0a4b454550205550204f4e20534f4349414c204d454449413a0a4761623a2068747470733a2f2f6761622e61692f4461766543756c6c656e0a537562736372696265206f6e204761622054563a2068747470733a2f2f74762e6761622e636f6d2f6368616e6e656c2f4461766543756c6c656e0a4d696e64732e636f6d3a2068747470733a2f2f7777772e6d696e64732e636f6d2f6461766563756c6c656e0a537562736372696265206f6e204f64797365653a2068747470733a2f2f6f64797365652e636f6d2f405468654461766543756c6c656e53686f773a370a54656c656772616d3a2068747470733a2f2f742e6d652f436f6d707574696e67466f72657665724f6666696369616c0a0a5468697320766964656f20636f6e7461696e7320696d6167657320616e6420766964656f7320736f75726365642066726f6d20706978616261792e636f6d3a0a0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f776f6d616e2d666163652d6d61736b2d70726f74656374696f6e2d353639333734362f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f6d61736b2d70726f74656374696f6e2d76697275732d70616e64656d69632d343933343333372f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f636f726f6e6176697275732d636f7669642d636f7669642d31392d70616e64656d69632d343934373231302f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f6d6f7574682d67756172642d696e66656374696f6e2d70757263686173696e672d353036383134362f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f68656172742d6d65646963616c2d74726561746d656e742d6563672d6865616c74682d33323236342f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f626f776c2d627265616b666173742d6672756974732d6865616c7468792d666f6f642d313834343839342f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f6a6f696e742d626c756e742d736d6f6b652d617368747261792d63616e6e616269732d363533353535382f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f736e6f7766616c6c2d736e6f772d736e6f77666c616b65732d323336322f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f6972656c616e642d6174686c65746963732d7365612d72756e6e696e672d32323931332f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f73686f76656c696e672d6d616e2d736e6f772d776f726b2d6d616c652d746f6f6c2d31373332382f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f76616363696e6174696f6e2d737972696e67652d6d61736b2d76616363696e652d363537363832372f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f666c61672d7275737369612d666c61672d6f662d7275737369612d747269636f6c6f722d34313930332f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f756b7261696e652d666c61672d756b7261696e652d666c61672d6b6965762d3130393035332f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f65617274682d676c6f62652d636f756e7472792d6166726963612d617369612d313339332f0a52402a3e68747470733a2f2f7468756d62732e6f647963646e2e636f6d2f38643364366130303736636230396164373437386562386263373039376130652e6a70675a11636f6d707574696e6720666f72657665725a0b646176652063756c6c656e62020801', 'purchase_receipt': None, 'reflector_progress': 0, 'sd_hash': '2a3ff07adabe0086a67bd3dac69435d224bdd4dd691cca216dc91fd9aa7b9f80875dcab3041c9d26c70a53eafde10b89', 'status': 'running', 'stopped': False, 'stream_hash': 'd4076694abf6ab1c095c394f466858c1e99df4338f87068a8b8bee717f96bb75a0db941173f1852fd0b31a5f4b8153a9', 'stream_name': 'hitat-2-3-2022-Broadband High.mp4', 'streaming_url': 'http://localhost:5280/stream/2a3ff07adabe0086a67bd3dac69435d224bdd4dd691cca216dc91fd9aa7b9f80875dcab3041c9d26c70a53eafde10b89', 'suggested_file_name': 'hitat-2-3-2022-Broadband High.mp4', 'timestamp': 1646242133, 'total_bytes': 289797494, 'total_bytes_lower_bound': 289797478, 'txid': '5bd19409c7b9cfbc3ac5a33d8928c766db061620336d1d955fe082ea38fb64f5', 'uploading_to_reflector': False, 'written_bytes': 0}}
        """
        
        parameters = dict(
            uri=uri
        )
        
        if not (file_name == '' or file_name is None):
            parameters['file_name'] = file_name
        
        if not (download_directory == '' or download_directory is None):
            parameters['download_directory'] = download_directory
        
        result = requests.post(LBRY.API_URL,
                               json={"method": "get",
                                     "params": parameters}).json()
        
        m=f"get call with parameters {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_channel_list(self, claim_id : list = [], page : int = 0,
                         name : str = '', page_size : int = PAGE_RESULT_LENGTH,
                         resolve : bool = False):
        """
        Method to make a channel_list call to the LBRY API (setting resolve to
        True gives you more info on the channels listed not the claims on the
        channels themselves)
        Example Call: api_channel_list()
        Example Return: {'jsonrpc': '2.0', 'result': {'items': [{'address': 'bFR3HtPv3TqNRp8KQt1TZueZABnjos2WyB', 'amount': '0.005', 'claim_id': '8be45e4ba05bd6961619489f6408a0dc62f4e650', 'claim_op': 'update', 'confirmations': 11, 'has_signing_key': True, 'height': 1120834, 'is_internal_transfer': False, 'is_my_input': True, 'is_my_output': True, 'is_spent': False, 'meta': {}, 'name': '@Tiff_Tech_Test_Channel', 'normalized_name': '@tiff_tech_test_channel', 'nout': 0, 'permanent_url': 'lbry://@Tiff_Tech_Test_Channel#8be45e4ba05bd6961619489f6408a0dc62f4e650', 'timestamp': 1646319759, 'txid': 'c2ab9d8f4d151b771863165480ed2d6340d8f08bb5255849088f78ce67ffcbea', 'type': 'claim', 'value': {'cover': {'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Test-Logo.svg/783px-Test-Logo.svg.png'}, 'description': "Tiff's Channel for Testing things", 'email': 'test@tiff.tech', 'public_key': '3056301006072a8648ce3d020106052b8104000a03420004a922acec8cbff92392a0d5d206c9334f5b99b90143594d98fef4dc085d6917e68417c8b0fb67732266a5bc4b97785e256e6f2dedc3cbf4c269b0d7aabc1f3365', 'public_key_id': 'bHrJFge6cs7rhv8GknD1RGCWYPhDduC2Mj', 'thumbnail': {'url': 'https://e7.pngegg.com/pngimages/575/704/png-clipart-computer-icons-test-scalable-graphics-test-score-angle-pencil-thumbnail.png'}, 'title': 'Tiff Test Channel Updated', 'website_url': 'http://google.com'}, 'value_type': 'channel'}, {'address': 'bRaNopJotKsM61BfDV49fZTnRRgCWKMGoU', 'amount': '5.0', 'claim_id': '5e79dc0b3a00f643a0a964c87538ae2d66ddbbed', 'claim_op': 'create', 'confirmations': 9055, 'has_signing_key': True, 'height': 1111790, 'is_internal_transfer': False, 'is_my_input': True, 'is_my_output': True, 'is_spent': False, 'meta': {}, 'name': '@TechGirlTiff', 'normalized_name': '@techgirltiff', 'nout': 0, 'permanent_url': 'lbry://@TechGirlTiff#5e79dc0b3a00f643a0a964c87538ae2d66ddbbed', 'timestamp': 1644870241, 'txid': 'b3647d6c0ca2acba87206043320d8e06eeb8bd46177afd4c1a09a7040ea77511', 'type': 'claim', 'value': {'cover': {'url': 'https://spee.ch/f/a5d238ffa2ed219b.png'}, 'description': 'This channel is just a dumping place for videos documenting various adventures I am undertaking (typicaly various hobbies).  So far I have lockpicking and Dance and Rhythm Games as well as cooking/baking and some interesting tech based projects.  I wonder what I will do next?', 'email': 'tiff@tiff.tech', 'languages': ['en'], 'public_key': '3056301006072a8648ce3d020106052b8104000a03420004fbdd4d2c0a8b838c922055c09fe0adfdc0534daa2ef8fb98c31cd7755f60b98d7d57e73b590b451aea68b76f22bde09901cc749c53ba9095e21977a1405b8166', 'public_key_id': 'bDC75tUzjxCpiTLrAoehbVBzagwvfb2LbD', 'tags': ['tech', 'locksport', 'cooking', 'hobbies', 'howto'], 'thumbnail': {'url': 'https://spee.ch/d/aaa3b1d3f58d2753.png'}, 'title': 'Tech_Girl_Tiff'}, 'value_type': 'channel'}], 'page': 1, 'page_size': 20, 'total_items': 2, 'total_pages': 1}}
        """
        parameters = dict(
            claim_id=claim_id,
            resolve=resolve,
            page_size=page_size
        )
        
        if not (page == 0 or page is None):
            parameters['page'] = page
            
        if not (name == '' or name is None):
            parameters['name'] = name

        
        result = requests.post(LBRY.API_URL,
                               json={"method": "channel_list",
                                     "params": parameters}).json()
        
        m=f"channel_list call with params: {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_channel_create(self, name : str, bid : float, title : str,
                           description : str, email : str, website_url : str,
                           thumbnail_url : str, cover_url : str,
                           featured : list = [], tags : list = [],
                           languages : list = []):
        """
        Method to make a channel_create call to the LBRY API
        Example Call: api_channel_create(name="@TestChannelToBeDeleted",
                                        bid=.001, title='Test Title Channel', 
                                        description='Who Cares will be deleted',
                                        email='test@tiff.tech',
                                        website_url='http://google.com',
                                        thumbnail_url='', cover_url='',
                                        tags=['test'], languages=['en'])
        Example Return: {'jsonrpc': '2.0', 'result': {'height': -2, 'hex': '01000000012e0396eb30908cbd38e5f13ac6ddbd7cde9acf1df27efd691770f12af560aac6010000006b483045022100f6b7a5de3977af0489fd407bd4c04ae5254e7de293383c24862f6744c081ac4502206b522756e3c6081ca820c8429a73ff8ccf6625d5bbdad4f61e03ef2f18424fb6012103530e3fc1f5bb76c05c5cd473fb292bd1dbe175435ebd81aa2b040d873dfdd346ffffffff02a086010000000000f3b51740546573744368616e6e656c546f426544656c657465644cbd00127f0a583056301006072a8648ce3d020106052b8104000a03420004f16d2b496368cebe4c196f7c22a60e86936298077a8446a626a2b212c800ab1ca4df77c2cdf68dbef93815fa2282ead77bc76f2d6ac448b5e2340618e06999be120e7465737440746966662e746563681a11687474703a2f2f676f6f676c652e636f6d2200421254657374205469746c65204368616e6e656c4a1957686f2043617265732077696c6c2062652064656c6574656452005a0474657374620208016d7576a9144744d18d37d7412a2cd465a6dc0c205df630234488ac50f8d400000000001976a91422cf64f8535aa5c6c9678c7e2de83fc99fedf5cd88ac00000000', 'inputs': [{'address': 'bbhW2MsQdsqWNgjU8r1itnyJyLDyQpjkt7', 'amount': '0.186679', 'confirmations': 19, 'height': 1120820, 'nout': 1, 'timestamp': 1646317805, 'txid': 'c6aa60f52af1701769fd7ef21dcf9ade7cbdddc63af1e538bd8c9030eb96032e', 'type': 'payment'}], 'outputs': [{'address': 'bKE77SwrcYvaf9jyY2SfhEqytVYjsNtVLr', 'amount': '0.001', 'claim_id': 'dbac30041d0d4fd0ed928696379e839b062e8565', 'claim_op': 'create', 'confirmations': -2, 'has_signing_key': True, 'height': -2, 'meta': {}, 'name': '@TestChannelToBeDeleted', 'normalized_name': '@testchanneltobedeleted', 'nout': 0, 'permanent_url': 'lbry://@TestChannelToBeDeleted#dbac30041d0d4fd0ed928696379e839b062e8565', 'timestamp': None, 'txid': '7cd963a313c2c93279af226971e1e33c4abd0dcde5d314dcc012a42d4d5f087b', 'type': 'claim', 'value': {'cover': {}, 'description': 'Who Cares will be deleted', 'email': 'test@tiff.tech', 'languages': ['en'], 'public_key': '3056301006072a8648ce3d020106052b8104000a03420004f16d2b496368cebe4c196f7c22a60e86936298077a8446a626a2b212c800ab1ca4df77c2cdf68dbef93815fa2282ead77bc76f2d6ac448b5e2340618e06999be', 'public_key_id': 'bFKbUSauFLnLzchVsfZFNXS7jQcKFMJkrq', 'tags': ['test'], 'thumbnail': {}, 'title': 'Test Title Channel', 'website_url': 'http://google.com'}, 'value_type': 'channel'}, {'address': 'bFuL7margt27eQVwx2EdNtsHAKDz7TCEmi', 'amount': '0.139572', 'confirmations': -2, 'height': -2, 'nout': 1, 'timestamp': None, 'txid': '7cd963a313c2c93279af226971e1e33c4abd0dcde5d314dcc012a42d4d5f087b', 'type': 'payment'}], 'total_fee': '0.046107', 'total_input': '0.186679', 'total_output': '0.140572', 'txid': '7cd963a313c2c93279af226971e1e33c4abd0dcde5d314dcc012a42d4d5f087b'}}
        Example Call with Error: api_channel_create(name="TestChannelToBeDeleted",
                                                    bid=.001, title='Test Title Channel',
                                                    description='Who Cares will be deleted',
                                                    email='test@tiff.tech',
                                                    website_url='http://google.com',
                                                    thumbnail_url='', cover_url='',
                                                    tags=['test'], languages=['en'])
        Example Result with Error: {'error': {'code': -32500, 'data': {'args': [], 'command': 'channel_create', 'kwargs': {'bid': '0.001', 'cover_url': '', 'description': 'Who Cares will be deleted', 'email': 'test@tiff.tech', 'featured': [], 'languages': ['en'], 'name': 'TestChannelToBeDeleted', 'tags': ['test'], 'thumbnail_url': '', 'title': 'Test Title Channel', 'website_url': 'http://google.com'}, 'name': 'Exception', 'traceback': ['Traceback (most recent call last):', '  File "lbry\\extras\\daemon\\daemon.py", line 752, in _process_rpc_call', '  File "lbry\\extras\\daemon\\daemon.py", line 2682, in jsonrpc_channel_create', '  File "lbry\\extras\\daemon\\daemon.py", line 5304, in valid_channel_name_or_error', "Exception: Channel names must start with '@' symbol.", '']}, 'message': "Channel names must start with '@' symbol."}, 'jsonrpc': '2.0'}
        """
        parameters = dict(
            name=name,
            bid=str(bid),
            title=title,
            description=description,
            email=email,
            website_url=website_url,
            featured=featured,
            tags=tags,
            languages=languages,
            thumbnail_url=thumbnail_url,
            cover_url=cover_url 
        )
        
        result = requests.post(LBRY.API_URL,
                               json={"method": "channel_create",
                                     "params": parameters}).json()
        
        m=f"channel_create call with params: {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_channel_abandon(self, claim_id : str):
        """
        Method to make a channel_abandon call to the LBRY API
        Example Call: api_channel_abandon(claim_id='dbac30041d0d4fd0ed928696379e839b062e8565')
        Example Return: {'jsonrpc': '2.0', 'result': {'height': -2, 'hex': '01000000017b085f4d2da412c0dc14d3e5cd0dbd4a3ce3e1716922af7932c9c213a363d97c000000006b483045022100faac86e6ea0c46e6be9235e27f65b0379cccfeffe39e59416f24a7d7e77826cc02207414f375ed9aca14e96b9052086dbd3fe3a72f266f3accace62c5ea01e452a8f012103ff76d3a403eb8d5d2ec2132e3006e3eec95b9b2b9178509326e3c340bb8e8c95ffffffff01d45c0100000000001976a9149d834f10a22358ea8ceae4dfb49905448a07b91688ac00000000', 'inputs': [{'address': 'bKE77SwrcYvaf9jyY2SfhEqytVYjsNtVLr', 'amount': '0.001', 'claim_id': 'dbac30041d0d4fd0ed928696379e839b062e8565', 'claim_op': 'create', 'confirmations': 2, 'has_signing_key': True, 'height': 1120839, 'meta': {}, 'name': '@TestChannelToBeDeleted', 'normalized_name': '@testchanneltobedeleted', 'nout': 0, 'permanent_url': 'lbry://@TestChannelToBeDeleted#dbac30041d0d4fd0ed928696379e839b062e8565', 'timestamp': 1646320497, 'txid': '7cd963a313c2c93279af226971e1e33c4abd0dcde5d314dcc012a42d4d5f087b', 'type': 'claim', 'value': {'cover': {}, 'description': 'Who Cares will be deleted', 'email': 'test@tiff.tech', 'languages': ['en'], 'public_key': '3056301006072a8648ce3d020106052b8104000a03420004f16d2b496368cebe4c196f7c22a60e86936298077a8446a626a2b212c800ab1ca4df77c2cdf68dbef93815fa2282ead77bc76f2d6ac448b5e2340618e06999be', 'public_key_id': 'bFKbUSauFLnLzchVsfZFNXS7jQcKFMJkrq', 'tags': ['test'], 'thumbnail': {}, 'title': 'Test Title Channel', 'website_url': 'http://google.com'}, 'value_type': 'channel'}], 'outputs': [{'address': 'bT685r4t2vaZkRdKBMyjaveuD9Sw4TDS8D', 'amount': '0.000893', 'confirmations': -2, 'height': -2, 'nout': 0, 'timestamp': None, 'txid': '528372edeb28f5a6b568870e55d468edfcce7caaf0c2175a05c0f48d979d79de', 'type': 'payment'}], 'total_fee': '0.000107', 'total_input': '0.001', 'total_output': '0.000893', 'txid': '528372edeb28f5a6b568870e55d468edfcce7caaf0c2175a05c0f48d979d79de'}}
        """
        parameters = dict(
            claim_id=claim_id
        )

        result = requests.post(LBRY.API_URL,
                               json={"method": "channel_abandon",
                                     "params": parameters}).json()
        
        m=f"channel_abandon call w/ params: {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_channel_update(self, claim_id : str, bid : float, title : str,
                           description : str, email : str, website_url : str,
                           cover_url : str, thumbnail_url : str,
                           clear_tags : bool = True,
                           clear_languages : bool = True,
                           replace : bool = True,
                           languages : list = [], tags : list = [],
                           featured : list = []):
        """
        Method to make a channel_update call to the LBRY API
        Example Call: api_channel_update(claim_id='8be45e4ba05bd6961619489f6408a0dc62f4e650',
                                        bid=.005, title='Tiff Test Channel Updated',
                                        description="Tiff's Channel for Testing things",
                                        email='test@tiff.tech', website_url='http://google.com',
                                        cover_url='https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Test-Logo.svg/783px-Test-Logo.svg.png',
                                        thumbnail_url='https://e7.pngegg.com/pngimages/575/704/png-clipart-computer-icons-test-scalable-graphics-test-score-angle-pencil-thumbnail.png')
        Example Return: {'jsonrpc': '2.0', 'result': {'height': -2, 'hex': '0100000002ede6315d9a2f2139ffc8aba32bad12995ba7f86f807df942adbed26035f3b0a7000000006a47304402201f775457257a581f4801131a1566a6d4d5d4a13a18d9a13454f1a87ea8d6ff310220063e69019ffaddaf424c76a50a81c2c20fccf55f52dedde750553716b73034410121033832d5ba14c39f8474fde721b3c2f0c553545d232050cbe96c3844a8738ea88dffffffff1117b3f455c31227275048dce10309a1e752e9b97de300e4607d4eb2faffae76010000006b483045022100bcab9f50d45cc3b84e129ebe679e7fe8540f92f6ad6e8165215011271b2a9b4102203ae9cfb997a09ffe4d8e236ef3614f2a7aa26dd18521f029f277dc63f0a01079012103d6d1ca10877c3d1a7989b0bed1996d4a4f39569184648a8965c31e571e40e7e5ffffffff0220a1070000000000fdf201b71740546966665f546563685f546573745f4368616e6e656c1450e6f462dca008649f48191696d65ba04b5ee48b4da6010012e0010a583056301006072a8648ce3d020106052b8104000a03420004a922acec8cbff92392a0d5d206c9334f5b99b90143594d98fef4dc085d6917e68417c8b0fb67732266a5bc4b97785e256e6f2dedc3cbf4c269b0d7aabc1f3365120e7465737440746966662e746563681a11687474703a2f2f676f6f676c652e636f6d22612a5f68747470733a2f2f75706c6f61642e77696b696d656469612e6f72672f77696b6970656469612f636f6d6d6f6e732f7468756d622f312f31312f546573742d4c6f676f2e7376672f37383370782d546573742d4c6f676f2e7376672e706e674219546966662054657374204368616e6e656c20557064617465644a21546966662773204368616e6e656c20666f722054657374696e67207468696e67735281012a7f68747470733a2f2f65372e706e676567672e636f6d2f706e67696d616765732f3537352f3730342f706e672d636c69706172742d636f6d70757465722d69636f6e732d746573742d7363616c61626c652d67726170686963732d746573742d73636f72652d616e676c652d70656e63696c2d7468756d626e61696c2e706e676d6d76a9141d75b3c435ce5e0d5d2399fa614feab2bd3b4b7088acf6e00a00000000001976a9147a8d33c1c72f7d6cc776a2a0c288571aa08dfd9d88ac00000000', 'inputs': [{'address': 'bFR3HtPv3TqNRp8KQt1TZueZABnjos2WyB', 'amount': '0.001', 'claim_id': '8be45e4ba05bd6961619489f6408a0dc62f4e650', 'claim_op': 'create', 'confirmations': 176963, 'has_signing_key': True, 'height': 943870, 'meta': {}, 'name': '@Tiff_Tech_Test_Channel', 'normalized_name': '@tiff_tech_test_channel', 'nout': 0, 'permanent_url': 'lbry://@Tiff_Tech_Test_Channel#8be45e4ba05bd6961619489f6408a0dc62f4e650', 'timestamp': 1618163141, 'txid': 'a7b0f33560d2bead42f97d806ff8a75b9912ad2ba3abc8ff39212f9a5d31e6ed', 'type': 'claim', 'value': {'description': 'Channel to use for testing stuff with the API/SDK', 'email': 'test@tiff.tech', 'public_key': '3056301006072a8648ce3d020106052b8104000a03420004a922acec8cbff92392a0d5d206c9334f5b99b90143594d98fef4dc085d6917e68417c8b0fb67732266a5bc4b97785e256e6f2dedc3cbf4c269b0d7aabc1f3365', 'public_key_id': 'bHrJFge6cs7rhv8GknD1RGCWYPhDduC2Mj', 'title': 'Tiff_Tech_Test_Channel'}, 'value_type': 'channel'}, {'address': 'bNX8WTAAYFSWTqKpVD1SzWHRbuJnmKFF14', 'amount': '0.011565', 'confirmations': 13, 'height': 1120820, 'nout': 1, 'timestamp': 1646317805, 'txid': '76aefffab24e7d60e400e37db9e952e7a10903e1dc4850272712c355f4b31711', 'type': 'payment'}], 'outputs': [{'address': 'bFR3HtPv3TqNRp8KQt1TZueZABnjos2WyB', 'amount': '0.005', 'claim_id': '8be45e4ba05bd6961619489f6408a0dc62f4e650', 'claim_op': 'update', 'confirmations': -2, 'has_signing_key': True, 'height': -2, 'meta': {}, 'name': '@Tiff_Tech_Test_Channel', 'normalized_name': '@tiff_tech_test_channel', 'nout': 0, 'permanent_url': 'lbry://@Tiff_Tech_Test_Channel#8be45e4ba05bd6961619489f6408a0dc62f4e650', 'timestamp': None, 'txid': 'c2ab9d8f4d151b771863165480ed2d6340d8f08bb5255849088f78ce67ffcbea', 'type': 'claim', 'value': {'cover': {'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Test-Logo.svg/783px-Test-Logo.svg.png'}, 'description': "Tiff's Channel for Testing things", 'email': 'test@tiff.tech', 'public_key': '3056301006072a8648ce3d020106052b8104000a03420004a922acec8cbff92392a0d5d206c9334f5b99b90143594d98fef4dc085d6917e68417c8b0fb67732266a5bc4b97785e256e6f2dedc3cbf4c269b0d7aabc1f3365', 'public_key_id': 'bHrJFge6cs7rhv8GknD1RGCWYPhDduC2Mj', 'thumbnail': {'url': 'https://e7.pngegg.com/pngimages/575/704/png-clipart-computer-icons-test-scalable-graphics-test-score-angle-pencil-thumbnail.png'}, 'title': 'Tiff Test Channel Updated', 'website_url': 'http://google.com'}, 'value_type': 'channel'}, {'address': 'bPuGHXszAGMEEh1eggyyPYtHJssztw9R6x', 'amount': '0.0071295', 'confirmations': -2, 'height': -2, 'nout': 1, 'timestamp': None, 'txid': 'c2ab9d8f4d151b771863165480ed2d6340d8f08bb5255849088f78ce67ffcbea', 'type': 'payment'}], 'total_fee': '0.0004355', 'total_input': '0.012565', 'total_output': '0.0121295', 'txid': 'c2ab9d8f4d151b771863165480ed2d6340d8f08bb5255849088f78ce67ffcbea'}}
        Example Return When Channel Not Found: {'error': {'code': -32500, 'data': {'args': [], 'command': 'channel_update', 'kwargs': {'bid': '0.005', 'claim_id': '', 'clear_languages': True, 'clear_tags': True, 'cover_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Test-Logo.svg/783px-Test-Logo.svg.png', 'description': "Tiff's Channel for Testing things", 'email': 'test@tiff.tech', 'featured': [], 'languages': [], 'replace': True, 'tags': [], 'thumbnail_url': 'https://e7.pngegg.com/pngimages/575/704/png-clipart-computer-icons-test-scalable-graphics-test-score-angle-pencil-thumbnail.png', 'title': 'Tiff Test Channel Updated', 'website_url': 'http://google.com'}, 'name': 'Exception', 'traceback': ['Traceback (most recent call last):', '  File "lbry\\extras\\daemon\\daemon.py", line 752, in _process_rpc_call', '  File "lbry\\extras\\daemon\\daemon.py", line 2824, in jsonrpc_channel_update', "Exception: Can't find the channel '' in account(s) 'bZkN7AQZ2YRdaGgsnCfYp11ZFTg1bg9o3D', 'bTRr9fjH87FbWQ8aaPtBc7LwofA2YBtRj4', 'bZcpngoM832zRMhrSgE1ZQzk2Kipu9gSGC', 'bU2K1YaFywwj9n3msswAMzBfHYDV8nJBbW', 'bZjBTGehFi3GSt9eZyQbcX1uyw8iZRN71i', 'bFjUVQYBrC4ExmaunhsEraEx8MSwvRbhWD', 'bY7nD4vBxbXZghJWxt76sputpr5dzHbmiL', 'bSScgcW5bQnScnokcJhcA8j8Q5zgQUztDD', 'baKez6UL7D2CFDywBr5vDPJqNCc4HvDQD3', 'bW6NWXZn3C3Ag6WSu9pb2gcoKRL5SX1wL7'.", '']}, 'message': "Can't find the channel '' in account(s) 'bZkN7AQZ2YRdaGgsnCfYp11ZFTg1bg9o3D', 'bTRr9fjH87FbWQ8aaPtBc7LwofA2YBtRj4', 'bZcpngoM832zRMhrSgE1ZQzk2Kipu9gSGC', 'bU2K1YaFywwj9n3msswAMzBfHYDV8nJBbW', 'bZjBTGehFi3GSt9eZyQbcX1uyw8iZRN71i', 'bFjUVQYBrC4ExmaunhsEraEx8MSwvRbhWD', 'bY7nD4vBxbXZghJWxt76sputpr5dzHbmiL', 'bSScgcW5bQnScnokcJhcA8j8Q5zgQUztDD', 'baKez6UL7D2CFDywBr5vDPJqNCc4HvDQD3', 'bW6NWXZn3C3Ag6WSu9pb2gcoKRL5SX1wL7'."}, 'jsonrpc': '2.0'}
        """
        parameters = dict(
            claim_id=claim_id,
            bid=str(bid),
            title=title,
            description=description,
            email=email,
            website_url=website_url,
            featured=featured,
            tags=tags,
            clear_tags=clear_tags,
            clear_languages=clear_languages,
            thumbnail_url=thumbnail_url,
            languages=languages,
            cover_url=cover_url,
            replace=replace
        )
        
        result = requests.post(LBRY.API_URL,
                               json={"method": "channel_update",
                                     "params": parameters}).json()
        
        m=f"channel_update call with params: {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_file_delete(self, delete_from_download_dir : bool = False,
                        delete_all : bool = False, sd_hash : str = '',
                        file_name : str = '', claim_id : str = '',
                        claim_name : str = ''):
        """
        Method to make a file_delete call to the LBRY API
        Example Call: api_file_delete(claim_id='1ef601ec82b58b457214acf167583fc3fad079bd')
        Example Good Return: {'jsonrpc': '2.0', 'result': True}
        Example Bad Return: {'jsonrpc': '2.0', 'result': False}
        """
        parameters = dict(
            delete_from_download_dir=delete_from_download_dir,
            delete_all=delete_all
        )
        
        if not(sd_hash == '' or sd_hash is None):
            parameters['sd_hash'] = sd_hash
        
        if not(file_name == '' or file_name is None):
            parameters['file_name'] = file_name
            
        if not(claim_id == '' or claim_id is None):
            parameters['claim_id'] = claim_id
            
        if not(claim_name == '' or claim_name is None):
            parameters['claim_name'] = claim_name
        
        if not(len(parameters) > 2):
            self.logger.error("Must provide something to delete")
            return
        
        result = requests.post(LBRY.API_URL,
                               json={"method": "file_delete",
                                     "params": parameters}).json()
        
        m=f"file_delete call with parameters {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_file_save(self, download_directory : str,
                      claim_id : str, file_name : str = ''):
        """
        Method to make a file_save call to the LBRY API
        Example Call: api_file_save(download_directory=os.getcwd(),
                                    claim_id='1ef601ec82b58b457214acf167583fc3fad079bd')
        Example Return: {'jsonrpc': '2.0', 'result': {'added_on': 1646318291, 'blobs_completed': 9, 'blobs_in_stream': 139, 'blobs_remaining': 130, 'channel_claim_id': '92b7f813e4210a06fc55968dbea36e5f1f095e6d', 'channel_name': '@ComputingForever', 'claim_id': '1ef601ec82b58b457214acf167583fc3fad079bd', 'claim_name': 'hitat-2-3-2022-Broadband-High', 'completed': False, 'confirmations': 470, 'content_fee': None, 'download_directory': 'D:\\Python\\workspace\\Content Creator Manager\\src\\test', 'download_path': 'D:\\Python\\workspace\\Content Creator Manager\\src\\test\\hitat-2-3-2022-Broadband High.mp4', 'file_name': 'hitat-2-3-2022-Broadband High.mp4', 'height': 1120356, 'is_fully_reflected': True, 'key': '9e6ec5180383afa0ce8cf6647e0465bb', 'metadata': {'description': 'Sign-up to Nord VPN here: http://nordvpn.org/computingforever\n\nSupport my work on Subscribe Star: https://www.subscribestar.com/dave-cullen\nSupport my work via crypto: https://computingforever.com/donate/\nFollow me on Bitchute: https://www.bitchute.com/channel/hybM74uIHJKg/\n\nThomas Sheridan’s video: Some Curious Observations: https://www.youtube.com/watch?v=eV6ZPjyZI_0\n\nSources: https://computingforever.com/2022/03/02/how-is-this-a-thing-2nd-march-2022/\n\nhttp://www.computingforever.com\nKEEP UP ON SOCIAL MEDIA:\nGab: https://gab.ai/DaveCullen\nSubscribe on Gab TV: https://tv.gab.com/channel/DaveCullen\nMinds.com: https://www.minds.com/davecullen\nSubscribe on Odysee: https://odysee.com/@TheDaveCullenShow:7\nTelegram: https://t.me/ComputingForeverOfficial\n\nThis video contains images and videos sourced from pixabay.com:\n\nhttps://pixabay.com/photos/woman-face-mask-protection-5693746/\nhttps://pixabay.com/photos/mask-protection-virus-pandemic-4934337/\nhttps://pixabay.com/photos/coronavirus-covid-covid-19-pandemic-4947210/\nhttps://pixabay.com/photos/mouth-guard-infection-purchasing-5068146/\nhttps://pixabay.com/videos/heart-medical-treatment-ecg-health-32264/\nhttps://pixabay.com/photos/bowl-breakfast-fruits-healthy-food-1844894/\nhttps://pixabay.com/photos/joint-blunt-smoke-ashtray-cannabis-6535558/\nhttps://pixabay.com/videos/snowfall-snow-snowflakes-2362/\nhttps://pixabay.com/videos/ireland-athletics-sea-running-22913/\nhttps://pixabay.com/photos/shoveling-man-snow-work-male-tool-17328/\nhttps://pixabay.com/photos/vaccination-syringe-mask-vaccine-6576827/\nhttps://pixabay.com/videos/flag-russia-flag-of-russia-tricolor-41903/\nhttps://pixabay.com/videos/ukraine-flag-ukraine-flag-kiev-109053/\nhttps://pixabay.com/videos/earth-globe-country-africa-asia-1393/\n', 'languages': ['en'], 'license': 'None', 'release_time': '1646240461', 'source': {'hash': 'b17cf22cb42351f77300c100f5f348a336335fc693cc84266000eea7af2e0d4791b80c26e2e3b0db3878e21f34492f5b', 'media_type': 'video/mp4', 'name': 'hitat-2-3-2022-Broadband High.mp4', 'sd_hash': '2a3ff07adabe0086a67bd3dac69435d224bdd4dd691cca216dc91fd9aa7b9f80875dcab3041c9d26c70a53eafde10b89', 'size': '289797482'}, 'stream_type': 'video', 'tags': ['computing forever', 'dave cullen'], 'thumbnail': {'url': 'https://thumbs.odycdn.com/8d3d6a0076cb09ad7478eb8bc7097a0e.jpg'}, 'title': 'How is This a Thing? 2nd March 2022', 'video': {'duration': 751, 'height': 720, 'width': 1280}}, 'mime_type': 'video/mp4', 'nout': 0, 'outpoint': '5bd19409c7b9cfbc3ac5a33d8928c766db061620336d1d955fe082ea38fb64f5:0', 'points_paid': 0.0, 'protobuf': '016d5e091f5f6ea3be8d9655fc060a21e413f8b79226f86f0ef1419dbd6ba19930aca6ba907e4438119d5776da11c6dde391551ab1f00cf37f7a6bc20d7ce334e95b6757ac9fd786f21449aee75d95ac8386a33cc20ab2010a98010a30b17cf22cb42351f77300c100f5f348a336335fc693cc84266000eea7af2e0d4791b80c26e2e3b0db3878e21f34492f5b122168697461742d322d332d323032322d42726f616462616e6420486967682e6d703418eaea978a012209766964656f2f6d703432302a3ff07adabe0086a67bd3dac69435d224bdd4dd691cca216dc91fd9aa7b9f80875dcab3041c9d26c70a53eafde10b891a044e6f6e6528cdc5fe90065a0908800a10d00518ef054223486f7720697320546869732061205468696e673f20326e64204d6172636820323032324ae90d5369676e2d757020746f204e6f72642056504e20686572653a20687474703a2f2f6e6f726476706e2e6f72672f636f6d707574696e67666f72657665720a0a537570706f7274206d7920776f726b206f6e2053756273637269626520537461723a2068747470733a2f2f7777772e737562736372696265737461722e636f6d2f646176652d63756c6c656e0a537570706f7274206d7920776f726b207669612063727970746f3a2068747470733a2f2f636f6d707574696e67666f72657665722e636f6d2f646f6e6174652f0a466f6c6c6f77206d65206f6e2042697463687574653a2068747470733a2f2f7777772e62697463687574652e636f6d2f6368616e6e656c2f6879624d37347549484a4b672f0a0a54686f6d617320536865726964616ee280997320766964656f3a20536f6d6520437572696f7573204f62736572766174696f6e733a2068747470733a2f2f7777772e796f75747562652e636f6d2f77617463683f763d6556365a506a795a495f300a0a536f75726365733a2068747470733a2f2f636f6d707574696e67666f72657665722e636f6d2f323032322f30332f30322f686f772d69732d746869732d612d7468696e672d326e642d6d617263682d323032322f0a0a687474703a2f2f7777772e636f6d707574696e67666f72657665722e636f6d0a4b454550205550204f4e20534f4349414c204d454449413a0a4761623a2068747470733a2f2f6761622e61692f4461766543756c6c656e0a537562736372696265206f6e204761622054563a2068747470733a2f2f74762e6761622e636f6d2f6368616e6e656c2f4461766543756c6c656e0a4d696e64732e636f6d3a2068747470733a2f2f7777772e6d696e64732e636f6d2f6461766563756c6c656e0a537562736372696265206f6e204f64797365653a2068747470733a2f2f6f64797365652e636f6d2f405468654461766543756c6c656e53686f773a370a54656c656772616d3a2068747470733a2f2f742e6d652f436f6d707574696e67466f72657665724f6666696369616c0a0a5468697320766964656f20636f6e7461696e7320696d6167657320616e6420766964656f7320736f75726365642066726f6d20706978616261792e636f6d3a0a0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f776f6d616e2d666163652d6d61736b2d70726f74656374696f6e2d353639333734362f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f6d61736b2d70726f74656374696f6e2d76697275732d70616e64656d69632d343933343333372f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f636f726f6e6176697275732d636f7669642d636f7669642d31392d70616e64656d69632d343934373231302f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f6d6f7574682d67756172642d696e66656374696f6e2d70757263686173696e672d353036383134362f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f68656172742d6d65646963616c2d74726561746d656e742d6563672d6865616c74682d33323236342f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f626f776c2d627265616b666173742d6672756974732d6865616c7468792d666f6f642d313834343839342f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f6a6f696e742d626c756e742d736d6f6b652d617368747261792d63616e6e616269732d363533353535382f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f736e6f7766616c6c2d736e6f772d736e6f77666c616b65732d323336322f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f6972656c616e642d6174686c65746963732d7365612d72756e6e696e672d32323931332f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f73686f76656c696e672d6d616e2d736e6f772d776f726b2d6d616c652d746f6f6c2d31373332382f0a68747470733a2f2f706978616261792e636f6d2f70686f746f732f76616363696e6174696f6e2d737972696e67652d6d61736b2d76616363696e652d363537363832372f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f666c61672d7275737369612d666c61672d6f662d7275737369612d747269636f6c6f722d34313930332f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f756b7261696e652d666c61672d756b7261696e652d666c61672d6b6965762d3130393035332f0a68747470733a2f2f706978616261792e636f6d2f766964656f732f65617274682d676c6f62652d636f756e7472792d6166726963612d617369612d313339332f0a52402a3e68747470733a2f2f7468756d62732e6f647963646e2e636f6d2f38643364366130303736636230396164373437386562386263373039376130652e6a70675a11636f6d707574696e6720666f72657665725a0b646176652063756c6c656e62020801', 'purchase_receipt': None, 'reflector_progress': 0, 'sd_hash': '2a3ff07adabe0086a67bd3dac69435d224bdd4dd691cca216dc91fd9aa7b9f80875dcab3041c9d26c70a53eafde10b89', 'status': 'running', 'stopped': False, 'stream_hash': 'd4076694abf6ab1c095c394f466858c1e99df4338f87068a8b8bee717f96bb75a0db941173f1852fd0b31a5f4b8153a9', 'stream_name': 'hitat-2-3-2022-Broadband High.mp4', 'streaming_url': 'http://localhost:5280/stream/2a3ff07adabe0086a67bd3dac69435d224bdd4dd691cca216dc91fd9aa7b9f80875dcab3041c9d26c70a53eafde10b89', 'suggested_file_name': 'hitat-2-3-2022-Broadband High.mp4', 'timestamp': 1646242133, 'total_bytes': 289797494, 'total_bytes_lower_bound': 289797478, 'txid': '5bd19409c7b9cfbc3ac5a33d8928c766db061620336d1d955fe082ea38fb64f5', 'uploading_to_reflector': False, 'written_bytes': 2097151}}
        Example Return if you try to save a file when blobs are not on the system or claim_id is not found: {'jsonrpc': '2.0', 'result': False}
        """
        parameters = dict(
            download_directory=download_directory,
            claim_id=claim_id
        )
        
        if not(file_name == '' or file_name is None):
            parameters['file_name'] = file_name
        
        result = requests.post(LBRY.API_URL,
                               json={"method": "file_save",
                                     "params": parameters}).json()
        
        m=f"file_save call with params: {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_stream_abandon(self, claim_id : str):
        """
        Method to make a stream_abandon call to the LBRY API
        Example Call: api_stream_abandon(claim_id='9df6f11c4581dc4deb48246582c638e4c7576af2')
        Example Return: {'jsonrpc': '2.0', 'result': {'height': -2, 'hex': '01000000011117b3f455c31227275048dce10309a1e752e9b97de300e4607d4eb2faffae76000000006b483045022100d7d1c4678b9bf1f9cb55f1cfaef2b45738b314615ef88755423e1749dd726cdf022006292036ab9a6775c8e7f5218f726089bda759afafb8e570395332903ab3ff24012103a5dc7286cfceb5f92a4732c842262ed7fbcc8ac07b90f2035d9aab239fa6d17bffffffff0174e30200000000001976a914ebd03f818f1820d7bcafb00d9327ed6334ca775d88ac00000000', 'inputs': [{'address': 'bStGY1KcMifPvtNWjh5mDkfnD57qvU53sm', 'amount': '0.002', 'claim_id': '9df6f11c4581dc4deb48246582c638e4c7576af2', 'claim_op': 'update', 'confirmations': 1, 'height': 1120820, 'meta': {}, 'name': 'ContentCreatorManagerTestUpload', 'normalized_name': 'contentcreatormanagertestupload', 'nout': 0, 'permanent_url': 'lbry://ContentCreatorManagerTestUpload#9df6f11c4581dc4deb48246582c638e4c7576af2', 'timestamp': 1646317805, 'txid': '76aefffab24e7d60e400e37db9e952e7a10903e1dc4850272712c355f4b31711', 'type': 'claim', 'value': {'description': 'new description', 'languages': ['en'], 'source': {'hash': '2015599953d2274b728d8d75afb970956785669a039fc57952d58931b01d6c2b1233bdc613d1e271e7b9b2c70ce936f0', 'media_type': 'video/mp4', 'name': 'upload_test.mp4', 'sd_hash': '503bee2b0ce3fd5f4e7fd50db8b04461a15542513b23b45f4d0a992e064ac3bf571b2b400187000c1f45d5dcd239431f', 'size': '1181789'}, 'stream_type': 'video', 'tags': ['newtag'], 'title': 'New Title', 'video': {'duration': 5, 'height': 720, 'width': 1280}}, 'value_type': 'stream'}], 'outputs': [{'address': 'baE8xe6vxpWzH8gL3H9JCtHPuLDpAh1fWR', 'amount': '0.001893', 'confirmations': -2, 'height': -2, 'nout': 0, 'timestamp': None, 'txid': '29202c96652a2f6172b0f9283babaaf2fc1635d6e4ab2542523401d8153434b6', 'type': 'payment'}], 'total_fee': '0.000107', 'total_input': '0.002', 'total_output': '0.001893', 'txid': '29202c96652a2f6172b0f9283babaaf2fc1635d6e4ab2542523401d8153434b6'}}
        """
        parameters = dict(
            claim_id=claim_id
        )
        
        result = requests.post(LBRY.API_URL,
                               json={"method": "stream_abandon",
                                     "params": parameters}).json()
        
        m=f"stream_abandon call with params: {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_stream_create(self, name : str, bid : float, file_path : str,
                          title : str, description: str, channel_id : str,
                          languages : list = [], tags : list = [],
                          thumbnail_url : str = '', lic : str = '',
                          license_url : str = ''):
        """
        Method to make a stream_create call to the LBRY API
        Example Call: api_stream_create(name='newapimethodstestupload',
                                        bid=.001, file_path=os.path.join(os.getcwd(),
                                        'upload_test.mp4'), title="Yet another test",
                                        description="Test Description",
                                        channel_id='8be45e4ba05bd6961619489f6408a0dc62f4e650',
                                        languages=['en'], tags=['test'])
        Example Return: {'jsonrpc': '2.0', 'result': {'height': -2, 'hex': '0100000001d7d6df32ce66e0c8fd4af18e8477d7033d294c660f99628c04dcbc5862b0c2ca010000006a47304402205cac40078d903ee0e70d0af2eca035e1e73c69756c5f45cc054220bb4802d1bf02206d811fe44160ea932eebef556ebeab5b136c7e9ec7dc74d5c0e949f9594334d801210389cdb09a4f17e2eb286aba8fd2e96c11392bc08cda0a10d4db8b5136b86749acffffffff02a086010000000000fd4e01b5176e65776170696d6574686f64737465737475706c6f61644d17010150e6f462dca008649f48191696d65ba04b5ee48bbb76ead9be638875cff624dd950aeb75d0b929501853c863903b79a1078786169d6d76d9957b64eeb1da592acc3d2c49041a57e65295d67b16c25533c813d1810a91010a84010a302015599953d2274b728d8d75afb970956785669a039fc57952d58931b01d6c2b1233bdc613d1e271e7b9b2c70ce936f0120f75706c6f61645f746573742e6d703418dd90482209766964656f2f6d7034323010ee171b5dc87c333f51779ac5fdeace1e507ffc4509522dfbac5de26e5af7f2dcb692358ba01914b2edc78f397387635a0808800a10d0051805421059657420616e6f7468657220746573744a1054657374204465736372697074696f6e5a0474657374620208016d7576a91471a0054e53b7c6ddc44cc6a88d986412654e369d88ac7cd91c01000000001976a914fbf53033340135fd734f11dcc3fe41eae2f9426c88ac00000000', 'inputs': [{'address': 'bRC7ZEbsUAMQMKR2z6HzADb63YqkoVro5s', 'amount': '0.233786', 'confirmations': 1375, 'height': 1119445, 'nout': 1, 'timestamp': 1646095859, 'txid': 'cac2b06258bcdc048c62990f664c293d03d777848ef14afdc8e066ce32dfd6d7', 'type': 'payment'}], 'outputs': [{'address': 'bP64kLpgUdYCcZwMFJqrw9XA1RqbCbTbyp', 'amount': '0.001', 'claim_id': '5dfe9bbb8b8b82cc9cd2d4d32c3c10fa0e707388', 'claim_op': 'create', 'confirmations': -2, 'height': -2, 'is_channel_signature_valid': True, 'meta': {}, 'name': 'newapimethodstestupload', 'normalized_name': 'newapimethodstestupload', 'nout': 0, 'permanent_url': 'lbry://newapimethodstestupload#5dfe9bbb8b8b82cc9cd2d4d32c3c10fa0e707388', 'signing_channel': {'address': 'bFR3HtPv3TqNRp8KQt1TZueZABnjos2WyB', 'amount': '0.001', 'claim_id': '8be45e4ba05bd6961619489f6408a0dc62f4e650', 'claim_op': 'create', 'confirmations': 176950, 'has_signing_key': True, 'height': 943870, 'meta': {}, 'name': '@Tiff_Tech_Test_Channel', 'normalized_name': '@tiff_tech_test_channel', 'nout': 0, 'permanent_url': 'lbry://@Tiff_Tech_Test_Channel#8be45e4ba05bd6961619489f6408a0dc62f4e650', 'timestamp': 1618163141, 'txid': 'a7b0f33560d2bead42f97d806ff8a75b9912ad2ba3abc8ff39212f9a5d31e6ed', 'type': 'claim', 'value': {'description': 'Channel to use for testing stuff with the API/SDK', 'email': 'test@tiff.tech', 'public_key': '3056301006072a8648ce3d020106052b8104000a03420004a922acec8cbff92392a0d5d206c9334f5b99b90143594d98fef4dc085d6917e68417c8b0fb67732266a5bc4b97785e256e6f2dedc3cbf4c269b0d7aabc1f3365', 'public_key_id': 'bHrJFge6cs7rhv8GknD1RGCWYPhDduC2Mj', 'title': 'Tiff_Tech_Test_Channel'}, 'value_type': 'channel'}, 'timestamp': None, 'txid': 'c6aa60f52af1701769fd7ef21dcf9ade7cbdddc63af1e538bd8c9030eb96032e', 'type': 'claim', 'value': {'description': 'Test Description', 'languages': ['en'], 'source': {'hash': '2015599953d2274b728d8d75afb970956785669a039fc57952d58931b01d6c2b1233bdc613d1e271e7b9b2c70ce936f0', 'media_type': 'video/mp4', 'name': 'upload_test.mp4', 'sd_hash': '10ee171b5dc87c333f51779ac5fdeace1e507ffc4509522dfbac5de26e5af7f2dcb692358ba01914b2edc78f39738763', 'size': '1181789'}, 'stream_type': 'video', 'tags': ['test'], 'title': 'Yet another test', 'video': {'duration': 5, 'height': 720, 'width': 1280}}, 'value_type': 'stream'}, {'address': 'bbhW2MsQdsqWNgjU8r1itnyJyLDyQpjkt7', 'amount': '0.186679', 'confirmations': -2, 'height': -2, 'nout': 1, 'timestamp': None, 'txid': 'c6aa60f52af1701769fd7ef21dcf9ade7cbdddc63af1e538bd8c9030eb96032e', 'type': 'payment'}], 'total_fee': '0.046107', 'total_input': '0.233786', 'total_output': '0.187679', 'txid': 'c6aa60f52af1701769fd7ef21dcf9ade7cbdddc63af1e538bd8c9030eb96032e'}}
        """
        parameters = dict(
            name=name,
            bid=str(bid),
            file_path=file_path,
            description=description,
            title=title,
            tags=tags,
            languages=languages,
            channel_id=channel_id,
            thumbnail_url=thumbnail_url,
            license=lic,
            license_url=license_url
        )
        
        result = requests.post(LBRY.API_URL,
                               json={"method": "stream_create",
                                     "params": parameters}).json()
        
        m=f"stream_create call with params: {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_stream_update(self, claim_id : str, bid : float, title : str,
                          description : str, tags : list, languages : list,
                          channel_id : str, clear_languages : bool = True, 
                          clear_tags : bool = True, replace : bool = False,
                          thumbnail_url : str = '', file_path : str = '',
                          lic : str = '', license_url : str = ''):
        """
        Method to make a stream_update call to the LBRY API
        Example Call: api_stream_update(claim_id='9df6f11c4581dc4deb48246582c638e4c7576af2',
                                        bid=0.002, title='New Title',
                                        description='new description',
                                        tags=['newtag'], languages=['en'],
                                        channel_id='8be45e4ba05bd6961619489f6408a0dc62f4e650')
        Example Return: {'jsonrpc': '2.0', 'result': {'height': -2, 'hex': '0100000002c57d34462cd751ae92c52c5a72a051721be6b04359c33773f56f076dc9dee3b8000000006a47304402202ca2151de46bc8bbf267f4a308c30e4459bf0bbdf0d895a2c85f3d44ab9d61a3022046be4679c5c0ff19f1c3bc5de0868bc8a99158d95a93c3666777c359cf14a541012103a5dc7286cfceb5f92a4732c842262ed7fbcc8ac07b90f2035d9aab239fa6d17bffffffffd027f53a69267cf9dd5e69a6b09821d080faa7d0e2fd192495ff26bf85ccf7df010000006a47304402202a548898a41a2b45d74f54eac7487f2439128fb391ec2cb3536f7041abf91ce102206d58409630f9f1d274f469de58a832c87fccb4f2368089d6005ab3fdb16785f401210242f047bd8b9d56d7e6aaac523066ebf1bb98b55b600700d89ee33f59ebcbca17ffffffff02400d030000000000fd6501b71f436f6e74656e7443726561746f724d616e616765725465737455706c6f616414f26a57c7e438c682652448eb4ddc81451cf1f69d4d11010150e6f462dca008649f48191696d65ba04b5ee48b334957530bf04956d8eb5298461a675f0bf642754b50fd99298450cc099a009b2e9580199671ddf4e164b6c1068299d016eb1ab9776e2ee4a5730b3ba3aa5a4c0a91010a84010a302015599953d2274b728d8d75afb970956785669a039fc57952d58931b01d6c2b1233bdc613d1e271e7b9b2c70ce936f0120f75706c6f61645f746573742e6d703418dd90482209766964656f2f6d70343230503bee2b0ce3fd5f4e7fd50db8b04461a15542513b23b45f4d0a992e064ac3bf571b2b400187000c1f45d5dcd239431f5a0808800a10d005180542094e6577205469746c654a0f6e6577206465736372697074696f6e5a066e6577746167620208016d6d76a9149b455f32bccc6f164f60990e83261813fd6942cc88ac94a51100000000001976a9146b656edf853ca66345793a66a7ad7aabf7899c8a88ac00000000', 'inputs': [{'address': 'bStGY1KcMifPvtNWjh5mDkfnD57qvU53sm', 'amount': '0.001', 'claim_id': '9df6f11c4581dc4deb48246582c638e4c7576af2', 'claim_op': 'update', 'confirmations': 1494, 'height': 1119326, 'meta': {}, 'name': 'ContentCreatorManagerTestUpload', 'normalized_name': 'contentcreatormanagertestupload', 'nout': 0, 'permanent_url': 'lbry://ContentCreatorManagerTestUpload#9df6f11c4581dc4deb48246582c638e4c7576af2', 'timestamp': 1646076040, 'txid': 'b8e3dec96d076ff57337c35943b0e61b7251a0725a2cc592ae51d72c46347dc5', 'type': 'claim', 'value': {'description': 'All this is done by the app', 'languages': ['en'], 'source': {'hash': '2015599953d2274b728d8d75afb970956785669a039fc57952d58931b01d6c2b1233bdc613d1e271e7b9b2c70ce936f0', 'media_type': 'video/mp4', 'name': 'upload_test.mp4', 'sd_hash': '503bee2b0ce3fd5f4e7fd50db8b04461a15542513b23b45f4d0a992e064ac3bf571b2b400187000c1f45d5dcd239431f', 'size': '1181789'}, 'stream_type': 'video', 'tags': ['uploadtest', 'contentcreatormanager'], 'thumbnail': {}, 'title': 'THis is a reupload after deleting this video', 'video': {'duration': 5, 'height': 720, 'width': 1280}}, 'value_type': 'stream'}, {'address': 'bRYeTpzomKR5diLxPhErozMwkT2senB3y4', 'amount': '0.01293', 'confirmations': 3219, 'height': 1117601, 'nout': 1, 'timestamp': 1645799858, 'txid': 'dff7cc85bf26ff952419fde2d0a7fa80d02198b0a6695eddf97c26693af527d0', 'type': 'payment'}], 'outputs': [{'address': 'bStGY1KcMifPvtNWjh5mDkfnD57qvU53sm', 'amount': '0.002', 'claim_id': '9df6f11c4581dc4deb48246582c638e4c7576af2', 'claim_op': 'update', 'confirmations': -2, 'height': -2, 'is_channel_signature_valid': True, 'meta': {}, 'name': 'ContentCreatorManagerTestUpload', 'normalized_name': 'contentcreatormanagertestupload', 'nout': 0, 'permanent_url': 'lbry://ContentCreatorManagerTestUpload#9df6f11c4581dc4deb48246582c638e4c7576af2', 'signing_channel': {'address': 'bFR3HtPv3TqNRp8KQt1TZueZABnjos2WyB', 'amount': '0.001', 'claim_id': '8be45e4ba05bd6961619489f6408a0dc62f4e650', 'claim_op': 'create', 'confirmations': 176950, 'has_signing_key': True, 'height': 943870, 'meta': {}, 'name': '@Tiff_Tech_Test_Channel', 'normalized_name': '@tiff_tech_test_channel', 'nout': 0, 'permanent_url': 'lbry://@Tiff_Tech_Test_Channel#8be45e4ba05bd6961619489f6408a0dc62f4e650', 'timestamp': 1618163141, 'txid': 'a7b0f33560d2bead42f97d806ff8a75b9912ad2ba3abc8ff39212f9a5d31e6ed', 'type': 'claim', 'value': {'description': 'Channel to use for testing stuff with the API/SDK', 'email': 'test@tiff.tech', 'public_key': '3056301006072a8648ce3d020106052b8104000a03420004a922acec8cbff92392a0d5d206c9334f5b99b90143594d98fef4dc085d6917e68417c8b0fb67732266a5bc4b97785e256e6f2dedc3cbf4c269b0d7aabc1f3365', 'public_key_id': 'bHrJFge6cs7rhv8GknD1RGCWYPhDduC2Mj', 'title': 'Tiff_Tech_Test_Channel'}, 'value_type': 'channel'}, 'timestamp': None, 'txid': '76aefffab24e7d60e400e37db9e952e7a10903e1dc4850272712c355f4b31711', 'type': 'claim', 'value': {'description': 'new description', 'languages': ['en'], 'source': {'hash': '2015599953d2274b728d8d75afb970956785669a039fc57952d58931b01d6c2b1233bdc613d1e271e7b9b2c70ce936f0', 'media_type': 'video/mp4', 'name': 'upload_test.mp4', 'sd_hash': '503bee2b0ce3fd5f4e7fd50db8b04461a15542513b23b45f4d0a992e064ac3bf571b2b400187000c1f45d5dcd239431f', 'size': '1181789'}, 'stream_type': 'video', 'tags': ['newtag'], 'title': 'New Title', 'video': {'duration': 5, 'height': 720, 'width': 1280}}, 'value_type': 'stream'}, {'address': 'bNX8WTAAYFSWTqKpVD1SzWHRbuJnmKFF14', 'amount': '0.011565', 'confirmations': -2, 'height': -2, 'nout': 1, 'timestamp': None, 'txid': '76aefffab24e7d60e400e37db9e952e7a10903e1dc4850272712c355f4b31711', 'type': 'payment'}], 'total_fee': '0.000365', 'total_input': '0.01393', 'total_output': '0.013565', 'txid': '76aefffab24e7d60e400e37db9e952e7a10903e1dc4850272712c355f4b31711'}}
        """
        parameters = dict(
            claim_id=claim_id,
            bid=str(bid),
            title=title,
            description=description,
            tags=tags,
            languages=languages,
            channel_id=channel_id,
            replace=replace,
            clear_tags=clear_tags,
            clear_languages=clear_languages,
            thumbnail_url = thumbnail_url,
            license=lic,
            license_url=license_url
        )
        
        if not (file_path == '' or file_path is None):
            parameters['file_path'] = file_path
        
        result = requests.post(LBRY.API_URL,
                               json={"method": "stream_update",
                                     "params": parameters}).json()
        
        m=f"stream_update call with params: {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_claim_list(self, claim_type : list = [], claim_id : list = [],
                       channel_id: list = [], name : list = [],
                       account_id : str = '', order_by : str = '',
                       page : int = 0, resolve : bool = True,
                       page_size: int = PAGE_RESULT_LENGTH):
        """
        Method to make a claim_list call to the LBRY API
        Example Call: api_claim_list(claim_id=['0986a13ef9d562c9daa5793fcd33a41d929cd403'])
        Example Return: {'jsonrpc': '2.0', 'result': {'items': [{'address': 'bFxUNfmMUbqnPqnYFEpZ8r2BrutvhG47PF', 'amount': '0.001', 'canonical_url': 'lbry://@Tiff_Tech_Test_Channel#8/TestLBRYPostAboutTestVideo#0', 'claim_id': '0986a13ef9d562c9daa5793fcd33a41d929cd403', 'claim_op': 'create', 'confirmations': 1359, 'height': 1119445, 'is_channel_signature_valid': True, 'is_internal_transfer': False, 'is_my_input': True, 'is_my_output': True, 'is_spent': False, 'meta': {'activation_height': 1119445, 'creation_height': 1119445, 'creation_timestamp': 1646095859, 'effective_amount': '0.001', 'expiration_height': 3221845, 'is_controlling': True, 'reposted': 0, 'support_amount': '0.0', 'take_over_height': 1119445}, 'name': 'TestLBRYPostAboutTestVideo', 'normalized_name': 'testlbrypostabouttestvideo', 'nout': 0, 'permanent_url': 'lbry://TestLBRYPostAboutTestVideo#0986a13ef9d562c9daa5793fcd33a41d929cd403', 'short_url': 'lbry://TestLBRYPostAboutTestVideo#0', 'signing_channel': {'address': 'bFR3HtPv3TqNRp8KQt1TZueZABnjos2WyB', 'amount': '0.001', 'claim_id': '8be45e4ba05bd6961619489f6408a0dc62f4e650', 'claim_op': 'create', 'confirmations': 176934, 'has_signing_key': True, 'height': 943870, 'meta': {}, 'name': '@Tiff_Tech_Test_Channel', 'normalized_name': '@tiff_tech_test_channel', 'nout': 0, 'permanent_url': 'lbry://@Tiff_Tech_Test_Channel#8be45e4ba05bd6961619489f6408a0dc62f4e650', 'timestamp': 1618163141, 'txid': 'a7b0f33560d2bead42f97d806ff8a75b9912ad2ba3abc8ff39212f9a5d31e6ed', 'type': 'claim', 'value': {'description': 'Channel to use for testing stuff with the API/SDK', 'email': 'test@tiff.tech', 'public_key': '3056301006072a8648ce3d020106052b8104000a03420004a922acec8cbff92392a0d5d206c9334f5b99b90143594d98fef4dc085d6917e68417c8b0fb67732266a5bc4b97785e256e6f2dedc3cbf4c269b0d7aabc1f3365', 'public_key_id': 'bHrJFge6cs7rhv8GknD1RGCWYPhDduC2Mj', 'title': 'Tiff_Tech_Test_Channel'}, 'value_type': 'channel'}, 'timestamp': 1646095859, 'txid': 'cac2b06258bcdc048c62990f664c293d03d777848ef14afdc8e066ce32dfd6d7', 'type': 'claim', 'value': {'languages': ['en'], 'source': {'hash': '2c2227dd7ce54b4a7812750daf47c18838afa9987221d9851eefe30da25cc2907ba3e07d5eb4a8030e1c2d711a943e9d', 'media_type': 'text/markdown', 'name': 'TestLBRYPostAboutTestVideo.md', 'sd_hash': 'aef0e62330bf19d8a1a74490789620e8adca2195a9517f8b24a91a299c4a04f3d3146d66249a696481ca6952ee7db1e7', 'size': '189'}, 'stream_type': 'document', 'tags': ['testposttag'], 'thumbnail': {}, 'title': 'Test LBRY Post About Test Video'}, 'value_type': 'stream'}], 'page': 1, 'page_size': 20, 'total_items': 1, 'total_pages': 1}}
        """
        parameters = dict(
            claim_type=claim_type,
            claim_id=claim_id,
            channel_id=channel_id,
            name=name,
            page_size=page_size,
            resolve=resolve,
        )
        
        if not (account_id == '' or account_id is None):
            parameters['account_id']=account_id
        
        if not (page == 0 or page is None):
            parameters['page']=page
        
        if not (order_by == '' or order_by is None):
            parameters['order_by']=order_by
        
        
        result = requests.post(LBRY.API_URL,
                               json={"method": "claim_list",
                                     "params": parameters}).json()
        
        m=f"claim_list call with params: {parameters} made to the LBRY API"
        self.logger.info(m)
        
        return result
    
    def api_upload_thumb(self, file : str):
        """
        Use API to upload a thumbnail to LBRY using spee.ch
        """
        name = shortuuid.ShortUUID().random(length=24)
        
        files = {
            'name': (None, name),
            'file': (file, open(file, 'rb'))
        }
        
        response = requests.post(LBRY.LBRY_THUMB_API_URL, files=files)
        
        return response.json()