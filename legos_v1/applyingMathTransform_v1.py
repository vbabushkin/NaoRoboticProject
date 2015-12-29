__author__ = 'vahan'
__author__ = 'vahan'

import cv2
import shapeDetectionModuleInterface
import shapeDetectionModule
import time
import random
from naoqi import ALProxy
import motion
import math
import almath
import numpy as np


# Set here the current camera ("CameraTop" or "CameraBottom").
currentCamera            = "CameraBottom"

# Set here the size of the landmark in meters.
landmarkTheoreticalSize = 0.0195
ALPHA=30.485#21.8#22.8#21.8#30.485#22#21.8#
BETA=16.14#17#16.14#23.82#22#22.69#
IP = "vahan.local"
PORT = 9559


"""
detect landmark position
"""


def detectTar(ip):

    try:
        memoryProxy = ALProxy("ALMemory", ip, 9559)
        landmarkProxy = ALProxy("ALLandMarkDetection", ip, 9559)
        motionProxy = ALProxy("ALMotion", ip, 9559)
    except Exception,e:
        print "Faults in objects"
        print "ERRORS: ", e



    # Subscribe to LandmarkDetected event from ALLandMarkDetection proxy.
    landmarkProxy.subscribe("landmarkTest")

    # Wait for a mark to be detected.
    markData = memoryProxy.getData("LandmarkDetected")
    while (len(markData) == 0):
        markData = memoryProxy.getData("LandmarkDetected")
##    print "This is mark data: ", markData
    # Retrieve landmark center position in radians.
    wzCamera = markData[1][0][0][1]

    # print "wzCamera"
    # print wzCamera
    wyCamera = markData[1][0][0][2]

    # print "wyCamera"
    # print wyCamera

    # Retrieve landmark angular size in radians.
    angularSize = markData[1][0][0][3]

    # print "angularSize"
    # print angularSize

    # Compute distance to landmark.
    distanceFromCameraToLandmark = landmarkTheoreticalSize / ( 2 * math.tan( angularSize / 2))
##    print "Distance to landMark: ",distanceFromCameraToLandmark


    # Get current camera position in NAO space.
    transform = motionProxy.getTransform(currentCamera, 2, True)#"RHand",2,True)#

##    print "get current cam: ",transform
    transformList = almath.vectorFloat(transform)
##    print "and list: ", transformList
    robotToCamera = almath.Transform(transformList)
##    print "robot to cam: ", robotToCamera

    # Compute the rotation to point towards the landmark.
    cameraToLandmarkRotationTransform = almath.Transform_from3DRotation(0, wyCamera, wzCamera)
##    print "Rotation transform: ",cameraToLandmarkRotationTransform
    # Compute the translation to reach the landmark.
    cameraToLandmarkTranslationTransform = almath.Transform(distanceFromCameraToLandmark, 0, 0)

    # Combine all transformations to get the landmark position in NAO space.
    robotToLandmark = robotToCamera * cameraToLandmarkRotationTransform *cameraToLandmarkTranslationTransform

    x,y,z=robotToLandmark.r1_c4,robotToLandmark.r2_c4,robotToLandmark.r3_c4
    # print "ROBOT TO LANDMARK"
    # print robotToLandmark

    landmarkProxy.unsubscribe("landmarkTest")

    # as suggested in tutorial
    # d=math.sqrt(x**2+y**2)
    # x,y,theta=d*0.75,y,
    #theta=math.atan(y/x)

    return x,y,z




"""
    To return current configuration of legos on the gameboard along with their centers
"""

def getCurrentGameboard():
    NUM_OF_TIMES=5
    THRESHOLD=3

    #first we scan the gameboard NUM_OF_TIMES times and store shapes detected during each time:
    detected=[[],[],[],[],[],[],[],[],[]]

    for times in range(0,NUM_OF_TIMES):
        listOfShapesDetected= shapeDetectionModuleInterface.shapeDetectionMain("vahan.local", 9559)
        for shapeID in range(0,9):
            detected[times].append(listOfShapesDetected[shapeID])



    #mean coordinates
    meanOfCenters=[]

    #list of probabilities to detect a particular shape
    probList=[]

    #calculate probabilities that each figure appears on the gameboard
    for shapeID in range(0,9):
        shapeCentersListLength=0
        meanX=0
        meanY=0
        n=0
        for times in range(0,NUM_OF_TIMES):
            #only count those shapes, which are detected in single exemplars (i.e. no 2 red triangles)
            if(len(detected[times][shapeID].getCenters())==1 or len(detected[times][shapeID].getCenters())==0):
                shapeCentersListLength+=len(detected[times][shapeID].getCenters())
                if(len(detected[times][shapeID].getCenters())==1):
                    meanX+=detected[times][shapeID].getCenters()[0][0]
                    meanY+=detected[times][shapeID].getCenters()[0][1]
                    n+=1.0
            else:
                shapeCentersListLength+=0
        probList.append(shapeCentersListLength)
        if n==0:
            meanOfCenters.append((0, 0))
        else:
            meanOfCenters.append((meanX/n, meanY/n))


    #to remove noise
    for shapeID in range(0,9):
        if probList[shapeID]< THRESHOLD:
            meanOfCenters[shapeID]=(0,0)


    detectedPiecesIDs=[i for i,v in enumerate(probList) if v >= THRESHOLD]

    return (detectedPiecesIDs,meanOfCenters)



