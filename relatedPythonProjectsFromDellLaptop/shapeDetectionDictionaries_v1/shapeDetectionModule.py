__author__ = 'vahan'

import cv
import cv2
import math
import numpy as np
import Image
import main


CONTOUR_DETECTION_TUNING_CONST=0.03
CONTOUR_AREA=150
path = "/home/vahan/PycharmProjects/visionForLegoGame/images"

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


###########################################################################
# Dictionary containing centers of detected shapes
dictOfCenters={}

dictOfCenters["red"]={}
dictOfCenters["yellow"]={}
dictOfCenters["blue"]={}
dictOfCenters["green"]={}

dictOfCenters["red"]["triangle"]=[]
dictOfCenters["red"]["pentagon"]=[]
dictOfCenters["red"]["square"]=[]
dictOfCenters["red"]["circle"]=[]

dictOfCenters["yellow"]["triangle"]=[]
dictOfCenters["yellow"]["pentagon"]=[]
dictOfCenters["yellow"]["square"]=[]
dictOfCenters["yellow"]["circle"]=[]

dictOfCenters["blue"]["triangle"]=[]
dictOfCenters["blue"]["pentagon"]=[]
dictOfCenters["blue"]["square"]=[]
dictOfCenters["blue"]["circle"]=[]

dictOfCenters["green"]["triangle"]=[]
dictOfCenters["green"]["pentagon"]=[]
dictOfCenters["green"]["square"]=[]
dictOfCenters["green"]["circle"]=[]


def initDictionary():
    dictOfCenters={}

    dictOfCenters["red"]={}
    dictOfCenters["yellow"]={}
    dictOfCenters["blue"]={}
    dictOfCenters["green"]={}

    dictOfCenters["red"]["triangle"]=[]
    dictOfCenters["red"]["pentagon"]=[]
    dictOfCenters["red"]["square"]=[]
    dictOfCenters["red"]["circle"]=[]

    dictOfCenters["yellow"]["triangle"]=[]
    dictOfCenters["yellow"]["pentagon"]=[]
    dictOfCenters["yellow"]["square"]=[]
    dictOfCenters["yellow"]["circle"]=[]

    dictOfCenters["blue"]["triangle"]=[]
    dictOfCenters["blue"]["pentagon"]=[]
    dictOfCenters["blue"]["square"]=[]
    dictOfCenters["blue"]["circle"]=[]

    dictOfCenters["green"]["triangle"]=[]
    dictOfCenters["green"]["pentagon"]=[]
    dictOfCenters["green"]["square"]=[]
    dictOfCenters["green"]["circle"]=[]
    return dictOfCenters


#########################################################################


RED_MIN = np.array([170, 50, 0],np.uint8)
RED_MAX = np.array([180, 255, 255],np.uint8)

YELLOW_MIN = np.array([10, 50, 50],np.uint8)
YELLOW_MAX = np.array([45, 255, 255],np.uint8)

BLUE_MIN = np.array([105, 100, 100],np.uint8)
BLUE_MAX = np.array([120, 255, 255],np.uint8)

GREEN_MIN = np.array([55, 50, 0],np.uint8)
GREEN_MAX = np.array([83, 255, 255],np.uint8)




#visualize detected shapes
def visualize(image, dict):
    #Convert to PIL image
    original=convert2pil(image)

    #convert to numpy array
    frame=np.asarray(original[:,:])

    #showImage('initial Image', frame)

    cv2.imwrite(path+ "/initialImage.jpg", frame)
    #array of colors
    colors=["red","green","blue","yellow"]
    #array of shapes
    shapes = ["triangle","pentagon","square","circle"]

    #iterate over all colors and show contours of shape of corresponding color
    for color in colors:
        #detect shape for each color
        detectShape(image, color)

        for shape in shapes:
            if shape == "triangle":
                hue=(0,255,0)
            elif shape == "pentagon":
                hue=(255,0,0)
            elif shape == "square":
                hue=(0,0,255)
            elif shape == "circle":
                hue= (0,255,255)
            contours=dict[color][shape]
            for cnt in contours:
                if len(contours)!=0:
                    cv2.drawContours(frame,[cnt],0,hue,-1)
                    labelDetectedObject(cnt, frame,color+" "+shape)
    return frame


#return detected shapes coordinates
def getDetectedShapesCenters(image,dict):
    #Convert to PIL image
    original=convert2pil(image)

    #convert to numpy array
    frame=np.asarray(original[:,:])

    #array of colors
    colors=["red","green","blue","yellow"]
    #array of shapes
    shapes = ["triangle","pentagon","square","circle"]

    #iterate over all colors and show contours of shape of corresponding color
    for color in colors:
        #detect shape for each color
        detectShape(image, color)
        for shape in shapes:
            contours=dict[color][shape]
            for cnt in contours:
                if len(contours)!=0:
                    object_rect=cv2.minAreaRect(cnt)
                    box = cv2.cv.BoxPoints(object_rect)
                    box = np.int0(box)
                    minX=min(box[0][0],box[1][0],box[2][0],box[3][0])
                    minY=min(box[0][1],box[1][1],box[2][1],box[3][1])
                    maxX=max(box[0][0],box[1][0],box[2][0],box[3][0])
                    maxY=max(box[0][1],box[1][1],box[2][1],box[3][1])
                    center = (math.fabs(minX+(maxX-minX)/2.0), math.fabs(minY+(maxY-minY)/2.0))
                    dictOfCenters[color][shape].append(center)
                    #cv2.putText(frame,text, (int(center[0]), int(center[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (255,255,255),1)

    return dictOfCenters



