__author__ = 'vahan'

import cv2
import shapeDetectionModule_v1
import Image
from naoqi import ALProxy
from naoqi import ALBroker
import numpy as np
import pickle
import time

path = "/home/vahan/PycharmProjects/shapeDetection_v1/images"
#
#Set initial color limits for green


RED_MIN = np.array([165, 50, 0],np.uint8)
RED_MAX = np.array([180, 255, 255],np.uint8)

YELLOW_MIN = np.array([10, 50, 50],np.uint8)
YELLOW_MAX = np.array([45, 255, 255],np.uint8)

BLUE_MIN = np.array([105, 100, 100],np.uint8)
BLUE_MAX = np.array([120, 255, 255],np.uint8)

GREEN_MIN = np.array([55, 50, 0],np.uint8)
GREEN_MAX = np.array([83, 255, 255],np.uint8)


def getImage(camProxy,videoClient):

    naoImage= camProxy.getImageRemote(videoClient)
    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]

    #Create a PIL Image Instance from our pixel array.
    img0= Image.frombytes("RGB", (imageWidth, imageHeight), array)
     #Convert to PIL image
    return img0


def detectShape(img0,color):
    if color=='red':
        (COLOR_MIN,COLOR_MAX)=(RED_MIN,RED_MAX)
    elif color=='blue':
        (COLOR_MIN,COLOR_MAX)=(BLUE_MIN,BLUE_MAX)
    elif color=='yellow':
        (COLOR_MIN,COLOR_MAX)=(YELLOW_MIN,YELLOW_MAX)
    elif color=='green':
        (COLOR_MIN,COLOR_MAX)=(GREEN_MIN,GREEN_MAX)

    frame=shapeDetectionModule_v1.detectShape(img0,COLOR_MIN,COLOR_MAX,color)

    return frame


def mainModule(IP, PORT):
    t0 = time.time()
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
    resolution = 2 # VGA
    colorSpace = 11 # RGB

    videoClient = camProxy.subscribe("python_GVM", resolution, colorSpace, 30)

    #create an empty list of shapes:
    shapeDetectionModule_v1.listOfShapes=shapeDetectionModule_v1.initShapes()


    #get an image from Nao's camera
    img0 = getImage(camProxy, videoClient)

    #detect shape of given color

    for color in ["red", "green", "blue", "yellow"]:
        frame=detectShape(img0, color)

    #visualise
    for i in range(0,12):
        print shapeDetectionModule_v1.listOfShapes[i].getColor()
        print shapeDetectionModule_v1.listOfShapes[i].getShape()
        print shapeDetectionModule_v1.listOfShapes[i].getContours()
        print shapeDetectionModule_v1.listOfShapes[i].getCenters()

    #save the dictionary of Shape objects:
    save_obj(shapeDetectionModule_v1.listOfShapes, "shapesDetected" )

    #print the list of detected shapes:
    # for color in ["red","green","blue","yellow"]:
    #     for shape in ["triangle","square","circle"]:
    #         i=shapeDetectionModule_v1.convert2index(color,shape)
    #         frame=outputResults(frame,i)
    #
    # showImage('contour', frame)
    # cv2.imwrite(path+ "/recognizedImage.jpg", frame)
    camProxy.unsubscribe(videoClient)
    t1 = time.time()

    total = t1-t0

    print "TOTAL TIME REQUIRED: "
    print total



"""
    To visualize the results
    :param frame: image frame
    :param i: index in list of shapes
"""
def outputResults(frame,i):
    color= shapeDetectionModule_v1.listOfShapes[i].getColor()
    # print color
    shape= shapeDetectionModule_v1.listOfShapes[i].getShape()
    # print shape
    # print shapeDetectionModule_v1.listOfShapes[i].getCenters()
    frame=drawContours(shapeDetectionModule_v1.listOfShapes[i].getContours(),frame)
    contours=shapeDetectionModule_v1.listOfShapes[i].getContours()
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

#for saving dictionary of Shape objects
def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

#for loading dictionary of Shape objects
def load_obj(name ):
    with open(name + '.pkl', 'r') as f:
        return pickle.load(f)

#to visualize current frame
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

#for drawing contours on the frame (visualization)
def drawContours(contours, frame):
    hue= (0,255,255)
    for cnt in contours:
                if len(contours)!=0:
                    cv2.drawContours(frame,[cnt],0,hue,-1)
    return frame


if __name__ == '__main__':
    IP = "10.104.67.182"
    PORT = 9559

    naoImage = mainModule(IP, PORT)

    cv2.destroyAllWindows()

