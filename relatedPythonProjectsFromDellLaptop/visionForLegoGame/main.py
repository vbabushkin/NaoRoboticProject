__author__ = 'vahan'
import cv2
import shapeDetectionModule
import Image
from naoqi import ALProxy
from naoqi import ALBroker
import numpy as np

path = "/home/vahan/PycharmProjects/visionForLegoGame/images"


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


    # Get a camera image.
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)


    camProxy.unsubscribe(videoClient)

    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]

    #Create a PIL Image Instance from our pixel array.
    img0= Image.frombytes("RGB", (imageWidth, imageHeight), array)
     #Convert to PIL image
    original=shapeDetectionModule.convert2pil(img0)

    #convert to numpy array
    frame=np.asarray(original[:,:])
    #frame = shapeDetectionModule.visualize(img0, shapeDetectionModule.dict)

    #shapeDetectionModule.showImage('contour', frame)

    dict={}
    dict=shapeDetectionModule.getDetectedShapesCenters(img0,shapeDetectionModule.dict)

    #array of colors
    colors=["red","green","blue","yellow"]
    #array of shapes
    shapes = ["triangle","pentagon","square","circle"]

    #iterate over all colors and show contours of shape of corresponding color
    for color in colors:
        for shape in shapes:
            centers=dict[color][shape]
            print (color+" "+shape+" ",centers)
            if len(centers)!=0:
                for center in centers:
                      cv2.circle(frame, (int(center[0]),int(center[1])), 3, (255, 0, 0), -1)
                      text=str(int(center[0]))+" , "+str(int(center[1]))
                      cv2.putText(frame,text, (int(center[0]), int(center[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (255,255,255),1)
#                cv2.circle(frame, center, radius, (0, 255, 0), 1)

    shapeDetectionModule.showImage('contour', frame)
    cv2.imwrite(path+ "/recognizedImage.jpg", frame)

#TODO
#change the rectangle with min area to just a rectangle:
#
#
# def labelDetectedObject(cnt, frame, text):
#     #bounding rectangle
#     x,y,w,h = cv2.boundingRect(cnt)
#     cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
#     center = (int(x+w/2),int(y+h/2))
#     centerCoords="( "+str(int(center[0]))+" , "+str(int(center[1]))+" )"
#     cv2.putText(frame,text, (int(center[0]), int(center[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (255,255,255),1)
#     cv2.putText(frame,centerCoords, (int(center[0]), int(center[1]+10)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.4, (0,255,255),1)
#     #put a circle in the center

    cv2.circle(frame,center,3,(0, 0, 255),-1,8,0)
if __name__ == '__main__':
    IP = "10.104.65.96"
    PORT = 9559
    naoImage = mainModule(IP, PORT)
    cv2.destroyAllWindows()