"""
    To visualize the results
    :param frame: image frame
"""
def outputResults(frame):
    #array of colors
    colors=["red","green","blue","yellow"]
    #array of shapes
    shapes = ["triangle","pentagon","square","circle"]

    for color in colors:
        for shape in shapes:
            contours= dict[color][shape]
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                center = (int(x+w/2),int(y+h/2))
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

                centerCoords="( "+str(int(center[0]))+" , "+str(int(center[1]))+" )"
                text= color+" "+shape
                cv2.putText(frame,text, (int(center[0]), int(center[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (255,255,255),1)

                cv2.putText(frame,centerCoords, (int(center[0]), int(center[1]+10)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.4, (255,0,0),1)
                #put a green circle in the center
                cv2.circle(frame,(int(center[0]), int(center[1])),3,(0, 255, 0),-1,8,0)
    return frame

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

def convert2pil(img):
    cv_im = cv.CreateImageHeader(img.size, cv.IPL_DEPTH_8U, 3)
    r,g,b=img.split()
    pi2=Image.merge("RGB",(b,g,r))
    cv.SetData(cv_im, pi2.tobytes())
    return cv_im

def HSVColorValues(color):
    hsv_color = cv2.cvtColor(color,cv2.COLOR_BGR2HSV)
    return hsv_color



#to select detected objects to the main frame
def selectDetected(object_rect,frame):
    points = []
    box = cv2.cv.BoxPoints(object_rect)
    box = np.int0(box)
    minX=min(box[0][0],box[1][0],box[2][0],box[3][0])
    minY=min(box[0][1],box[1][1],box[2][1],box[3][1])
    maxX=max(box[0][0],box[1][0],box[2][0],box[3][0])
    maxY=max(box[0][1],box[1][1],box[2][1],box[3][1])
    center = (math.fabs(minX+(maxX-minX)/2.0), math.fabs(minY+(maxY-minY)/2.0))
    circleCenter=(int(center[0]), int(center[1]))
    cv2.drawContours(frame,[box],0,(0,0,255),2)
    cv2.circle(frame,circleCenter,3,(0, 255, 0),-1,8,0)
    return frame



def detectShape(image,color):
    if color=='red':
        (COLOR_MIN,COLOR_MAX)=(RED_MIN,RED_MAX)
    elif color=='blue':
        (COLOR_MIN,COLOR_MAX)=(BLUE_MIN,BLUE_MAX)
    elif color=='yellow':
        (COLOR_MIN,COLOR_MAX)=(YELLOW_MIN,YELLOW_MAX)
    elif color=='green':
        (COLOR_MIN,COLOR_MAX)=(GREEN_MIN,GREEN_MAX)
    #Convert to PIL image
    original=convert2pil(image)
    #convert to numpy array
    frame=np.asarray(original[:,:])


    #smoothing and filtering

    preFrame=np.asarray(original[:,:])
    frame = cv2.fastNlMeansDenoisingColored(preFrame,None,2,2,3,9)

    #convert frame from BRG to HSV
    hsv_img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    #showImage('hsv1_img',hsv_img)


    #Extract colored contours
    frame_threshed = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)
    thresh= frame_threshed.copy()

    #showImage('gray_converted',thresh)


    contours,h = cv2.findContours(thresh,1,2)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt,CONTOUR_DETECTION_TUNING_CONST*cv2.arcLength(cnt,True),True)
        if cv2.contourArea(cnt)<CONTOUR_AREA or not(cv2.isContourConvex(approx)):
            #print "contour is not convex    ", len(approx)
            continue
        if len(approx)==3:
            dict[color]["triangle"].append(cnt)
        elif len(approx)==5:
            dict[color]["pentagon"].append(cnt)
        elif len(approx)==4:
            dict[color]["square"].append(cnt)
        else:
            dict[color]["circle"].append(cnt)
    return frame



def labelDetectedObject(cnt, frame, text):
    object_rect=cv2.minAreaRect(cnt)
    box = cv2.cv.BoxPoints(object_rect)
    box = np.int0(box)
    minX=min(box[0][0],box[1][0],box[2][0],box[3][0])
    minY=min(box[0][1],box[1][1],box[2][1],box[3][1])
    maxX=max(box[0][0],box[1][0],box[2][0],box[3][0])
    maxY=max(box[0][1],box[1][1],box[2][1],box[3][1])
    center = (math.fabs(minX+(maxX-minX)/2.0), math.fabs(minY+(maxY-minY)/2.0))
    cv2.putText(frame,text, (int(center[0]), int(center[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (255,255,255),1)





