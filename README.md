# ContentCreatorManager
Tool for small content creators to manage thier content on multiple platforms

still under dev proper readme to come

currently working on reorganizing into multiple files and changing the class structure

downloading working even for private videos on youtube with pytube as long as o_auth is used and this install was used python -m pip install git+https://github.com/tfdahlin/pytube.git@fix/1097 and fix from https://github.com/pytube/pytube/issues/1243 to cipher.py

thumbnail functionality working

Started working towards making youtube-dl an option and even the default option but due to it not having a good option for downloading private videos like pytube (I am able to get it to auth once and the oauth token caches) I have made pytube default and left youtube-dl in an unfinished state but may return to it one day