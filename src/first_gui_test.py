import tkinter as tk
import tkinter.filedialog as tk_fd
import os.path
import shutil
import contentcreatormanager.config as config
import contentcreatormanager.platform.youtube as yt_plat
import contentcreatormanager.media.video.youtube as yt_vid
import contentcreatormanager.media.video.lbry as lbry_vid
import tkinter.simpledialog as tk_sd
import json
import contentcreatormanager.platform.lbry as lbry_plat
import tkinter.ttk as ttk

class CCMApp(tk.Tk):
    
    WIDTH = 1450
    HEIGHT = 750
    
    WIN_X = 10
    WIN_Y = 10
    
    def __clear_yt_upload_lb(self):
        if len(self.yt_upload_list) > 0:
            for o in self.yt_upload_list:
                self.yt_upload_lb.delete(0)
                
    def __clear_lbry_upload_lb(self):
        if len(self.lbry_upload_list) > 0:
            for o in self.lbry_upload_list:
                self.lbry_upload_lb.delete(0)
    
    def __populate_yt_upload_lb_from_lbry(self):
        self.__clear_yt_upload_lb()
        list1 = self.lbry_plat.media_objects
        list2 = self.yt_plat.media_objects
        list3 = []
        for obj in list1:
            not_this_one = False
            for o in list2:
                if obj.title == o.title:
                    not_this_one = True
            if not not_this_one:
                yvid = yt_vid.YouTubeVideo(channel=self.yt_plat,
                                           self_declared_made_for_kids=False,
                                           made_for_kids=False,
                                           public_stats_viewable=True,
                                           embeddable=True,
                                           privacy_status='public',
                                           has_custom_thumbnail=False,
                                           title=obj.title,
                                           description=obj.description,
                                           file_name=os.path.basename(obj.file),
                                           update_from_web=False,
                                           tags=obj.tags,
                                           new_video=True)
                if not os.path.isdir(os.path.join(os.getcwd(), 'thumbs')):
                    os.makedirs('thumbs')
                thumb_dir = os.path.join(os.getcwd(), 'thumbs')
                os.chdir(thumb_dir)
                if not os.path.isfile(obj.thumbnail):
                    yvid.thumbnail = obj.download_thumb()
                else:
                    yvid.thumbnail = obj.thumbnail
                os.chdir(self.settings.folder_location)
                yvid.thumbnail = os.path.join(thumb_dir, )
                list3.append(yvid)
        count = 0
        for o in list3:
            self.yt_upload_lb.insert(count, o.title)
            count += 1
        self.yt_upload_list = list3
        return
    
    def __yt_get_lbry_not_on_yt(self, event):
        self.__populate_yt_upload_lb_from_lbry()
        return
    
    def __populate_lbry_upload_lb_from_yt(self):
        self.__clear_lbry_upload_lb()
        list1 = self.yt_plat.media_objects
        list2 = self.lbry_plat.media_objects
        list3 = []
        thumb_dir = os.path.join(os.getcwd(), 'thumbs')
        for obj in list1:
            not_this_one = False
            for o in list2:
                if obj.title == o.title:
                    not_this_one = True
            if not not_this_one:
                lvid = lbry_vid.LBRYVideo(lbry_channel=self.lbry_plat, tags=obj.tags, title=obj.title, file_name=os.path.basename(obj.file), description=obj.description, new_video=True)
                if not os.path.isdir(os.path.join(os.getcwd(), 'thumbs')):
                    os.makedirs('thumbs')
                os.chdir(thumb_dir)
                if not os.path.isfile(obj.thumbnail):
                    lvid.thumbnail = obj.download_thumb()
                else:
                    lvid.thumbnail = obj.thumbnail
                os.chdir(self.settings.folder_location)
                list3.append(lvid)
        count = 0
        for o in list3:
            self.lbry_upload_lb.insert(count, o.title)
            count += 1
        self.lbry_upload_list = list3
        return
    
    def __lbry_get_yt_not_on_lbry(self, event):
        self.__populate_lbry_upload_lb_from_yt()
        
    
    def __clear_lbry_lb(self):
        if self.lbry_plat is None:
            self.settings.logger.warning("No LBRY Platform Setup")
        elif len(self.lbry_plat.media_objects) > 0:
            for o in self.lbry_plat.media_objects:
                self.lbry_lb.delete(0)
        if len(self.lbry_vids_not_downloaded) > 0:
            for o in self.lbry_vids_not_downloaded:
                self.lbry_not_downloaded_lb.delete(0)
            
    def __clear_yt_lb(self):
        if self.yt_plat is None:
            self.settings.logger.warning("No YT Platform Setup")
        elif len(self.yt_plat.media_objects) > 0:
            for o in self.yt_plat.media_objects:
                self.yt_lb.delete(0)
        if len(self.yt_vids_not_downloaded) > 0:
            for o in self.yt_vids_not_downloaded:
                self.yt_not_downloaded_lb.delete(0)
    
    def __populate_lbry_lb(self):
        count = 0
        count_2 = 0
        self.lbry_vids_not_downloaded = []
        for o in self.lbry_plat.media_objects:
            self.settings.logger.info(f"adding entry {o.title} from lb")
            self.lbry_lb.insert(count, o.title)
            check = o.is_downloaded()
            if not check:
                self.lbry_vids_not_downloaded.append(o)
                self.lbry_not_downloaded_lb.insert(count_2, o.title)
                count_2 += 1
            count += 1
            
    
    def __populate_yt_lb(self): 
        count = 0
        count_2 = 0
        self.yt_vids_not_downloaded = []
        for o in self.yt_plat.media_objects:
            self.yt_lb.insert(count, o.title)
            check = o.is_downloaded(file_check_only=True)
            if not check:
                self.yt_vids_not_downloaded.append(o)
                self.yt_not_downloaded_lb.insert(count_2, o.title)
                count_2 += 1
            count += 1
            
    
    def __create_yt_client_secrets(self):
        secrets_json = {
            "installed":{
                "client_id":"",
                "project_id":"",
                "auth_uri":"https://accounts.google.com/o/oauth2/auth",
                "token_uri":"https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
                "client_secret":"",
                "redirect_uris":["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }}
        client_id = tk_sd.askstring("client_id", "Please enter the client id for a google project with access to the YouTube Data API v3")
        project_id = tk_sd.askstring("project_id", "Please enter the project id for a google project with access to the YouTube Data API v3")
        client_secret = tk_sd.askstring("client_secret", "Please enter the client secret for a google project with access to the YouTube Data API v3")
        secrets_json['installed']['client_id'] = client_id
        secrets_json['installed']['project_id'] = project_id
        secrets_json['installed']['client_secret'] = client_secret
        
        with open(self.yt_cred_file, 'w') as jf:
            json.dump(secrets_json, jf)
        return
    
    def __yt_init_plat(self, event):
        self.withdraw()
        self.__clear_yt_lb()
        self.yt_plat = None
        self.yt_plat = yt_plat.YouTube(settings=self.settings, init_videos=True)
        self.__populate_yt_lb()
        self.deiconify()
        return 
    
    def __setup_folder(self, folder_location: str=''):
        if folder_location == '':
            folder = tk_fd.askdirectory(title='Choose Application Directory')
        else:
            folder = folder_location
        logging_config_file = os.path.join(folder, 'logging.ini')
        if not os.path.isfile(logging_config_file):
            shutil.copy(os.path.join(os.getcwd(), 'logging.ini'), logging_config_file)
        return config.Settings(folder_location=folder, logging_config_file=logging_config_file)
    
    def __yt_api_setup(self, event):
        if os.path.isfile(self.yt_cred_file):
            self.withdraw()
            tk.messagebox.showinfo(message='YouTube Creds Already Present')
            self.deiconify()
        else:
            self.__create_yt_client_secrets()    
        return 'break'
    
    def __yt_gui_setup(self):
        
        self.yt_lbl_str = tk.StringVar()
        self.yt_lbl_str.set("YouTube Channel")
        self.yt_lbl = tk.Label(self, textvariable=self.yt_lbl_str)
        self.yt_lbl.grid(column=0, row=0, columnspan=2)
        
        self.yt_lb = tk.Listbox(self, width=80)
        self.yt_lb.grid(column=0, row=1, rowspan=3, columnspan=2)
        
        self.yt_lb_sb = tk.Scrollbar(self)
        self.yt_lb_sb.grid(column=0, row=1, rowspan=3, columnspan=2, sticky=tk.E+tk.N+tk.S)
        self.yt_lb.config(yscrollcommand=self.yt_lb_sb.set)
        self.yt_lb_sb.config(command=self.yt_lb.yview)
        
        self.yt_api_setup_btn = tk.Button(self, text="Configure API Details")
        self.yt_api_setup_btn.grid(column=0, row=4)
        self.yt_api_setup_btn.bind('<Button-1>', func=self.__yt_api_setup)
        
        self.yt_load_btn = tk.Button(self, text="Load in YouTube Data")
        self.yt_load_btn.grid(column=1, row=4)
        self.yt_load_btn.bind('<Button-1>', func=self.__yt_init_plat)
        
        self.yt_not_downloaded_lbl_str = tk.StringVar()
        self.yt_not_downloaded_lbl_str.set("Videos not Found Locally")
        self.yt_not_downloaded_lbl = tk.Label(self, textvariable=self.yt_not_downloaded_lbl_str)
        self.yt_not_downloaded_lbl.grid(column=0, row=5, columnspan=2)
        
        self.yt_not_downloaded_lb = tk.Listbox(self, width=80)
        self.yt_not_downloaded_lb.grid(column=0, row=6, rowspan=3, columnspan=2)
        
        self.yt_not_downloaded_lb_sb = tk.Scrollbar(self)
        self.yt_not_downloaded_lb_sb.grid(column=0, row=6, rowspan=3, columnspan=2, sticky=tk.E+tk.N+tk.S)
        self.yt_not_downloaded_lb.config(yscrollcommand=self.yt_not_downloaded_lb_sb.set)
        self.yt_not_downloaded_lb_sb.config(command=self.yt_not_downloaded_lb.yview)
        
        self.yt_upload_lbl_str = tk.StringVar()
        self.yt_upload_lbl_str.set("Videos to Upload to YouTube")
        self.yt_upload_lbl = tk.Label(self, textvariable=self.yt_upload_lbl_str)
        self.yt_upload_lbl.grid(column=4, row=5, columnspan=2)
        
        self.yt_get_lbry_not_on_yt_btn = tk.Button(self, text="Get Vids on LBRY Not YT")
        self.yt_get_lbry_not_on_yt_btn.grid(column=4, row=9)
        self.yt_get_lbry_not_on_yt_btn.bind('<Button-1>', func=self.__yt_get_lbry_not_on_yt)
        
        self.yt_upload_lb = tk.Listbox(self, width=80)
        self.yt_upload_lb.grid(column=4, row=6, rowspan=3, columnspan=2)
        
        self.yt_upload_lb_sb = tk.Scrollbar(self)
        self.yt_upload_lb_sb.grid(column=5, row=6, rowspan=3, columnspan=2, sticky=tk.E+tk.N+tk.S)
        self.yt_upload_lb.config(yscrollcommand=self.yt_upload_lb_sb.set)
        self.yt_upload_lb_sb.config(command=self.yt_upload_lb.yview)
        
        self.yt_download_btn = tk.Button(self, text="Download")
        self.yt_download_btn.grid(column=0, row=9)
        self.yt_download_btn.bind('<Button-1>', func=self.__yt_download_video)
        
        self.yt_select_file_btn = tk.Button(self, text="Select Video File")
        self.yt_select_file_btn.grid(column=1, row=9)
        self.yt_select_file_btn.bind('<Button-1>', func=self.__yt_select_video_file)
        
        self.yt_remove_from_sync_btn = tk.Button(self, text="Remove from Sync List")
        self.yt_remove_from_sync_btn.grid(column=5, row=9)
        self.yt_remove_from_sync_btn.bind('<Button-1>', func=self.__yt_remove_from_sync)
        
        self.yt_upload_btn = tk.Button(self, text="Upload to YT")
        self.yt_upload_btn.grid(column=5, row=5)
        self.yt_upload_btn.bind('<Button-1>', func=self.__yt_upload_vids)
    
    def __yt_download_video(self, event):
        self.withdraw()
        for i in self.yt_not_downloaded_lb.curselection():
            self.yt_vids_not_downloaded[i].download()
        self.__clear_yt_lb()
        self.__populate_yt_lb()
        self.deiconify()
        return
    
    def __lbry_download_video(self, event):
        self.withdraw()
        for i in self.lbry_not_downloaded_lb.curselection():
            self.lbry_vids_not_downloaded[i].download()
        self.__clear_lbry_lb()
        self.__populate_lbry_lb()
        self.deiconify()
        return
        
    def __yt_select_video_file(self, event):
        self.withdraw()
        file = tk_fd.askopenfilename(filetypes=[("Video files", ".mp4")])
        video = None
        for i in self.yt_not_downloaded_lb.curselection():
            video = self.yt_vids_not_downloaded[i]
        
        self.settings.Base_logger.info(f"Copying {file} to {video.file}")
        shutil.copy(file, video.file)
        self.__clear_yt_lb()
        self.__populate_yt_lb()
        self.deiconify()
        return 'break'
    
    def __lbry_select_video_file(self, event):
        self.withdraw()
        file = tk_fd.askopenfilename(filetypes=[("Video files", ".mp4")])
        video = None
        for i in self.lbry_not_downloaded_lb.curselection():
            video = self.lbry_vids_not_downloaded[i]
        
        self.settings.Base_logger.info(f"Copying {file} to {video.file}")
        shutil.copy(file, video.file)
        self.__clear_lbry_lb()
        self.__populate_lbry_lb()
        self.deiconify()
        return 'break'
    
    def __lbry_init_plat(self, event):
        self.withdraw()
        self.__clear_lbry_lb()
        channels = lbry_plat.claim_list(claim_type=['channel'])
        count = 1
        choices = {}
        options = []
        for channel in channels['result']['items']:
            options.append(f"{count}. {channel['name']}")
            choices[f'{count}'] = channel
            count += 1
        
        self.lbry_channel_chooser = SimpleChoiceBox(title="LBRY Channel", text="Pick Your LBRY Channel", choices=options)
        self.lbry_channel_chooser.c.wait_variable(self.lbry_channel_chooser.selection)
        
        choice = self.lbry_channel_chooser.selection.get()[0]
        
        self.lbry_plat = lbry_plat.LBRY(settings=self.settings, ID=choices[choice]['claim_id'], init_videos=True)
        
        self.__populate_lbry_lb()
        
        self.deiconify()
        
        return 'break'
    
    def __lbry_api_setup(self, event):
        self.withdraw()
        try:
            lbry_plat.claim_list()
        except Exception:
            tk.messagebox.showwarning(message='LBRY Not Running please start the LBRY Desktop App')
            self.deiconify()
            return 'break'
        tk.messagebox.showinfo(message='LBRY Running')
        self.deiconify()
        return 'break'
    
    def __lbry_gui_setup(self):
        self.lbry_upload_lbl_str = tk.StringVar()
        self.lbry_upload_lbl_str.set("Videos to Upload to LBRY")
        self.lbry_upload_lbl = tk.Label(self, textvariable=self.lbry_upload_lbl_str)
        self.lbry_upload_lbl.grid(column=4, row=0, columnspan=2)
        
        self.lbry_get_yt_not_on_lbry_btn = tk.Button(self, text="Get Vids on YT not LBRY")
        self.lbry_get_yt_not_on_lbry_btn.grid(column=4, row=4)
        self.lbry_get_yt_not_on_lbry_btn.bind('<Button-1>', func=self.__lbry_get_yt_not_on_lbry)
        
        self.lbry_lbl_str = tk.StringVar()
        self.lbry_lbl_str.set("LBRY Channel")
        self.lbry_lbl = tk.Label(self, textvariable=self.lbry_lbl_str)
        self.lbry_lbl.grid(column=2, row=0, columnspan=2)
        
        self.lbry_lb = tk.Listbox(self, width=80)
        self.lbry_lb.grid(column=2, row=1, rowspan=3, columnspan=2)
        
        self.lbry_lb_sb = tk.Scrollbar(self)
        self.lbry_lb_sb.grid(column=2, row=1, rowspan=3, columnspan=2, sticky=tk.E+tk.N+tk.S)
        self.lbry_lb.config(yscrollcommand=self.lbry_lb_sb.set)
        self.lbry_lb_sb.config(command=self.lbry_lb.yview)
        
        self.lbry_api_setup_btn = tk.Button(self, text="Confirm API is Running")
        self.lbry_api_setup_btn.grid(column=2, row=4)
        self.lbry_api_setup_btn.bind('<Button-1>', func=self.__lbry_api_setup)
        
        self.lbry_load_btn = tk.Button(self, text="Load in LBRY Channel Data")
        self.lbry_load_btn.grid(column=3, row=4)
        self.lbry_load_btn.bind('<Button-1>', func=self.__lbry_init_plat)
        
        self.lbry_not_downloaded_lbl_str = tk.StringVar()
        self.lbry_not_downloaded_lbl_str.set("LBRY Videos not Downloaded")
        self.lbry_not_downloaded_lbl = tk.Label(self, textvariable=self.lbry_not_downloaded_lbl_str)
        self.lbry_not_downloaded_lbl.grid(column=2, row=5, columnspan=2)
        
        self.lbry_not_downloaded_lb = tk.Listbox(self, width=80)
        self.lbry_not_downloaded_lb.grid(column=2, row=6, rowspan=3, columnspan=2)
        
        self.lbry_not_downloaded_lb_sb = tk.Scrollbar(self)
        self.lbry_not_downloaded_lb_sb.grid(column=2, row=6, rowspan=3, columnspan=2, sticky=tk.E+tk.N+tk.S)
        self.lbry_not_downloaded_lb.config(yscrollcommand=self.lbry_not_downloaded_lb_sb.set)
        self.lbry_not_downloaded_lb_sb.config(command=self.lbry_not_downloaded_lb.yview)
        
        self.lbry_upload_lbl_str = tk.StringVar()
        self.lbry_upload_lbl_str.set("Videos to upload to LBRY")
        self.lbry_upload_lbl = tk.Label(self, textvariable=self.lbry_upload_lbl_str)
        self.lbry_upload_lbl.grid(column=4, row=0, columnspan=2)
        
        self.lbry_upload_lb = tk.Listbox(self, width=80)
        self.lbry_upload_lb.grid(column=4, row=1, rowspan=3, columnspan=2)
        
        self.lbry_upload_lb_sb = tk.Scrollbar(self)
        self.lbry_upload_lb_sb.grid(column=4, row=1, rowspan=3, columnspan=2, sticky=tk.E+tk.N+tk.S)
        self.lbry_upload_lb.config(yscrollcommand=self.lbry_upload_lb_sb.set)
        self.lbry_upload_lb_sb.config(command=self.lbry_upload_lb.yview)
        
        self.lbry_download_btn = tk.Button(self, text="Download")
        self.lbry_download_btn.grid(column=2, row=9)
        self.lbry_download_btn.bind('<Button-1>', func=self.__lbry_download_video)
        
        self.lbry_select_file_btn = tk.Button(self, text="Select Video File")
        self.lbry_select_file_btn.grid(column=3, row=9)
        self.lbry_select_file_btn.bind('<Button-1>', func=self.__lbry_select_video_file)
        
        self.lbry_remove_from_sync_btn = tk.Button(self, text="Remove from Sync List")
        self.lbry_remove_from_sync_btn.grid(column=5, row=4)
        self.lbry_remove_from_sync_btn.bind('<Button-1>', func=self.__lbry_remove_from_sync)
        
        self.lbry_upload_btn = tk.Button(self, text="Upload to LBRY")
        self.lbry_upload_btn.grid(column=5, row=0)
        self.lbry_upload_btn.bind('<Button-1>', func=self.__lbry_upload_vids)
        
    
    def __lbry_upload_vids(self,event):
        self.withdraw()
        for o in self.lbry_upload_vids:
            o.upload()
            self.lbry_upload_vids.remove(o)
            
        self.__clear_lbry_upload_lb()
        self.__populate_lbry_upload_lb_from_yt()
        self.__populate_lbry_lb()
        self.deiconify()
        return
    
    def __yt_upload_vids(self,event):
        self.withdraw()
        self.settings.logger.info("Attempting to upload to YouTube")
        for o in self.yt_upload_list:
            self.settings.logger.info(f"Attempting to upload {o.title} from {o.file}")
            o.upload()
            self.yt_upload_list.remove(o)
            
        self.__clear_yt_upload_lb()
        self.__populate_yt_upload_lb_from_lbry()
        self.__yt_init_plat(event=None)
        self.deiconify()
        return
    
    def __lbry_remove_from_sync(self, event):
        
        return
    
    def __yt_remove_from_sync(self, event):
        
        return
    
    def __init__(self, folder_location: str=''):
        super(CCMApp, self).__init__()
        
        self.settings = self.__setup_folder(folder_location=folder_location)
        self.secrets_dir = os.path.join(os.getcwd(), 'secrets')
        self.yt_cred_file = os.path.join(self.secrets_dir, 'youtube_client_secret.json')
        self.yt_plat = None
        self.lbry_plat = None
        self.lbry_channel_chooser = None
        self.yt_vids_not_downloaded = []
        self.lbry_vids_not_downloaded = []
        self.yt_upload_list = []
        self.lbry_upload_list = []
        
        self.geometry(f"{CCMApp.WIDTH}x{CCMApp.HEIGHT}+{CCMApp.WIN_X}+{CCMApp.WIN_Y}")
        
        self.__yt_gui_setup()
        
        self.__lbry_gui_setup()
        
        
        
class SimpleChoiceBox:
    def __init__(self,title,text,choices):
        self.t = tk.Toplevel()
        self.t.title(title if title else "")
        self.selection = tk.StringVar()
        tk.Label(self.t, text=text if text else "").grid(row=0, column=0)
        self.c = ttk.Combobox(self.t, value=choices if choices else [], state="readonly", textvariable=self.selection)
        self.c.bind("<<ComboboxSelected>>", self.combobox_select)
        self.c.grid(row=0, column=1)
        
    
    def combobox_select(self,event):
        self.t.destroy()
