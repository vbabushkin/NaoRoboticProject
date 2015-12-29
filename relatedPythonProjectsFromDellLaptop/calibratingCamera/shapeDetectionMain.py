__author__ = 'vahan'

import cv2
import shapeDetectionModule
import Image
from naoqi import ALProxy
from naoqi import ALBroker
import numpy as np
import pickle

path = "/home/vahan/PycharmProjects/calibratingCamera/images"
#
#Set initial color limits for green


RED_MIN = np.array([170, 50, 0],np.uint8)
RED_MAX = np.array([180, 255, 255],np.uint8)

YELLOW_MIN = np.array([10, 50, 50],np.uint8)
YELLOW_MAX = np.array([45, 255, 255],np.uint8)

BLUE_MIN = np.array([105, 100, 100],np.uint8)
BLUE_MAX = np.array([120, 255, 255],np.uint8)

GREEN_MIN = np.array([55, 50, 0],np.uint8)
GREEN_MAX = np.array([83, 255, 255],np.uint8)


#dictionary to store number of times the shapes have been detected


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
    resolution = 2 # VGA
    colorSpace = 11 # RGB

    videoClient = camProxy.subscribe("python_GVM", resolution, colorSpace, 30)


    #get an image from Nao's camera
    img0 = getImage(camProxy, videoClient)

    #get dictionary of centers
    dictOfCenters=shapeDetectionModule.getDetectedShapesCenters(img0,shapeDetectionModule.dict)

    #visualise
    frame = shapeDetectionModule.visualize(img0, shapeDetectionModule.dict)

    # #printing dictionary of centers:
    # print dictOfCenters

    #print the list of detected shapes:
    for color in ["red","green","blue","yellow"]:
        for shape in ["triangle","square","circle"]:
            print color, shape, dictOfCenters[color][shape]

    #place bounding squares and centers on the frame
    #frame=shapeDetectionModule.outputResults(frame)

    #show the recognized image
    #####################################################################################################################
    # UNCOMMENT TO SEE THE RECOGNIZED PICTURE

    #showImage('contour', frame)

    #save the recognized image
    #cv2.imwrite(path+ "/recognizedImage.jpg", frame)

    #save the dictionaryOfCenters:
    #save_obj(dictOfCenters,"dictOfCenters")
    camProxy.unsubscribe(videoClient)
    return dictOfCenters






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

