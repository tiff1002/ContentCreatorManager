'''
Created on Feb 9, 2022

@author: tiff
'''
import cv2
import numpy as np



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