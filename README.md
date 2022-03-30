# ContentCreatorManager

# Warning:

# Work on the GUI may have broken the scripts.  I have not tested them and I have not updated this readme apart from this warning.  Further updates to come

## What Is This?

This aims to be a tool for small content creators to manage and promote their content on as many platforms as possible.  This tool should make it so that once set up a content creator has to do the same amount of or less work than managing one platform and still get their content everywhere and announced everywhere.

While the goals for this thing are big, it is still heavily under development.  Its just a work in progress.  There is a fair amount of work on the code base and what it is capable of can be seen below.  In addition to that some scripts have been written using this code base to accomplish various tasks.  The logic used in these scripts will slowly get added into the code base and eventually a UI for the actual tool this is all working towards will be made..

### Scripts:

- Bulk **LBRY** upload script (tested working on my Windows machine and almost working on another person's Arch Linux machine)

- **YouTube < = > LBRY** sync script (Tested on my Windows machine and one other Linux machine at this point)

- **LBRY** Thumbnail set script (This script finds videos with matching titles on your YouTube and LBRY Channel and then tells LBRY where the YouTube thumbnail is, but does not upload a thumbnail to LBRY itself)

- **LBRY** Thumbnail generation and upload script (This will go through every video on a channel and download the video cut a thumbnail out of it, Upload, and set that thumbnail)

#### Bulk LBRY Upload Script:

##### Requirements:

 - You will need Python 3 installed
 - You will need to be running the LBRY Desktop App.  
 - You will need to install the shortuuid python lib.
 
##### How To:

 - Run the script lbry_bulk_upload.py
 - It will ask you to input the path to the folder that all your videos are in
 - It will then list all your LBRY Channels and require you to pick one
 - You will be prompted for some default info to go with the videos
 - It should prompt you once at the end to confirm before upload begins
 
#### LBRY Thumbnail Generation Script:

##### Requirements:

 - You will need Python 3 installed
 - You will need to be running the LBRY Desktop App.  
 - You will need to install the shortuuid python lib.
 - You will need ffmpeg binary installed
 - You will need python-ffmpeg installed
 
##### How To:

 - Run the script lbry_thumbnail_generate_and_upload.py
 - It will ask you to input the path to the folder that all your videos are in (or that they will be downloaded to keep in mind if you want to use existing videos the filenames need to match what they would be if the tool downloaded them a script to help rename videos probably coming)
 - It will then list all your LBRY Channels and require you to pick one
 - The script will then get to work
 
#### YouTube < = > LBRY Sync Script:

##### Requirements:

 - You will need Python 3 installed
 - You will need to be running the LBRY Desktop App.  
 - You can try running the testimports.py file (once able to run this without error you should have all Python libraries you need installed)
 - You will need to set up credentials for YouTube Data API v3 and save your secrets file as youtube_client_secret.json in the same directory that the youtube_lbry_sync.py file lives in
 
##### How To:

 - Run the script youtube_lbry_sync.py
 - It will ask you to input the path to the folder that all your videos will be downloaded to.
 - It will then list all your LBRY Channels and require you to pick one
 - You will be prompted for a default bid for LBRY uploads
 - It should prompt you on the first couple of uploads that way you can ensure it is working before you let it finish the job

#### LBRY Thumbnail Sync Script:

##### Requirements:

 - You will need Python 3 installed
 - You will need to be running the LBRY Desktop App.  
 - You can try running the testimports.py file (once able to run this without error you should have all Python libraries you need installed)
 - You will need to set up credentials for YouTube Data API v3 and save your secrets file as youtube_client_secret.json in the same directory that the youtube_lbry_sync.py file lives in
 
##### How To:

 - Run the script lbry_set_thumbs_from_youtube.py
 - It will list all your LBRY Channels and require you to pick one
 - It will then do its thing and point LBRY Videos to the YouTube Thumbnails

## I NEED HELP WITH ONE or MORE of THESE SCRIPTS:

- Hit me up on discord Techie_Tiff#5008
- Shoot me an email tiff@tiff.tech

### Code Base Current Functionality:

#### Posting To:

- Facebook

- Twitter

- Reddit

- YouTube

- LBRY

- Rumble

#### Updating Content On:

- YouTube

- LBRY

#### Downloading Content From:

- YouTube

- LBRY

## Upcoming (hopefully):

- Local Backup

- Methods to compare various things (lists of videos from different platforms, or list of videos on a platform versus locally on the machine/in apps memory for example)

- Basic Command Line UI

## Down The Line:

- Backup to cloud service (Google Drive for example)

- More Platforms for Posting and Promoting Content

- Platform Independent GUI

- Templates for content upload details and promotional posts

- Automation for Promotion

- Upload/Post Scheduling

## Do You Want To Help? (with Testing or Coding or thoughts):

 - **Discord:** Techie_Tiff#5008

 - **Email:** tiff@tiff.tech

### My Content Channels:

 - **Odysee:** https://odysee.com/@TechGirlTiff:5

 - **YouTube:** http://www.youtube.com/channel/UCidrHvFXBvyesh1hbOR2rTw
