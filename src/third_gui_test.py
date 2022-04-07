'''
Created on Mar 30, 2022

@author: tiff
'''
import platform
import sys
import tkinter as tk
import tkinter.ttk as ttk
import shutil
import contentcreatormanager.config as config
import os.path
import tkinter.filedialog as tk_fd
import tkinter.simpledialog as tk_sd
import json
import contentcreatormanager.media.video.youtube as yt_vid
import contentcreatormanager.platform.lbry as lbry_plat
import contentcreatormanager.media.video.lbry as lbry_vid
import tkinter.messagebox as tk_mb
import pickle

def focus_next_widget(event):
    """Callback to focus on next widget when pressing <Tab>."""
    event.widget.tk_focusNext().focus()
    return "break"


def setup_listbox(parent, height=10, width=40,
                  var=None):
    vsrl = ttk.Scrollbar(parent)
    vsrl.pack(side=tk.RIGHT, fill=tk.Y)

    listb = tk.Listbox(parent,
                       height=height, width=width,
                       yscrollcommand=vsrl.set,
                       listvariable=var)
    # listb.bind("<Tab>", focus_next_widget)

    listb.pack(side="top", expand=True)
    vsrl.config(command=listb.yview)

    return listb


class Thread_Vars:
    def __init__(self):
        super().__init__()

class Variables:
    def setup_vars(self, folder_location, parent):
        logging_config_file = os.path.join(folder_location, 'logging.ini')
        if not os.path.isfile(logging_config_file):
            shutil.copy(os.path.join(os.getcwd(), 'logging.ini'), logging_config_file)
        self.settings = config.Settings(folder_location=folder_location, logging_config_file=logging_config_file)
        self.logger = self.settings.Base_logger
        
        self.secrets_dir = os.path.join(os.getcwd(), 'secrets')
        self.yt_cred_file = os.path.join(self.secrets_dir, 'youtube_client_secret.json')
        
        self.yt_plat = None
        
        self.lbry_plat = None
        self.lbry_channel_chooser = None
        
        self.list_h = 10
        self.list_w = 45

        self.default_bid = 0.0001

        self.yt_vid_var = tk.StringVar()

        self.lbry_vid_var = tk.StringVar()
        self.lbry_title_var = tk.StringVar()

        self.lbry_upload_vids = []
        self.lbry_upload_titles = []
        self.lbry_up_var = tk.StringVar()

        self.yt_vid_not_dl = []
        self.yt_vid_not_dl_titles = []
        self.yt_vid_not_var = tk.StringVar()
        

        self.lbry_vid_not_dl = []
        self.lbry_vid_not_dl_titles = []
        self.lbry_vid_not_var = tk.StringVar()

        self.yt_upload_vids = []
        self.yt_upload_titles = []
        self.yt_up_var = tk.StringVar()
        
        self.yt_no_custom_thumb_vids = []
        self.yt_no_custom_thumb_vid_titles = []
        self.yt_custom_thumb_var = tk.StringVar()

