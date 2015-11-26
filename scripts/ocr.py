import matplotlib.pyplot as plt
import numpy as np
import cv2
import copy

from pylab import imread, imshow, figure, show, subplot, plot, scatter
from scipy.cluster.vq import kmeans, vq

# from skimage import data, img_as_uint, img_as_float
# from skimage.external.tifffile import imsave
# from skimage.filters import threshold_otsu, threshold_adaptive, threshold_yen
# from skimage.segmentation import clear_border


# returns the image with digits boxed
def crop_digit(imgName, boundingRectMinSize):
    img = cv2.imread(imgName)
    thresh = binary_filter(img)
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    idx = 0 
    for cnt in contours:
        if cnt.shape[0] >= boundingRectMinSize:
            idx += 1
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)      # draw box on original image
    return img


# crop the digit and save as binary files, then return the boxed digits
def save_digit_to_binary_img(imgName, boundingRectMinSize):
    img = cv2.imread(imgName)
    imgToShow = copy.copy(img)
    thresh = binary_filter(img)
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    idx = 0 
    for cnt in contours:
        if cnt.shape[0] >= boundingRectMinSize:
            idx += 1
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(imgToShow,(x,y),(x+w,y+h),(0,255,0),1)

            # crop out the image, threshold it and save as binary image
            crop_img = img[y: y + h, x: x + w]   # img[y: y + h, x: x + w]
            grayed_im  = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
            # blur = cv2.GaussianBlur(grayed_im,(5, 5), 0)  
            ret,thresh = cv2.threshold(grayed_im, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # resize image to fit mnist dataset
            resized_img = resize(thresh, 28.)
            print resized_img.shape
            cv2.imwrite('../pics/cropped/' + str(idx) + '.png', resized_img)
    return imgToShow


def binary_filter(img):
    """ takes in a colored img and returns the binary threshold """
    blur = cv2.GaussianBlur(img,(5, 5), 0)  
    edge = cv2.Canny(blur, 50, 50)
    # ret,thresh = cv2.threshold(edge,127,255,cv2.THRESH_OTSU)
    # Otsu's thresholding after Gaussian filtering and Canny edge detection
    ret,thresh = cv2.threshold(edge,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    return thresh

def resize(img, size):
    """ resize the image to fit in the size x size matrix """
    r = float(size) / img.shape[1]
    dim = (int(size), int(img.shape[0] * r))
    resized_img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return resized_img

# obsolete code



# K means on color filtering, it doesn't clear out the background very well
# produces thick edge that connects digits together causion confusion
def img_kmeans(imgFile, k):
    img = imread(imgFile)
    # reshaping the pixels matrix to read in for k means
    pixel = np.reshape(img, (img.shape[0] * img.shape[1], 3))

    # performing the clustering on shaped pixels
    centroids, _ = kmeans(pixel, k)      # centeroids contains the 2 representative color of the image

    # quantization of 2 for color
    qnt, _ = vq(pixel, centroids)

    # reshaping the result of the quantization, clustered contains the cluster numbers
    clustered = np.reshape(qnt, (img.shape[0], img.shape[1]))   
    clustered_color = centroids[clustered]   #color the clustered
    return clustered, clustered_color


# binary matrix to position is used to convert binary image to positional matrix of each 
# non white pixel, it is then used for k means to cluster the digits into groups
# It didn't go well because digits sometimes are connected so they are often clustered together
def binary_matrix_to_position(binMat):
    """ takes in n x n binary True False color matrix and output a 
        n*n x 1 position matrix represent the position of colored digits 
    """
    binPosMat = np.empty((0,2), int)
    # go through the clustered matrix and get the position of the pixel that's not white
    for (x,y), pixel in np.ndenumerate(binMat):
        pixelColor =  binMat[x,y]
        if pixelColor == False:
            binPos = np.empty((1,2), int)
            binPos[0,0] = x
            binPos[0,1] = y
            binPosMat = np.append(binPosMat, binPos, axis=0)

    # flip the matrix
    return binPosMat


def binary_matrix_to_position_num(binMat):
    """ takes in n x n binary True False color matrix and output a 
        n*n x 1 position matrix represent the position of colored digits 
    """
    binPosMat = np.empty((0,2), int)
    # go through the clustered matrix and get the position of the pixel that's not white
    for (x,y), pixel in np.ndenumerate(binMat):
        pixelColor =  binMat[x,y]
        if pixelColor > 0:
            binPos = np.empty((1,2), int)
            binPos[0,0] = x
            binPos[0,1] = y
            binPosMat = np.append(binPosMat, binPos, axis=0)

    # flip the matrix
    return binPosMat

def binary_matrix_to_position_2(clustered):
    """ we assume the first color pixel that's most upper left of the image is not the 
    color of the number, a quick fix 
    """
    not_digit_color = clustered[1,1]

    binPosMat = np.empty((0,2), int)
    # go through the clustered matrix and get the position of the pixel that represent a digit
    for (x,y), pixel in np.ndenumerate(clustered):
        pixelColor =  clustered[x,y]
        if pixelColor != not_digit_color:
            binPos = np.empty((1,2), int)
            binPos[0,0] = x
            binPos[0,1] = y
            binPosMat = np.append(binPosMat, binPos, axis=0)

    return binPosMat
        
