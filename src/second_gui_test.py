'''
Created on Mar 30, 2022

@author: tiff
'''
import platform
import random
import sys
import tkinter as tk
import tkinter.ttk as ttk
import shutil
import contentcreatormanager.config as config
import os.path
import tkinter.filedialog as tk_fd
import tkinter.simpledialog as tk_sd
import json
import contentcreatormanager.platform.youtube as yt_plat
import contentcreatormanager.media.video.youtube as yt_vid
import contentcreatormanager.platform.lbry as lbry_plat
import contentcreatormanager.media.video.lbry as lbry_vid
import tkinter.messagebox as tk_mb

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


class Variables:
    def setup_vars(self, folder_location):
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

        self.default_bid = 0.001

        self.yt_vid_var = tk.StringVar()

        self.lbry_vid_var = tk.StringVar()

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
        
        


class Methods:
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
        with open(self.yt_cred_file, 'w') as jf:
            json.dump(secrets_json, jf)
    
    def load_yt_data(self):
        self.logger.info("Loading in YouTube data")
        
        if self.yt_plat is None:
            self.logger.info("YouTube Platform is not initialized.  Initializing now")
            self.yt_plat = yt_plat.YouTube(settings=self.settings, init_videos=True)
        
        for vid in self.yt_plat.media_objects:
            if not os.path.isfile(vid.file):
                self.yt_vid_not_dl.append(vid)
                self.yt_vid_not_dl_titles.append(vid.title)
        
        self.yt_vid_var.set(self.yt_plat.media_object_titles)
        self.yt_vid_not_var.set(self.yt_vid_not_dl_titles)

    def confirm_api(self):
        try:
            lbry_plat.claim_list()
        except Exception:
            tk.messagebox.showwarning(message='LBRY Not Running please start the LBRY Desktop App')
            return 'break'
        tk.messagebox.showinfo(message='LBRY Running')
        return 'break'

    def load_lbry_data(self):
        self.logger.info("Loading in LBRY channel data")
        if self.lbry_plat is None:
            channels = lbry_plat.claim_list(claim_type=['channel'])
            if len(channels['result']['items']) > 1:
                picked = False
                for ch in channels['result']['items']:
                    if not picked:
                        option = tk_mb.askyesno(title='LBRY Channel Confirmation',message=f'Do you want to use this channel:{ch["name"]}')
                        if option:
                            self.lbry_plat = lbry_plat.LBRY(settings=self.settings, ID=ch['claim_id'], init_videos=True)
                            picked = True
            elif len(channels['result']['items']) == 0:
                self.logger.error("No LBRY Channels found")
                return
            else:
                self.lbry_plat = lbry_plat.LBRY(settings=self.settings, ID=channels['result']['items'][0]['claim_id'], init_videos=True)   
        
        for vid in self.lbry_plat.media_objects:
            if not os.path.isfile(vid.file):
                self.lbry_vid_not_dl.append(vid)
                self.lbry_vid_not_dl_titles.append(vid.title)
        
        self.lbry_vid_var.set(self.lbry_plat.media_object_titles)
        self.lbry_vid_not_var.set(self.lbry_vid_not_dl_titles)  

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

    def yt_download(self):
        for j in self.yt_not_dl_lb.curselection():
            vid = self.yt_vid_not_dl[j]
        
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
        for j in self.lbry_not_dl_lb.curselection():
            vid = self.lbry_vid_not_dl[j]
        
        self.logger.info(f"Downloading LBRYS Vid {vid.title}")
        vid.download()
        if os.path.isfile(vid.file):
            self.logger.info("Video Downloaded")
            self.lbry_vid_not_dl.remove(vid)
            self.lbry_vid_not_dl_titles.remove(vid.title)
            self.lbry_vid_not_var.set(self.lbry_vid_not_dl_titles)
        else:
            self.logger.error("Can not find video file download failed")

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

        self.setup_yt_ch(frame1)
        self.setup_lbry_ch(frame2)
        self.setup_lbry_up_list(frame3)
        self.setup_yt_not_dl_vids(frame4)
        self.setup_lbry_not_downloaded(frame5)
        self.setup_yt_up_list(frame6)

    def setup_yt_ch(self, parent):
        title = ttk.Label(parent,
                          text="YouTube channel")
        title.grid(row=0, column=0, sticky=tk.W + tk.E)

        f1 = ttk.Frame(parent)
        f1.grid(row=1, column=0, sticky=tk.W + tk.E)
        setup_listbox(f1, height=self.list_h, width=self.list_w,
                      var=self.yt_vid_var)

        f2 = ttk.Frame(parent)
        f2.grid(row=2, column=0, sticky=tk.W + tk.E)
        b1 = ttk.Button(f2, text="Configure API details",
                        command=self.conf_api_details)
        b1.grid(row=0, column=0, sticky=tk.W + tk.E)
        b2 = ttk.Button(f2, text="Load in YouTube data",
                        command=self.load_yt_data)
        b2.grid(row=0, column=1, sticky=tk.W + tk.E)

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
        b1 = ttk.Button(f2, text="Confirm API is running",
                        command=self.confirm_api)
        b1.grid(row=0, column=0, sticky=tk.W + tk.E)
        b2 = ttk.Button(f2, text="Load in LBRY channel data",
                        command=self.load_lbry_data)
        b2.grid(row=0, column=1, sticky=tk.W + tk.E)

    def setup_lbry_up_list(self, parent):
        title = ttk.Label(parent,
                          text=("LBRY upload list.\n"
                                "Default value: "
                                f"{self.default_bid} LBC each"))
        title.grid(row=0, column=0, sticky=tk.W + tk.E)

        f1 = ttk.Frame(parent)
        f1.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.lbry_upload_lb = setup_listbox(f1, height=self.list_h, width=self.list_w,
                      var=self.lbry_up_var)

        f2 = ttk.Frame(parent)
        f2.grid(row=2, column=0, sticky=tk.W + tk.E)
        b1 = ttk.Button(f2, text="Get vids on YT not on LBRY",
                        command=self.get_vids_yt_not_lbry)
        b1.grid(row=0, column=0, sticky=tk.W + tk.E)
        b2 = ttk.Button(f2, text="Remove from LBRY Upload List",
                        command=self.lbry_remove_upload_list)
        b2.grid(row=0, column=1, sticky=tk.W + tk.E)

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
        b1 = ttk.Button(f2, text="Download",
                        command=self.yt_download)
        b1.grid(row=0, column=0, sticky=tk.W + tk.E)
        b2 = ttk.Button(f2, text="Select video file",
                        command=self.yt_select_video)
        b2.grid(row=0, column=1, sticky=tk.W + tk.E)

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
        b1 = ttk.Button(f2, text="Download",
                        command=self.lbry_download)
        b1.grid(row=0, column=0, sticky=tk.W + tk.E)
        b2 = ttk.Button(f2, text="Select video file",
                        command=self.lbry_select_video)
        b2.grid(row=0, column=1, sticky=tk.W + tk.E)

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
        b1 = ttk.Button(f2, text="Get vids on LBRY not on YT",
                        command=self.get_vids_lbry_not_yt)
        b1.grid(row=0, column=0, sticky=tk.W + tk.E)
        b2 = ttk.Button(f2, text="Remove From YT Upload List",
                        command=self.yt_remove_upload_list)
        b2.grid(row=0, column=1, sticky=tk.W + tk.E)


class Application(ttk.Frame,
                  Variables, Methods,
                  MainPage):
    def __init__(self, root, folder_location):
        # Initialize and show the main frame
        super().__init__(root)  # Frame(root)
        self.pack(fill="both", expand=True)  # Frame.pack()

        self.setup_vars(folder_location=folder_location)  # Initialized from `Variables` class
        self.setup_widgets(parent=self)  # the new Frame is the main container

    def setup_widgets(self, parent):
        """Setup the widgets of the application."""
        # From the MainPage class
        self.setup_page_listboxes(parent)

def main(argv=None):    
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.title("CreatorManager")
    # The quit method is explicit because we create a second toplevel,
    # and it causes problems when we try to close the window
    root.protocol("WM_DELETE_WINDOW", root.quit)

    theme = ttk.Style()
    if "linux" in platform.system().lower():
        theme.theme_use("clam")

    if os.path.isdir(sys.argv[1]):
        app = Application(root=root, folder_location=sys.argv[1])
    else:
        folder = tk_fd.askdirectory(title='Choose Application Directory')
        app = Application(root=root, folder_location=folder)
    
    app.mainloop()


if __name__ == "__main__":
    sys.exit(main())