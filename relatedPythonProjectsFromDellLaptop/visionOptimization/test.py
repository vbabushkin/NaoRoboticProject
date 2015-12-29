__author__ = 'vahan'
__author__ = 'vahan'
import cv2
import shapeDetectionModule_v1
import Image
from naoqi import ALProxy
from naoqi import ALBroker
import numpy as np
import pickle

path = "/home/vahan/PycharmProjects/visionOptimization/images"
#
#Set initial color limits for green
GREEN_MIN_H=70
GREEN_MIN_S=50
GREEN_MIN_V=50
#
GREEN_MAX_H=100
GREEN_MAX_S=255
GREEN_MAX_V=255



#dictionary to store number of times the shapes have been detected
dictNumShapesDetected={}
dictNumShapesDetected["green"]={}
dictNumShapesDetected["green"]["triangle"]=[]
dictNumShapesDetected["green"]["pentagon"]=[]
dictNumShapesDetected["green"]["square"]=[]
dictNumShapesDetected["green"]["circle"]=[]

dictColorParameters={}
dictColorParameters["green"] = []

correctlyDetectedCases=[]

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
    cameraIndex=1
    resolution = 2 # VGA
    colorSpace = 11 # RGB
    #camProxy.setActiveCamera("python_client", cameraIndex)
    #videoClient = camProxy.subscribeCamera("python_client", cameraIndex, resolution, colorSpace, 30)
    videoClient=camProxy.subscribe("python_GVM", resolution, colorSpace, 30)

    colorMin = np.array([GREEN_MIN_H, GREEN_MIN_S, GREEN_MIN_V],np.uint8)#50,50,50
    colorMax = np.array([GREEN_MAX_H, GREEN_MAX_S, GREEN_MAX_V],np.uint8)#80,255,255
    probList=[]
    TIMES=5
    h_index=colorMin[1]
    s_index=colorMin[1]
    v_index=colorMin[2]
    # for h_index in range(colorMin[0], colorMin[0]+20):
    #     # for s_index in range(colorMin[1], colorMin[1]+3):
    #     #     for v_index in range(colorMin[2], colorMin[2]+3):
    WINDOW=20
    while h_index+WINDOW <=colorMax[1]:
                print (h_index,s_index,v_index)
                correctlyDetectedCases=[]
                tempColorMin = np.array([h_index, s_index, v_index],np.uint8)#50,50,50
                tempColorMax = np.array([h_index+WINDOW, GREEN_MAX_S, GREEN_MAX_V],np.uint8)#80,255,255
                dictColorParameters["green"].append((tempColorMin,tempColorMax))

                for numOfTimes in range(0,TIMES):
                    print "iteration # "+str(numOfTimes)
                    shapeDetectionModule_v1.listOfShapes=shapeDetectionModule_v1.initShapes()
                    #print shapeDetectionModule_v1.listOfShapes
                    img0 = getImage(camProxy, videoClient)
                    #detect shape of green color

                    frame=shapeDetectionModule_v1.detectShape(img0,tempColorMin,tempColorMax,"green")

                    t=shapeDetectionModule_v1.convert2index("green","triangle")
                    #p=shapeDetectionModule_v1.convert2index("green","pentagon")
                    s=shapeDetectionModule_v1.convert2index("green","square")
                    c=shapeDetectionModule_v1.convert2index("green","circle")

                    if len(shapeDetectionModule_v1.listOfShapes[t].getCenters())==1 and len(shapeDetectionModule_v1.listOfShapes[s].getCenters())==1 and len(shapeDetectionModule_v1.listOfShapes[c].getCenters())==1: #and len(shapeDetectionModule_v1.listOfShapes[p].getCenters())==1
                            correctlyDetectedCases.append(1)


                print len(correctlyDetectedCases)
                probList.append(len(correctlyDetectedCases)/float(TIMES))
                h_index+=2



    print "LIST OF CORRECTLY DETECTED CASES:"
    print correctlyDetectedCases

    print "INVESTIGATED COLOR PARAMETERS"
    print dictColorParameters

    print "DETECTION ACCURACY"
    print probList

    save_obj(dictColorParameters, "dictColorParameters")
    save_obj(probList, "probList")

    i=shapeDetectionModule_v1.convert2index("green","triangle")
    frame=outputResults(frame,i)

    # i=shapeDetectionModule_v1.convert2index("green","pentagon")
    # frame=outputResults(frame,i)

    i=shapeDetectionModule_v1.convert2index("green","square")
    frame=outputResults(frame,i)

    i=shapeDetectionModule_v1.convert2index("green","circle")
    frame=outputResults(frame,i)
    showImage('contour', frame)
    camProxy.unsubscribe(videoClient)

def outputResults(frame,i):
    # print i
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


def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name ):
    with open(name + '.pkl', 'r') as f:
        return pickle.load(f)


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


def drawContours(contours, frame):
    hue= (0,255,255)
    for cnt in contours:
                if len(contours)!=0:
                    cv2.drawContours(frame,[cnt],0,hue,-1)
    return frame


if __name__ == '__main__':
    IP = "10.104.68.16"
    PORT = 9559

    naoImage = mainModule(IP, PORT)

    cv2.destroyAllWindows()