class Methods:
    def __yt_thread_disable_buttons(self):
        self.yt_data_load_btn['state'] = tk.DISABLED
        self.yt_config_api_btn['state'] = tk.DISABLED
        self.yt_download_yt_custom_thumbs_btn['state'] = tk.DISABLED
        self.yt_download_btn['state'] = tk.DISABLED
        self.yt_select_vid_file_btn['state'] = tk.DISABLED
        self.yt_pick_thumb_file_btn['state'] = tk.DISABLED
        self.yt_generate_thumb_btn['state'] = tk.DISABLED
        self.yt_gen_and_upload_all_thumbs_btn['state'] = tk.DISABLED
        self.yt_get_lbry_vids_btn['state'] = tk.DISABLED
        self.yt_upload_btn['state'] = tk.DISABLED
        
        self.lbry_get_yt_vids_btn['state'] = tk.DISABLED
        
    def __lbry_thread_disable_buttons(self):
        self.lbry_api_btn['state'] = tk.DISABLED
        self.lbry_download_btn['state'] = tk.DISABLED
        self.lbry_select_vid_file_btn['state'] = tk.DISABLED
        self.lbry_get_yt_vids_btn['state'] = tk.DISABLED
        self.lbry_upload_btn['state'] = tk.DISABLED
        
        self.yt_get_lbry_vids_btn['state'] = tk.DISABLED

    def __yt_thread_enable_buttons(self):
        self.yt_data_load_btn['state'] = tk.NORMAL
        self.yt_config_api_btn['state'] = tk.NORMAL
        self.yt_download_yt_custom_thumbs_btn['state'] = tk.NORMAL
        self.yt_download_btn['state'] = tk.NORMAL
        self.yt_select_vid_file_btn['state'] = tk.NORMAL
        self.yt_pick_thumb_file_btn['state'] = tk.NORMAL
        self.yt_generate_thumb_btn['state'] = tk.NORMAL
        self.yt_gen_and_upload_all_thumbs_btn['state'] = tk.NORMAL
        self.yt_get_lbry_vids_btn['state'] = tk.NORMAL
        self.yt_upload_btn['state'] = tk.NORMAL
        
        self.lbry_get_yt_vids_btn['state'] = tk.NORMAL
    
    def __lbry_thread_enable_buttons(self):
        self.lbry_api_btn['state'] = tk.NORMAL
        self.lbry_download_btn['state'] = tk.NORMAL
        self.lbry_select_vid_file_btn['state'] = tk.NORMAL
        self.lbry_get_yt_vids_btn['state'] = tk.NORMAL
        self.lbry_upload_btn['state'] = tk.NORMAL
        
        self.yt_get_lbry_vids_btn['state'] = tk.NORMAL
    
    def __load_yt_thread_vars(self, thread):
        if hasattr(thread, 'yt_plat'):
            self.yt_plat = thread.yt_plat
        if hasattr(thread, 'yt_no_custom_thumb_vids'):
            self.yt_no_custom_thumb_vids = thread.yt_no_custom_thumb_vids
        if hasattr(thread, "yt_no_custom_thumb_vid_titles"):
            self.yt_no_custom_thumb_vid_titles = thread.yt_no_custom_thumb_vid_titles
        if hasattr(thread, "yt_vid_not_dl"):
            self.yt_vid_not_dl = thread.yt_vid_not_dl
        if hasattr(thread, "yt_vid_not_dl_titles"):
            self.yt_vid_not_dl_titles = thread.yt_vid_not_dl_titles
            
    def __load_lbry_thread_vars(self, thread):
        if hasattr(thread, 'lbry_plat'):
            self.lbry_plat = thread.lbry_plat
        if hasattr(thread, "lbry_vid_not_dl"):
            self.lbry_vid_not_dl = thread.lbry_vid_not_dl
        if hasattr(thread, "lbry_vid_not_dl_titles"):
            self.lbry_vid_not_dl_titles = thread.lbry_vid_not_dl_titles
        
    def __set_yt_lbs(self):
        if self.yt_plat is not None:
            self.yt_vid_var.set(self.yt_plat.media_object_titles)
        self.yt_vid_not_var.set(self.yt_vid_not_dl_titles)
        self.yt_up_var.set(self.yt_upload_titles)
        self.yt_custom_thumb_var.set(self.yt_no_custom_thumb_vid_titles)
        
    def __set_lbry_lbs(self):
        if self.lbry_plat is not None:
            self.lbry_vid_var.set(self.lbry_plat.media_object_titles)
        self.lbry_vid_not_var.set(self.lbry_vid_not_dl_titles)
        self.lbry_up_var.set(self.lbry_upload_titles)
    
    def __yt_thread_monitor(self, thread):
        if thread.is_alive():
            # check the thread every 100ms
            self.__yt_thread_disable_buttons()
            self.after(100, lambda: self.__yt_thread_monitor(thread))
        else:
            self.__yt_thread_enable_buttons()
        self.__load_yt_thread_vars(thread)
        self.__set_yt_lbs() 
        
    def __lbry_thread_monitor(self, thread):
        if thread.is_alive():
            # check the thread every 100ms
            self.__lbry_thread_disable_buttons()
            self.after(100, lambda: self.__lbry_thread_monitor(thread))
        else:
            self.__lbry_thread_enable_buttons()
        self.__load_lbry_thread_vars(thread)
        self.__set_lbry_lbs() 
    
    def __yt_thumb_thread_monitor(self, thread, i):
        if thread.is_alive():
            # check the thread every 100ms
            self.after(100, lambda: self.__yt_thread_monitor(thread))
        else:
            self.yt_plat.media_objects[i] = thread.video
            self.__yt_thread_enable_buttons()
        self.__load_yt_thread_vars(thread)
        self.__set_yt_lbs()
        
    def __yt_thread_monitor_no_var_update(self, thread):
        if thread.is_alive():
            # check the thread every 100ms
            self.after(100, lambda: self.__yt_thread_monitor(thread))
        else:
            self.__yt_thread_enable_buttons()
            
    def monitor_yt_custom_thumb_downloader_thread(self, thread):
        self.__yt_thread_monitor_no_var_update(thread)
    
    def monitor_yt_thumb_gen_thread(self, thread, i):
        self.__yt_thumb_thread_monitor(thread, i)
    
    def monitor_yt_thumb_gen_and_upload_thread(self, thread):
        self.__yt_thread_monitor(thread)
            
    def monitor_yt_data_load_thread(self, thread):
        self.__yt_thread_monitor(thread)
        
    def monitor_lbry_data_load_thread(self, thread):
        self.__lbry_thread_monitor(thread)
            
    def yt_generate_and_upload_thumbs(self):
        if len(self.yt_no_custom_thumb_vids) == 0:
            tk_mb.showwarning(title="No videos listed for this", message="No Videos are loaded into the no custom thumbnail list box")
            return
        
        self.__yt_thread_disable_buttons()
        
        gen_and_upload_thread = config.YTGUIThumbUploader(settings=self.settings,
                                                          yt_no_custom_thumb_vids=self.yt_no_custom_thumb_vids,
                                                          yt_no_custom_thumb_vid_titles=self.yt_no_custom_thumb_vid_titles)
        
        gen_and_upload_thread.start()
        
        self.monitor_yt_thumb_gen_and_upload_thread(gen_and_upload_thread)

    def yt_generate_thumb(self):
        video = None
        for i in self.yt_thumb_lb.curselection():
            video = self.yt_plat.media_objects[i]
            
        if video is None:
            tk_mb.showwarning(title="No Video Selected", message="You Must have a video selected when you press this button")
            os.chdir(self.settings.folder_location)
            return
        
        self.__yt_thread_disable_buttons()
        
        thumb_gen_thread = config.YTGUIThumbGenerator(settings=self.settings,
                                                      video=video)
        
        thumb_gen_thread.start()
        
        self.monitor_yt_thumb_gen_thread(thumb_gen_thread, i)
    
    def yt_pick_thumb(self):
        video = None
        for i in self.yt_thumb_lb.curselection():
            video = self.yt_plat.media_objects[i]
            
        if video is None:
            tk_mb.showwarning(title="No Video Selected", message="You Must have a video selected when you press this button")
            return
        
        file = tk_fd.askopenfilename(filetypes=[("Image files", ".jpg .jpeg")])
        
        if file == '':
            tk_mb.showwarning(title="No File Selected", message="You Must select an image file after you press this button")
            return
        
        self.logger.info(f"Copying {file} to {video.thumbnail}")
        shutil.copy(file, video.thumbnail)
        
        video.has_custom_thumbnail = True
    
    def download_yt_custom_thumbs(self):
        self.__yt_thread_disable_buttons()
        custom_thumb_downloader_thread = config.YTGUICustomThumbsDownloader(self.yt_plat)
        custom_thumb_downloader_thread.start()
        self.monitor_yt_custom_thumb_downloader_thread(custom_thumb_downloader_thread)
    
    def conf_api_details(self):
        self.logger.info("Configuring API Details for YouTube")
        if os.path.isfile(self.yt_cred_file):
            tk.messagebox.showinfo(message='YouTube Creds Already Present')
        else:
            self.logger.info("Creating Client Secrets File for YouTube")
            self.create_yt_client_secrets()    
        return 'break'
    
    def create_yt_client_secrets(self):
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
        self.logger.info(f"Saving Client Secrets file for YouTube as {self.yt_cred_file}")
        secrets_dir = os.path.join(os.getcwd(), 'secrets')
        if not os.path.isdir(secrets_dir):
            os.mkdir(secrets_dir)
        with open(self.yt_cred_file, 'w') as jf:
            json.dump(secrets_json, jf)
    
    def load_yt_data(self):
        self.__yt_thread_disable_buttons()
        loading_thread = config.YTGUIDataLoad(self.settings,self.yt_plat)
        loading_thread.start()
        self.monitor_yt_data_load_thread(loading_thread)

    def confirm_api(self):
        try:
            lbry_plat.claim_list()
        except Exception:
            tk.messagebox.showwarning(message='LBRY Not Running please start the LBRY Desktop App')
            return 'break'
        tk.messagebox.showinfo(message='LBRY Running')
        return 'break'

    def load_lbry_data(self):
        self.__lbry_thread_disable_buttons()
        self.logger.info("Loading in LBRY channel data")
        if self.lbry_plat is None:
            channels = lbry_plat.claim_list(claim_type=['channel'])
            if len(channels['result']['items']) > 1:
                picked = False
                for ch in channels['result']['items']:
                    if not picked:
                        option = tk_mb.askyesno(title='LBRY Channel Confirmation',message=f'Do you want to use this channel:{ch["name"]}')
                        if option:
                            lbry_loader_thread = config.LBRYGUIDataLoad(settings=self.settings, lbry_plat=self.lbry_plat, ID=ch['claim_id'])
                            lbry_loader_thread.start()
                            
                            self.monitor_lbry_data_load_thread(lbry_loader_thread)
                            picked = True
            elif len(channels['result']['items']) == 0:
                self.logger.error("No LBRY Channels found")
                return
            else:
                lbry_loader_thread = config.LBRYGUIDataLoad(settings=self.settings, lbry_plat=self.lbry_plat, ID=channels['result']['items'][0]['claim_id'])
                lbry_loader_thread.start()
                
                self.monitor_lbry_data_load_thread(lbry_loader_thread)
        else:
            lbry_loader_thread = config.LBRYGUIDataLoad(settings=self.settings, lbry_plat=self.lbry_plat, ID=channels['result']['items'][0]['claim_id'])
            lbry_loader_thread.start()
            
            self.monitor_lbry_data_load_thread(lbry_loader_thread)

    def get_vids_yt_not_lbry(self):
        self.logger.info("Getting videos on YouTube not on LBRY")
        
        list1 = self.yt_plat.media_objects
        list2 = self.lbry_plat.media_objects
        thumb_dir = os.path.join(os.getcwd(), 'thumbs')
        self.logger.info("Looping through YouTube Media Objects")
        for obj in list1:
            not_this_one = False
            self.logger.info("Looping through LBRY Media Objects")
            for o in list2:
                if obj.title == o.title:
                    self.logger.info(f"{o.title} is on both Platforms")
                    not_this_one = True
            if not not_this_one:
                self.logger.info(f"{obj.title} is not on LBRY creating LBRY Video Object")
                lvid = lbry_vid.LBRYVideo(lbry_channel=self.lbry_plat, tags=obj.tags, title=obj.title, file_name=os.path.basename(obj.file), description=obj.description, new_video=True)
                if not os.path.isdir(os.path.join(os.getcwd(), 'thumbs')):
                    self.logger.warning("Currently no thumbs dir creating it")
                    os.makedirs('thumbs')
                if not os.path.isfile(obj.thumbnail):
                    self.logger.warning(f"Thumbnail {obj.thumbnail} not downloaded downloading now")
                    os.chdir(thumb_dir)
                    lvid.thumbnail = obj.download_thumb()
                    os.chdir(self.settings.folder_location)
                else:
                    self.logger.info(f"Thumbnail already present no need to download")
                    lvid.thumbnail = obj.thumbnail
                    self.logger.info(f"Setting bid for new LBRY Vid to {self.default_bid}")
                    lvid.bid = self.default_bid
                self.logger.info(f"Adding {lvid.title} to list of vids not on LBRY that are on YouTube")
                self.lbry_upload_vids.append(lvid)
                self.lbry_upload_titles.append(lvid.title)
        
        self.lbry_up_var.set(self.lbry_upload_titles)

    def lbry_remove_upload_list(self):
        for i in self.lbry_upload_lb.curselection():
            removal_vid= self.lbry_upload_vids[i]
        
        self.logger.info(f"Removing {removal_vid.title} from LBRY Upload List")
        self.lbry_upload_vids.remove(removal_vid)
        self.lbry_upload_titles.remove(removal_vid.title)
        self.lbry_up_var.set(self.lbry_upload_titles)
        
    def lbry_set_title(self):
        self.lbry_title_var.set("LBRY upload list.\n"
                                "Default value: "
                                f"{self.default_bid} LBC each")
        
    def lbry_change_default_bid(self):
        new_bid = tk_sd.askfloat(title='Default Bid',
                       prompt="Please enter the default LBC bid you would like to make for video uploads")
        
        if new_bid >= 0.0001:
            self.default_bid = new_bid
            self.lbry_set_title()
            self.logger.info(f"Set LBRY Default bid to {new_bid}")
            return
        
        self.logger.error("Bad value given")
        tk_mb.showwarning(title="Bad Bid", message="Please enter a valid float that is 0.0001 or greater")
        
    def lbry_upload_videos(self):
        window = tk.Toplevel()
        window.geometry("400x90")
        window.wm_title("Uploading LBRY Videos")
        window.update_idletasks()
        window.grab_set()
        for vid in self.lbry_upload_vids:
            self.logger.info(f"Attempting to upload {vid.file} to LBRY")
            vid.upload()
            if vid.is_uploaded():
                self.logger.info("Video Uploaded")
                self.lbry_upload_vids.remove(vid)
                self.lbry_upload_titles.remove(vid.title)
                self.lbry_up_var.set(self.yt_upload_titles)
                self.lbry_plat.add_video(vid)
                self.lbry_vid_var.set(self.lbry_plat.media_object_titles)
            else:
                self.logger.error("LBRY Upload Failed")
        window.destroy()

    def yt_download(self):
        for j in self.yt_not_dl_lb.curselection():
            vid = self.yt_vid_not_dl[j]
        
        vid_dir = os.path.join(os.getcwd(), 'videos')
        if not os.path.isdir(vid_dir):
            os.mkdir(vid_dir)
        self.logger.info(f"Downloading YT Vid {vid.title}")
        vid.download()
        if os.path.isfile(vid.file):
            self.logger.info("Video Downloaded")
            self.yt_vid_not_dl.remove(vid)
            self.yt_vid_not_dl_titles.remove(vid.title)
            self.yt_vid_not_var.set(self.yt_vid_not_dl_titles)
        else:
            self.logger.error("Can not find video file download failed")

    def yt_select_video(self):
        file = tk_fd.askopenfilename(filetypes=[("Video files", ".mp4")])
        for j in self.yt_not_dl_lb.curselection():
            video = self.yt_vid_not_dl[j]
        
        self.logger.info(f"Copying {file} to {video.file}")
        shutil.copy(file, video.file)
        
        self.yt_vid_not_dl.remove(video)
        self.yt_vid_not_dl_titles.remove(video.title)
        self.yt_vid_not_var.set(self.yt_vid_not_dl_titles)

    def lbry_download(self):
        window = tk.Toplevel()
        window.geometry("400x90")
        window.wm_title("Downloading LBRY Video")
        window.update_idletasks()
        window.grab_set()
        for j in self.lbry_not_dl_lb.curselection():
            vid = self.lbry_vid_not_dl[j]
        
        vid_dir = os.path.join(os.getcwd(), 'videos')
        if not os.path.isdir(vid_dir):
            os.mkdir(vid_dir)
        
        self.logger.info(f"Downloading LBRYS Vid {vid.title}")
        vid.download()
        if os.path.isfile(vid.file):
            self.logger.info("Video Downloaded")
            self.lbry_vid_not_dl.remove(vid)
            self.lbry_vid_not_dl_titles.remove(vid.title)
            self.lbry_vid_not_var.set(self.lbry_vid_not_dl_titles)
        else:
            self.logger.error("Can not find video file download failed")
            
        window.destroy()

    def lbry_select_video(self):
        file = tk_fd.askopenfilename(filetypes=[("Video files", ".mp4")])
        for j in self.lbry_not_dl_lb.curselection():
            video = self.lbry_vid_not_dl[j]
        
        self.logger.info(f"Copying {file} to {video.file}")
        shutil.copy(file, video.file)
        
        self.lbry_vid_not_dl.remove(video)
        self.lbry_vid_not_dl_titles.remove(video.title)
        self.lbry_vid_not_var.set(self.lbry_vid_not_dl_titles)

    def get_vids_lbry_not_yt(self):
        self.logger.info("Getting videos on LBRY that are not on YouTube")
        
        list1 = self.lbry_plat.media_objects
        list2 = self.yt_plat.media_objects
        thumb_dir = os.path.join(os.getcwd(), 'thumbs')
        self.logger.info("Looping through LBRY Media Objects")
        for obj in list1:
            not_this_one = False
            self.logger.info("Looping through YouTube Media Objects")
            for o in list2:
                if obj.title == o.title:
                    self.logger.info(f"{o.title} is on both Platforms")
                    not_this_one = True
            if not not_this_one:
                self.logger.info(f"{obj.title} is not on YouTube creating YouTube Video Object")
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
                yvid.thumbnail = obj.thumbnail
                if not os.path.isdir(thumb_dir):
                    self.logger.warning("Currently no thumbs dir creating it")
                    os.makedirs('thumbs')
                if not os.path.isfile(obj.thumbnail):
                    self.logger.warning(f"Thumbnail {obj.thumbnail} not downloaded downloading now")
                    os.chdir(thumb_dir)
                    yvid.thumbnail = obj.download_thumb()
                    os.chdir(self.settings.folder_location)
                else:
                    self.logger.info(f"Thumbnail already present no need to download")
                    yvid.thumbnail = obj.thumbnail
                self.logger.info(f"Adding {yvid.title} to list of vids not on YouTube that are on LBRY")
                self.yt_upload_vids.append(yvid)
                self.yt_upload_titles.append(yvid.title)
        
        self.yt_up_var.set(self.yt_upload_titles)

    def yt_remove_upload_list(self):
        for i in self.yt_upload_lb.curselection():
            removal_vid= self.yt_upload_vids[i]
        
        self.logger.info(f"Removing {removal_vid.title} from YouTube Upload List")
        self.yt_upload_vids.remove(removal_vid)
        self.yt_upload_titles.remove(removal_vid.title)
        self.yt_up_var.set(self.yt_upload_titles)
        
    def yt_upload_videos(self):
        window = tk.Toplevel()
        window.geometry("400x90")
        window.wm_title("Uploading YouTube Videos")
        window.update_idletasks()
        window.grab_set()
        for vid in self.yt_upload_vids:
            self.logger.info(f"Attempting to upload {vid.file} to YouTube")
            vid.upload()
            if vid.is_uploaded():
                self.logger.info("Video Uploaded")
                self.yt_upload_vids.remove(vid)
                self.yt_upload_titles.remove(vid.title)
                self.yt_up_var.set(self.yt_upload_titles)
                self.yt_plat.add_video(vid)
                self.yt_vid_var.set(self.yt_plat.media_object_titles)
            else:
                self.logger.error("YouTube Upload Failed")
        window.destroy()       
                

