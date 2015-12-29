__author__ = 'vahan'
import cv
import cv2
import math
import numpy as np
import Image
from Shape import Shape

#constants to change to improve recognition accuracy
CONTOUR_DETECTION_TUNING_CONST=0.026 #0.026
CONTOUR_AREA=150

#Set initial color limits

RED_MIN = np.array([165, 50, 0],np.uint8)
RED_MAX = np.array([180, 255, 255],np.uint8)

YELLOW_MIN = np.array([10, 50, 50],np.uint8)
YELLOW_MAX = np.array([45, 255, 255],np.uint8)

BLUE_MIN = np.array([105, 100, 100],np.uint8)
BLUE_MAX = np.array([120, 255, 255],np.uint8)




#array of colors
colors=["red","blue","yellow"]
#array of shapes
shapes = ["triangle","square","circle"]
#list of shapes
listOfShapes=[]


"""
    initialize list of shapes
"""
def initShapes():
    listOfShapes=[]
    for color in colors:
        for shape in shapes:
            listOfShapes.append(Shape(color,shape))
    return listOfShapes

"""
    reset list of shapes
"""
def resetShapes():
    for i in range(0,len(listOfShapes)):
        listOfShapes[i]=listOfShapes[i].reset()
    return listOfShapes

"""
    convert binary image from camera to OpenCV PIL image
    :param image:  binary image obtained from camera
"""
def convert2pil(image):
    cv_im = cv.CreateImageHeader(image.size, cv.IPL_DEPTH_8U, 3)
    r,g,b=image.split()
    pi2=Image.merge("RGB",(b,g,r))
    cv.SetData(cv_im, pi2.tobytes())
    return cv_im

"""
    detect the shape (triangle, square, circle) of color
    :param image: binary image obtained from camera
    :param color: given shape color
"""
def detectShape(image,color):
    if color=='red':
        (COLOR_MIN,COLOR_MAX)=(RED_MIN,RED_MAX)
    elif color=='blue':
        (COLOR_MIN,COLOR_MAX)=(BLUE_MIN,BLUE_MAX)
    elif color=='yellow':
        (COLOR_MIN,COLOR_MAX)=(YELLOW_MIN,YELLOW_MAX)

    #Convert to PIL image
    original = convert2pil(image)

    #smoothing and filtering
    preFrame=np.asarray(original[:,:])

    frame = cv2.fastNlMeansDenoisingColored(preFrame,None,2,2,3,9)

    #convert frame from BRG to HSV
    hsv_img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    # #draw an hsv image
    #showImage('hsv1_img',hsv_img)

    #Extract colored contours
    frame_threshed = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)
    thresh= frame_threshed.copy()

    # #draw recognized contours
    #showImage('gray_converted '+color,thresh)

    contours,h = cv2.findContours(thresh,1,2)
    for cnt in contours:

        approx = cv2.approxPolyDP(cnt,CONTOUR_DETECTION_TUNING_CONST*cv2.arcLength(cnt,True),True)

        if cv2.contourArea(approx)<CONTOUR_AREA or not(cv2.isContourConvex(approx)):
            #print "contour is not convex    ", len(approx)
            continue

        if len(approx)==3:
            listOfShapes[convert2index(color,"triangle")].addContours(approx)
            listOfShapes[convert2index(color,"triangle")].addCenters(getShapeCenter(approx))

        elif len(approx)==4:
            listOfShapes[convert2index(color,"square")].addContours(approx)
            listOfShapes[convert2index(color,"square")].addCenters(getShapeCenter(approx))

        else:
            listOfShapes[convert2index(color,"circle")].addContours(approx)
            listOfShapes[convert2index(color,"circle")].addCenters(getShapeCenter(approx))

    return frame

"""
    To find the detected shape's center coordinates in pixels
    :param contour: detected shape's contour
"""
def getShapeCenter(contour):
    #bounding rectangle
    x,y,w,h = cv2.boundingRect(contour)
    center = (int(x+w/2),int(y+h/2))
    return center


"""
    To return the index of given colored shape in the list of shapes
    :param c: color
    :param s: shape
"""
def convert2index(c, s):
    i = 0
    for color in colors:
        for shape in shapes:
            if c == color and s == shape:
                return i
            i += 1

"""
    draw the image
    :param imageFrame: numpy array frame
    :param windowName: titlee of the window
"""
def showImage(windowName, imageFrame):
    cv2.namedWindow(windowName)
    while True:
        #key = cv2.waitKey(33) #this won't work
        #key = 0xFF & cv2.waitKey(33) #this is ok
        cv2.imshow(windowName,imageFrame)
        key = np.int16(cv2.waitKey(33)) #this is ok [2]

        if key == 27:
            break
#        else:
#            continue
            #print key, hex(key), key % 256

    cv2.destroyAllWindows()