"""
    to apply math transforms
    :param: Ip address
    :param: pair of coordinates in pixels
"""

listOfPiecesLabels=['red triangle','red square','red circle',
                       'blue triangle', 'blue square', 'blue circle',
                       'yellow triangle','yellow square','yellow circle']
(detectedPiecesIDs,meanOfCenters)=getCurrentGameboard()
##for testing, this input is always asking to detect the "blue triangle"
def applyTransform(robotIP):
    PORT = 9559
    x0,y0=meanOfCenters[listOfPiecesLabels.index("blue triangle")]
    print x0,y0

    motionProxy = ALProxy("ALMotion", robotIP, PORT)
    space           = motion.FRAME_ROBOT
    useSensorValues = True
    #Vector containing the Position6D using meters and radians (x, y, z, wx, wy, wz)
    result          = motionProxy.getPosition(currentCamera, space, useSensorValues)

    h=0.175 #meters --height of the plane
    P0=[0,0,h]
    theta_c=result[4]

    X_c=result[0:3]#[result[0]-robotPosition_x0, result[1]-robotPosition_y0, result[2]]#

    y_l=math.tan(math.radians(-ALPHA))

    y_h=math.tan(math.radians(ALPHA))

    z_l=math.tan(math.radians(-BETA))

    z_h=math.tan(math.radians(BETA))



    w_y=((320.0-x0)/320.0)*y_h

    w_z=((240.0-y0)/240.0)*z_h



    w=[1,w_y,w_z]


    wx=result[3]
    wy=result[4]
    wz=result[5]

    R_x = np.matrix([[1,0, 0],[0, math.cos(wx), -math.sin(wx)], [0, math.sin(wx),math.cos(wx)]])


    R_y = np.matrix([[math.cos(-wy),0, math.sin(-wy)],[0, 1, 0], [-math.sin(-wy), 0,math.cos(-wy)]])


    R_z = np.matrix([[math.cos(wz),- math.sin(wz),0],[math.sin(wz),math.cos(wz),0],[0, 0, 1]])


    w_prime= ((w*R_y)*R_x)*R_z

    w=w_prime.tolist()[0]

    n=[0,0,1]#[-math.sin(theta_c),0,math.cos(theta_c)]


    diff=list(p-q for p,q in zip(P0,X_c))

    t= sum(p*q for p,q in zip(diff, n))/sum(p*q for p,q in zip(w, n))


    X_prime= list(p+q for p,q in zip(X_c,list(t*q for q in w)))

    X_x=X_prime[0]
    X_y=X_prime[1]
    X_z=X_prime[2]

    #X=[X_x*math.cos(-theta_c)+(-X_z*math.sin(-theta_c)),X_y, X_x*math.sin(-theta_c)+X_z*math.cos(-theta_c)]
    X=[X_x,X_y,X_z]
    # print "Position of", currentCamera, " in World is:"
    # print result
    print "vision detection"
    print X

    return X[0],X[1],X[2]



##
##applyTransform("vahan.local")

#
# #main module
if __name__ == '__main__':
    IP = "vahan.local"
    PORT = 9559

    t0 = time.time()


    listOfPiecesLabels=['red triangle','red square','red circle',
                           'blue triangle', 'blue square', 'blue circle',
                           'yellow triangle','yellow square','yellow circle']

    print "****************************************************************************"


    (detectedPiecesIDs,meanOfCenters)=getCurrentGameboard()

    name="blue triangle"
    #
    shapeidx=listOfPiecesLabels.index(name)

    X=applyTransform("vahan.local")
    print X
    print ""
    print name
    print "*"*50
    print ""
    print "Calculated distance in meters:"
    print "Calculated x " + str(X[0]) + " (in meters)"
    print "Calculated y " + str(X[1]) + " (in meters)"
    print "Calculated z " + str(X[2]) + " (in meters)"
    print ""
    print "*"*50
    print ""

    print "LANDMARK DETECTION"
    print ""
    print "Please put on the naomark"
    time.sleep(2)
    x,y,z = detectTar(IP)
    # print ""
    # print "*"*50
    # print ""
    print "Actual distance to landmark: "#, robotToLandmark
    print "Detected x " + str(x) + " (in meters)"
    print "Detected y " + str(y) + " (in meters)"
    print "Detected z " + str(z) + " (in meters)"