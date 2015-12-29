__author__ = 'vahan'
from pylab import *
import Image
import filtertools
import harris
import time
import cv
import cv2
import math
import numpy as np
from naoqi import ALProxy
from naoqi import ALBroker

################################################################################################
## DICTIONARY TO STORE COLORED SHAPES
################################################################################################
dict={}

dict["red"]={}
dict["yellow"]={}
dict["blue"]={}
dict["green"]={}

dict["red"]["triangle"]=[]
dict["red"]["pentagon"]=[]
dict["red"]["square"]=[]
dict["red"]["circle"]=[]

dict["yellow"]["triangle"]=[]
dict["yellow"]["pentagon"]=[]
dict["yellow"]["square"]=[]
dict["yellow"]["circle"]=[]

dict["blue"]["triangle"]=[]
dict["blue"]["pentagon"]=[]
dict["blue"]["square"]=[]
dict["blue"]["circle"]=[]

dict["green"]["triangle"]=[]
dict["green"]["pentagon"]=[]
dict["green"]["square"]=[]
dict["green"]["circle"]=[]

################################################################################################
## COLOR DEFINITIONS
################################################################################################
RED_MIN = np.array([130, 50, 50],np.uint8)  #150 for red 110 for blue
RED_MAX = np.array([180, 255, 255],np.uint8)#180 for red 130 for blue

YELLOW_MIN = np.array([10, 50, 50],np.uint8)  #150 for red 110 for blue
YELLOW_MAX = np.array([45, 255, 255],np.uint8)#180 for red 130 for blue

BLUE_MIN = np.array([100, 50, 50],np.uint8)  #150 for red 110 for blue
BLUE_MAX = np.array([130, 255, 255],np.uint8)#180 for red 130 for blue

GREEN_MIN = np.array([50, 50, 50],np.uint8)
GREEN_MAX = np.array([80, 255, 255],np.uint8)

################################################################################################
## PATH
################################################################################################
path = "/home/vahan/PycharmProjects/coloredShapeDetectionHarris/images"



################################################################################################
## FUNCTIONS
################################################################################################
def convert2pil(img):
    cv_im = cv.CreateImageHeader(img.size, cv.IPL_DEPTH_8U, 3)
    r,g,b=img.split()
    pi2=Image.merge("RGB",(b,g,r))
    cv.SetData(cv_im, pi2.tobytes())
    return cv_im

def showImage(WINDOW_NAME, img):
    cv2.namedWindow(WINDOW_NAME)
    while True:
        #key = cv2.waitKey(33) #this won't work
        #key = 0xFF & cv2.waitKey(33) #this is ok
        cv2.imshow(WINDOW_NAME,img)
        key = np.int16(cv2.waitKey(33)) #this is ok [2]

        if key == 27:
            break
#        else:
#            continue
            #print key, hex(key), key % 256

def mainModule(IP, PORT):
    """
    First get an image from Nao, then show it on the screen with PIL.
    :param IP:
    :param PORT:
    """
    myBroker = ALBroker("myBroker",
        "0.0.0.0", # listen to anyone
        0, # find a free port and use it
        IP, # parent broker IP
        PORT) # parent broker port

    camProxy = ALProxy("ALVideoDevice", IP, PORT)
    cameraIndex=1
    resolution = 2 # VGA
    colorSpace = 11 # RGB
    #camProxy.setActiveCamera("python_client", cameraIndex)
    videoClient = camProxy.subscribeCamera("python_client", cameraIndex, resolution, colorSpace, 30)


    # resolution = vision_definitions.kVGA
    # colorSpace = vision_definitions.kRGBColorSpace
    # fps = 30
    #
    # videoClient = camProxy.subscribe("python_GVM", resolution, colorSpace, fps)



    t0 = time.time()

    # Get a camera image.
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)

    t1 = time.time()

    # Time the image transfer.
    #print "Runde: ", b

    camProxy.unsubscribe(videoClient)


    # Now we work with the image returned and save it as a PNG using ImageDraw
    # package.

    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]

    #Create a PIL Image Instance from our pixel array.
    img0= Image.frombytes("RGB", (imageWidth, imageHeight), array)

    image=img0

    #Convert to PIL image
    original=convert2pil(image)

    #convert to numpy array
    frame=np.asarray(original[:,:])
    print type(frame)
    #frame = cv2.bilateralFilter(preFrame,9,75,75)

    #showImage('blured',frame)

    #convert frame from BRG to HSV
    hsv_img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    showImage('hsv1_img',hsv_img)

    (COLOR_MIN,COLOR_MAX)=(RED_MIN,RED_MAX)

    #Extract colored contours
    frame_threshed = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)
    thresh= frame_threshed.copy()

    showImage('gray_converted',thresh)


    cv2.imwrite(path+ "/thresh.jpg", thresh)


    img = cv2.imread(path+ "/thresh.jpg")
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray,2,3,0.02)

    #result is dilated for marking the corners, not important
    dst = cv2.dilate(dst,None)

    # # Threshold for an optimal value, it may vary depending on the image.
    # img[dst>0.01*dst.max()]=[0,0,255]
    #
    # cv2.imshow('dst',img)
    # if cv2.waitKey(0) & 0xff == 27:
    #     cv2.destroyAllWindows()


    ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
    dst = np.uint8(dst)

    # find centroids
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

    # define the criteria to stop and refine the corners
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)

    # Now draw them
    res = np.hstack((centroids,corners))
    res = np.int0(res)
    img[res[:,1],res[:,0]]=[0,0,255]
    img[res[:,3],res[:,2]] = [0,255,0]

    cv2.imshow('dst',img)





    # image=Image.open(path+'/recognizedImage.jpg').convert("L")
    # harrisim = harris.compute_harris_response(image)
    # filtered_coords = harris.get_harris_points(harrisim,10,0.05)
    # harris.plot_harris_points(image, filtered_coords)



if __name__ == '__main__':
    IP = "10.104.67.41"
    PORT = 9559
    naoImage = mainModule(IP, PORT)
    cv2.destroyAllWindows()


# image=Image.open(path+'/initialImage.jpg').convert("RGBA")
# print type(image)
# im = array(image)

#
#
# frame=np.asarray(im[:,:])
#
# #convert frame from BRG to HSV
#
# hsv_img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
#
# #Extract colored contours
# frame_threshed = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)
# thresh= frame_threshed.copy()
#
#
# print type(thresh)
#
#

#





#


