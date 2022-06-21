# ContentCreatorManager

## What Is This?

This aims to be a tool for small content creators to manage and promote their content on as many platforms as possible.  This tool should make it so that once set up a content creator has to do the same amount of or less work than managing one platform and still get their content everywhere and announced everywhere.

While the goals for this thing are big, it is still heavily under development.  The most alpha version of the first GUI for this has just come out

Previously there were some scripts in this project to make use of the code and while still present on the [GitHub](https://github.com/tiff1002/ContentCreatorManager) they likely do not work without some tweaking at this point so use at your own risk.  Hell all of this is use at your own risk :P

## What Can This App Currently Do?

The most current version of the app (second_gui_test.py) can load in your YouTube Videos.  It can determine if they are downloaded on the system or not.  It will show you which ones it can not find and you can tell it where they are or you can download them from YouTube.

It can do the same thing for LBRY.

In addition to this is can determine which videos are on one platform and not the other and provide you the ability to upload all or some of those videos

## How Do I Use this?

You will need to set up a Project in [Google Dev Console](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwipmYuq7vH2AhVJSzABHXZkAI4QFnoECAcQAQ&url=https%3A%2F%2Fconsole.developers.google.com%2F&usg=AOvVaw39ieEDI7pzBj4NtuzqS57M) and give it access to the Youtube Data API v3.  You will need the client id project id and client secrets.

Well first thing you will need is the latest version of Python installed for your system.  [Python Downloads Page](https://www.python.org/downloads/)

In addition to this there are several Python libraries you will need to install with pip:

`pip install shortuuid ffmpeg-python Pillow pytube requests httplib2 google_auth google_auth_oauthlib google-api-python-client`

And in linux, the tkinter package for the GUI:

`apt install python3-tk`

You will also need the [LBRY Desktop App](https://lbry.com/get) installed and running

Finally you will need [FFMPEG](https://www.ffmpeg.org/download.html) Binaries for your system and they will need to be in the system's path.  How to do this will depend on your OS.  You will know you got it working if on command line (CMD or Powershell on windows, Terminal on Mac, any number of terminal emulators on Linux) you can run ffmpeg from any directory.

Once you have all these requirements met you can download this project via the git clone command or just downloading the .zip archive of the project from [GitHub](https://github.com/tiff1002/ContentCreatorManager) and run the program.

To run the program you will go into the src directory and run python second_gui_test.py

Once you do this you will get prompted to select a directory and this will be the directory that the application will use to run.

Alternatively you can run python second_gui_test.py "PATH TO APP DIR" to skip the dialog asking for a directory for the application.

Using the application should be fairly straight forward, but I will make some videos on how to install and use and link to them here.

## I NEED HELP:

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
