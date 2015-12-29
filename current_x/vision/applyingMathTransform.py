__author__ = 'vahan'

import cv2
import shapeDetectionModuleInterface
import shapeDetectionModule
import time
import random
from naoqi import ALProxy
import motion
import math
import numpy as np


# Set here the current camera ("CameraTop" or "CameraBottom").
currentCamera            = "CameraBottom"

# Set here the size of the landmark in meters.
landmarkTheoreticalSize = 0.0195
ALPHA=21.8#22.8#21.8#30.485#22#21.8#
BETA=16.14#17#16.14#23.82#22#22.69#
IP = "vahan.local"__author__ = 'vahan'

import cv2
import shapeDetectionModuleInterface
import shapeDetectionModule
import time
import random
from naoqi import ALProxy
import motion
import math
import numpy as np


# Set here the current camera ("CameraTop" or "CameraBottom").
currentCamera            = "CameraBottom"

# Set here the size of the landmark in meters.
landmarkTheoreticalSize = 0.0195
ALPHA=21.8#22.8#21.8#30.485#22#21.8#
BETA=16.14#17#16.14#23.82#22#22.69#
IP = "vahan.local"
PORT = 9559

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
    To select a random shape on the gameboard
    :param detectedPiecesIDs: IDs of shapes currently on the gameboard
"""
def selectShapeRandomly(detectedPiecesIDs):
    if len(detectedPiecesIDs)!=0:
        return random.choice(detectedPiecesIDs)
    else:
        return None

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

PORT = 9559

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
    To select a random shape on the gameboard
    :param detectedPiecesIDs: IDs of shapes currently on the gameboard
"""
def selectShapeRandomly(detectedPiecesIDs):
    if len(detectedPiecesIDs)!=0:
        return random.choice(detectedPiecesIDs)
    else:
        return None

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