class MainPage:
    """Main interface."""
    def setup_page_listboxes(self, parent):
        frame1 = ttk.Frame(parent)
        frame1.grid(row=0, column=0, padx=4, pady=4, sticky=tk.S)

        frame2 = ttk.Frame(parent)
        frame2.grid(row=0, column=1, padx=4, pady=4, sticky=tk.S)

        frame3 = ttk.Frame(parent)
        frame3.grid(row=0, column=2, padx=4, pady=4, sticky=tk.S)

        frame4 = ttk.Frame(parent)
        frame4.grid(row=1, column=0, padx=4, pady=4)

        frame5 = ttk.Frame(parent)
        frame5.grid(row=1, column=1, padx=4, pady=4)

        frame6 = ttk.Frame(parent)
        frame6.grid(row=1, column=2, padx=4, pady=4)
        
        frame7 = ttk.Frame(parent)
        frame7.grid(row=2, column=0, padx=4, pady=4)

        

        self.setup_yt_ch(frame1)
        self.setup_lbry_ch(frame2)
        self.setup_lbry_up_list(frame3)
        self.setup_yt_not_dl_vids(frame4)
        self.setup_lbry_not_downloaded(frame5)
        self.setup_yt_up_list(frame6)
        self.setup_yt_thumbnail_list(frame7)
        
        
        
    
    def setup_yt_thumbnail_list(self, parent):
        title = ttk.Label(parent,
                          text="YouTube Videos Without Custom Thumbnail")
        title.grid(row=0, column=0, sticky=tk.W + tk.E)

        f1 = ttk.Frame(parent)
        f1.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.yt_thumb_lb = setup_listbox(f1, height=self.list_h, width=self.list_w,
                      var=self.yt_custom_thumb_var)

        f2 = ttk.Frame(parent)
        f2.grid(row=2, column=0, sticky=tk.W + tk.E)
        self.yt_pick_thumb_file_btn = ttk.Button(f2, text="Pick Thumbnail File",
                        command=self.yt_pick_thumb)
        self.yt_pick_thumb_file_btn.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        self.yt_generate_thumb_btn = ttk.Button(f2, text="Generate Thumbnail",
                        command=self.yt_generate_thumb)
        self.yt_generate_thumb_btn.grid(row=0, column=1, sticky=tk.W + tk.E)
        
        f3 = ttk.Frame(parent)
        f3.grid(row=3, column=0, sticky=tk.W + tk.E)
        
        self.yt_gen_and_upload_all_thumbs_btn = ttk.Button(f3, text="Generate and Upload all Thumbnails",
                        command=self.yt_generate_and_upload_thumbs)
        self.yt_gen_and_upload_all_thumbs_btn.grid(row=0, column=0, sticky=tk.W + tk.E)
    
    def setup_yt_ch(self, parent):
        title = ttk.Label(parent,
                          text="YouTube channel")
        title.grid(row=0, column=0, sticky=tk.W + tk.E)

        f1 = ttk.Frame(parent)
        f1.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.yt_ch_lb = setup_listbox(f1, height=self.list_h, width=self.list_w,
                      var=self.yt_vid_var)

        f2 = ttk.Frame(parent)
        f2.grid(row=2, column=0, sticky=tk.W + tk.E)
        self.yt_config_api_btn = ttk.Button(f2, text="Configure API details",
                        command=self.conf_api_details)
        self.yt_config_api_btn.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        self.yt_data_load_btn = ttk.Button(f2, text="Load in YouTube data",
                        command=self.load_yt_data)
        self.yt_data_load_btn.grid(row=0, column=1, sticky=tk.W + tk.E)
        
        f3 = ttk.Frame(parent)
        f3.grid(row=3, column=0, sticky=tk.W + tk.E)
        
        self.yt_download_yt_custom_thumbs_btn = ttk.Button(f3, text="Download Custom Thumbnails",
                        command=self.download_yt_custom_thumbs)
        self.yt_download_yt_custom_thumbs_btn.grid(row=0, column=0, sticky=tk.W + tk.E)

    def setup_lbry_ch(self, parent):
        title = ttk.Label(parent,
                          text="LBRY channel")
        title.grid(row=0, column=0, sticky=tk.W + tk.E)

        f1 = ttk.Frame(parent)
        f1.grid(row=1, column=0, sticky=tk.W + tk.E)
        setup_listbox(f1, height=self.list_h, width=self.list_w,
                      var=self.lbry_vid_var)

        f2 = ttk.Frame(parent)
        f2.grid(row=2, column=0, sticky=tk.W + tk.E)
        self.lbry_api_btn = ttk.Button(f2, text="Confirm API is running",
                        command=self.confirm_api)
        self.lbry_api_btn.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        self.lbry_channel_load_btn = ttk.Button(f2, text="Load in LBRY channel data",
                        command=self.load_lbry_data)
        self.lbry_channel_load_btn.grid(row=0, column=1, sticky=tk.W + tk.E)
        
        f3 = ttk.Frame(parent)
        f3.grid(row=3, column=0, sticky=tk.W + tk.E)
        
        b3 = ttk.Button(f3, text="Future Button")
        b3.grid(row=0, column=0, sticky=tk.W + tk.E)

    def setup_lbry_up_list(self, parent):
        title = ttk.Label(parent,
                          textvariable=self.lbry_title_var)
        self.lbry_set_title()
        title.grid(row=0, column=0, sticky=tk.W + tk.E)

        f1 = ttk.Frame(parent)
        f1.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.lbry_upload_lb = setup_listbox(f1, height=self.list_h, width=self.list_w,
                      var=self.lbry_up_var)

        f2 = ttk.Frame(parent)
        f2.grid(row=2, column=0, sticky=tk.W + tk.E)
        
        self.lbry_get_yt_vids_btn = ttk.Button(f2, text="Get vids on YT not on LBRY",
                        command=self.get_vids_yt_not_lbry)
        self.lbry_get_yt_vids_btn.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        self.lbry_remove_from_upload_btn = ttk.Button(f2, text="Remove from LBRY Upload List",
                        command=self.lbry_remove_upload_list)
        self.lbry_remove_from_upload_btn.grid(row=0, column=1, sticky=tk.W + tk.E)
        
        f3 = ttk.Frame(parent)
        f3.grid(row=3, column=0, sticky=tk.W + tk.E)
        
        self.lbry_upload_btn = ttk.Button(f3, text="Upload to LBRY",
                        command=self.lbry_upload_videos)
        self.lbry_upload_btn.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        self.lbry_bid_btn = ttk.Button(f3, text="Change Default Bid",
                        command=self.lbry_change_default_bid)
        self.lbry_bid_btn.grid(row=0, column=1, sticky=tk.W + tk.E)

    def setup_yt_not_dl_vids(self, parent):
        title = ttk.Label(parent,
                          text="Videos not found locally")
        title.grid(row=0, column=0, sticky=tk.W + tk.E)

        f1 = ttk.Frame(parent)
        f1.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.yt_not_dl_lb = setup_listbox(f1, height=self.list_h, width=self.list_w,
                      var=self.yt_vid_not_var)

        f2 = ttk.Frame(parent)
        f2.grid(row=2, column=0, sticky=tk.W + tk.E)
        self.yt_download_btn = ttk.Button(f2, text="Download",
                        command=self.yt_download)
        self.yt_download_btn.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        self.yt_select_vid_file_btn = ttk.Button(f2, text="Select video file",
                        command=self.yt_select_video)
        self.yt_select_vid_file_btn.grid(row=0, column=1, sticky=tk.W + tk.E)
        
        f3 = ttk.Frame(parent)
        f3.grid(row=3, column=0, sticky=tk.W + tk.E)
        b3 = ttk.Button(f3, text="Future Button")
        b3.grid(row=0, column=0, sticky=tk.W + tk.E)

    def setup_lbry_not_downloaded(self, parent):
        title = ttk.Label(parent,
                          text="LBRY videos not downloaded")
        title.grid(row=0, column=0, sticky=tk.W + tk.E)

        f1 = ttk.Frame(parent)
        f1.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.lbry_not_dl_lb = setup_listbox(f1, height=self.list_h, width=self.list_w,
                      var=self.lbry_vid_not_var)

        f2 = ttk.Frame(parent)
        f2.grid(row=2, column=0, sticky=tk.W + tk.E)
        self.lbry_download_btn = ttk.Button(f2, text="Download",
                        command=self.lbry_download)
        self.lbry_download_btn.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.lbry_select_vid_file_btn = ttk.Button(f2, text="Select video file",
                        command=self.lbry_select_video)
        self.lbry_select_vid_file_btn.grid(row=0, column=1, sticky=tk.W + tk.E)
        
        f3 = ttk.Frame(parent)
        f3.grid(row=3, column=0, sticky=tk.W + tk.E)
        b3 = ttk.Button(f3, text="Future Button")
        b3.grid(row=0, column=0, sticky=tk.W + tk.E)

    def setup_yt_up_list(self, parent):
        title = ttk.Label(parent,
                          text="YouTube upload list")
        title.grid(row=0, column=0, sticky=tk.W + tk.E)

        f1 = ttk.Frame(parent)
        f1.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.yt_upload_lb = setup_listbox(f1, height=self.list_h, width=self.list_w,
                      var=self.yt_up_var)

        f2 = ttk.Frame(parent)
        f2.grid(row=2, column=0, sticky=tk.W + tk.E)
        self.yt_get_lbry_vids_btn = ttk.Button(f2, text="Get vids on LBRY not on YT",
                        command=self.get_vids_lbry_not_yt)
        self.yt_get_lbry_vids_btn.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        self.yt_remove_from_upload_btn = ttk.Button(f2, text="Remove From YT Upload List",
                        command=self.yt_remove_upload_list)
        self.yt_remove_from_upload_btn.grid(row=0, column=1, sticky=tk.W + tk.E)
        
        f3 = ttk.Frame(parent)
        f3.grid(row=3, column=0, sticky=tk.W + tk.E)
        
        self.yt_upload_btn = ttk.Button(f3, text="Upload to YouTube",
                        command=self.yt_upload_videos)
        self.yt_upload_btn.grid(row=0, column=0, sticky=tk.W + tk.E)


