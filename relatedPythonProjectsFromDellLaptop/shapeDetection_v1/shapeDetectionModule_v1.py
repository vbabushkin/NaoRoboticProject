__author__ = 'vahan'
import cv
import cv2
import math
import numpy as np
import Image
from Shape import Shape

#constants to change to improve recognition accuracy
CONTOUR_DETECTION_TUNING_CONST=0.026
CONTOUR_AREA=150






#array of colors
colors=["red","green","blue","yellow"]
#array of shapes
shapes = ["triangle","square","circle"]

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

    #draw an hsv image
    #showImage('hsv1_img',hsv_img)

    #Extract colored contours
    frame_threshed = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)
    thresh= frame_threshed.copy()

    #draw recognized contours
    showImage('contours of '+color,thresh)

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

    cv2.destroyAllWindows()

##testing the performance

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


