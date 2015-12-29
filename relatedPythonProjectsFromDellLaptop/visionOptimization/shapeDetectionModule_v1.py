__author__ = 'vahan'
import cv
import cv2
import math
import numpy as np
import Image
from Shape import Shape


CONTOUR_DETECTION_TUNING_CONST=0.022
CONTOUR_AREA=150

#Set initial color limits for green
GREEN_MIN_H=70
GREEN_MIN_S=50
GREEN_MIN_V=50
#
GREEN_MAX_H=100
GREEN_MAX_S=255
GREEN_MAX_V=255




#array of colors
colors=["red","green","blue","yellow"]
#array of shapes
shapes = ["triangle","pentagon","square","circle"]

listOfShapes=[]

def initShapes():
    listOfShapes=[]
    for color in colors:
        for shape in shapes:
            listOfShapes.append(Shape(color,shape))
    return listOfShapes

def resetShapes():
    for i in range(0,len(listOfShapes)):
        listOfShapes[i]=listOfShapes[i].reset()
    return listOfShapes

# def setColorLimits(color,(hMin,sMin,vMin),(hMax,sMax,vMax)):
#     if color=="green":
#         GREEN_MIN[0]=hMin
#         GREEN_MIN[1]=sMin
#         GREEN_MIN[2]=vMin
#
#         GREEN_MAX[0]=hMax
#         GREEN_MAX[1]=sMax
#         GREEN_MAX[2]=vMax
#
#
# def getColorLimits(color):
#     if color=="green":
#         return (GREEN_MIN,GREEN_MAX)


def convert2pil(img):
    cv_im = cv.CreateImageHeader(img.size, cv.IPL_DEPTH_8U, 3)
    r,g,b=img.split()
    pi2=Image.merge("RGB",(b,g,r))
    cv.SetData(cv_im, pi2.tobytes())
    return cv_im

def detectShape(image, COLOR_MIN, COLOR_MAX, color):

    #Convert to PIL image
    original = convert2pil(image)

    #smoothing and filtering
    preFrame=np.asarray(original[:,:])
    frame = cv2.fastNlMeansDenoisingColored(preFrame,None,2,2,3,9)

    #convert frame from BRG to HSV
    hsv_img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    #draw an image
    #showImage('hsv1_img',hsv_img)

    #Extract colored contours
    frame_threshed = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)
    thresh= frame_threshed.copy()

    #draw an image
    #showImage('gray_converted',thresh)

    contours,h = cv2.findContours(thresh,1,2)
    for cnt in contours:

        approx = cv2.approxPolyDP(cnt,CONTOUR_DETECTION_TUNING_CONST*cv2.arcLength(cnt,True),True)

        if cv2.contourArea(approx)<CONTOUR_AREA or not(cv2.isContourConvex(approx)):
            #print "contour is not convex    ", len(approx)
            continue

        if len(approx)==3:
            listOfShapes[convert2index(color,"triangle")].addContours(approx)
            listOfShapes[convert2index(color,"triangle")].addCenters(getShapeCenter(approx))

        elif len(approx)==5:
            listOfShapes[convert2index(color,"pentagon")].addContours(approx)
            listOfShapes[convert2index(color,"pentagon")].addCenters(getShapeCenter(approx))

        elif len(approx)==4:
            listOfShapes[convert2index(color,"square")].addContours(approx)
            listOfShapes[convert2index(color,"square")].addCenters(getShapeCenter(approx))

        else:
            listOfShapes[convert2index(color,"circle")].addContours(approx)
            listOfShapes[convert2index(color,"circle")].addCenters(getShapeCenter(approx))

    return frame


def getShapeCenter(cnt):
    #bounding rectangle
    x,y,w,h = cv2.boundingRect(cnt)
    center = (int(x+w/2),int(y+h/2))
    return center



def convert2index(c, s):
    i = 0
    for color in colors:
        for shape in shapes:
            if c == color and s == shape:
                return i
            i += 1





# if __name__ == '__main__':
#     print listOfShapes
#     listOfShapes=initShapes()
#     print listOfShapes
#     print listOfShapes[0].getColor()
#     print listOfShapes[0].getShape()
#     listOfShapes[0].setColor("blue")
#     i=convert2index("yellow","circle")
#     print i
#     print listOfShapes[i].getColor()
#     print listOfShapes[i].getShape()
#     #listOfShapes=resetShapes()
#     listOfShapes=initShapes()
#     print listOfShapes
#     print listOfShapes[0].getColor()
#     print listOfShapes[0].getShape()