class Application(ttk.Frame,
                  Variables, Methods,
                  MainPage):
    def __init__(self, root, folder_location):
        # Initialize and show the main frame
        super().__init__(root)  # Frame(root)
        self.pack(fill="both", expand=True)  # Frame.pack()

        self.setup_vars(folder_location=folder_location, parent=self)  # Initialized from `Variables` class
        self.setup_widgets(parent=self)  # the new Frame is the main container

    def setup_widgets(self, parent):
        """Setup the widgets of the application."""
        # From the MainPage class
        self.setup_page_listboxes(parent)

def main(argv=None):    
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.title("Content Creator Manager")
    # The quit method is explicit because we create a second toplevel,
    # and it causes problems when we try to close the window
    root.protocol("WM_DELETE_WINDOW", root.quit)

    theme = ttk.Style()
    if "linux" in platform.system().lower():
        theme.theme_use("clam")

    if len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]):
            app = Application(root=root, folder_location=sys.argv[1])
        else:
            folder = tk_fd.askdirectory(title='Choose Application Directory')
            app = Application(root=root, folder_location=folder)
    else:
        folder = tk_fd.askdirectory(title='Choose Application Directory')
        app = Application(root=root, folder_location=folder)
    
    app.mainloop()


if __name__ == "__main__":
    sys.exit(main())