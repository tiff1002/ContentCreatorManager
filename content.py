'''
Created on Feb 9, 2022

@author: tiff
'''
import cv2
import numpy as np


def lbry_youtube_video_compare(lbry_video, youtube_video):
    differences = {'lbry':{},'youtube':{},'count':0}
    
    if lbry_video.title != youtube_video.title:
        differences['lbry']['title'] = lbry_video.title
        differences['youtube']['title'] = youtube_video.title
        differences['count'] += 1
    
    if lbry_video.description != youtube_video.description:
        differences['lbry']['description'] = lbry_video.title
        differences['youtube']['description'] = youtube_video.title
        differences['count'] += 1
        
    if lbry_video.tags != youtube_video.tags:
        differences['lbry']['tags'] = lbry_video.title
        differences['youtube']['tags'] = youtube_video.title
        differences['count'] += 1
    
    return differences

def lbry_youtube_channel_compare(lbry_channel, youtube_channel):
    lbry_vids = lbry_channel.videos
    youtube_vids = youtube_channel.videos

    vids_missing_from_lbry = []
    vids_missing_from_youtube = []
    
    for x in lbry_vids:
        found = False
        for y in youtube_vids:
            compare = lbry_youtube_video_compare(x, y)
            if compare['count'] == 0:
                found = True
                
        if not found:
            vids_missing_from_youtube.append(x)
            
    for x in youtube_vids:
        found = False
        for y in lbry_vids:
            compare = lbry_youtube_video_compare(x, y)
            if compare['count'] == 0:
                found = True
                
        if not found:
            vids_missing_from_lbry.append(x)        
    
    
    result = {'lbry':{'missing':vids_missing_from_lbry},'youtube':{'missing':vids_missing_from_youtube}}
    return result

def compare_images(img1, img2, settings):
    file_1 = cv2.imread(img1)
    file_2 = cv2.imread(img2)
    difference = cv2.subtract(file_1, file_2)
    f_r = not np.any(difference)
    
    if f_r:
        settings.Base_Method_logger.info(f"{img1} matches {img2}")
        settings.Base_Method_logger.info("Returning True")
        return True
    else:
        settings.Base_Method_logger.info(f"{img1} does not match {img2}")
        settings.Base_Method_logger.info("returning False")
        return False

#Function to return a string that is a valid filename based on string given
def getValidFilename(filename):
    valid_chars = '`~!@#$%^&+=,-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    getVals = list([val for val in filename if val in valid_chars])
    return "".join(getVals)

# Function to get filename from given stream
def getInputFilename(stream):
    while stream.node._KwargReprNode__incoming_edge_map != {}:
        stream = stream.node._KwargReprNode__incoming_edge_map[None][0]
        if not hasattr(stream, 'node'):
            return stream.__dict__['kwargs']['filename']
    return stream.node.__dict__['kwargs']['filename']