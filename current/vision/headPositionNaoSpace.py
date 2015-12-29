# -*- encoding: UTF-8 -*-

import sys
from naoqi import ALProxy
import motion
import math
import almath
import pickle
import numpy as np
import time
import shapeDetectionModuleInterface

# Set here the current camera ("CameraTop" or "CameraBottom").
currentCamera            = "CameraBottom"

# Set here the size of the landmark in meters.
landmarkTheoreticalSize = 0.02

ALPHA=21.8#22.8                          #21.8#30.485#22#21.8#
BETA=16.14#17.0                           #16.14#23.82#22#22.69#
##SHAPE_NAME="red square"

listOfPiecesLabels=['red triangle','red square','red circle',
                   'blue triangle', 'blue square', 'blue circle',
                   'yellow triangle','yellow square','yellow circle']


##h=0.212# #meters --height of the plane
##h=0.189
h=0.221

def detect(robotIP,motionProxy,postureProxy,shape):

    motionProxy.setStiffnesses("Head", 1.0)

    motionProxy.angleInterpolation(
         ["HeadPitch"],
         [0.3 ],
         [1  ],
         False
    )

    useSensors = False
    robotPosition     = almath.Pose2D(motionProxy.getRobotPosition(useSensors))
    nextRobotPosition = almath.Pose2D(motionProxy.getNextRobotPosition())

    position=robotPosition.toVector()

    robotPosition_x0=position[0]
    robotPosition_y0=position[1]
    robotPosition_theta0=position[2]

    space           = motion.FRAME_ROBOT
    useSensorValues = True
    result          = motionProxy.getPosition(currentCamera, space, useSensorValues)

##    listOfPiecesLabels=['red triangle','red square','red circle',
##                       'blue triangle', 'blue square', 'blue circle',
##                       'yellow triangle','yellow square','yellow circle']

##    motionProxy.angleInterpolationWithSpeed("RElbowRoll",0.5,0.4)
##    motionProxy.angleInterpolationWithSpeed("LElbowRoll",0.5,0.4)

    listOfShapesDetected = shapeDetectionModuleInterface.shapeDetectionMain(robotIP, 9559)

    count = 0
    while (len(listOfShapesDetected[listOfPiecesLabels.index(shape)].getCenters()) == 0):
        if (count == 0):
            print "head to left"
            motionProxy.angleInterpolation(
                 ["HeadYaw"],
                 [0.4 ],
                 [1  ],
                 False
            )
            
        elif (count == 1):
            print "head to right"
            motionProxy.angleInterpolation(
                 ["HeadYaw"],
                 [-0.8 ],
                 [1  ],
                 False
            )
        elif (count == 2):
            print "back up"
            motionProxy.angleInterpolation(
                 ["HeadYaw"],
                 [0.4 ],
                 [1  ],
                 False
            )
            motionProxy.moveTo(-.04, 0.0, 0.0)# walk back
            count = -1
        else:
            print "i give up"
            break

        count += 1

        listOfShapesDetected = shapeDetectionModuleInterface.shapeDetectionMain(robotIP, 9559)

    useSensors = False
    robotPosition     = almath.Pose2D(motionProxy.getRobotPosition(useSensors))
    nextRobotPosition = almath.Pose2D(motionProxy.getNextRobotPosition())

    position=robotPosition.toVector()

    robotPosition_x0=position[0]
    robotPosition_y0=position[1]
    robotPosition_theta0=position[2]

    space           = motion.FRAME_ROBOT
    useSensorValues = True
    result          = motionProxy.getPosition(currentCamera, space, useSensorValues)

    x0,y0=listOfShapesDetected[listOfPiecesLabels.index(shape)].getCenters()[0]

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
    wx=-result[3]#changed to minus
    wy=result[4]
    wz=result[5]

    R_x = np.matrix([[1,0, 0],[0, math.cos(wx), -math.sin(wx)], [0, math.sin(wx),math.cos(wx)]])
    R_y = np.matrix([[math.cos(wy),0, math.sin(wy)],[0, 1, 0], [-math.sin(wy), 0,math.cos(wy)]])
    R_z = np.matrix([[math.cos(wz),-math.sin(wz),0],[math.sin(wz),math.cos(wz),0],[0, 0, 1]])

    wtrash = np.matrix(w)
    primero = R_y * wtrash.reshape((3,1))
    segundo = R_x * primero
    tercero = R_z * segundo

    w_prime = tercero.reshape((1,3))
    w=w_prime.tolist()[0]

    n=[0,0,1]#[-math.sin(theta_c),0,math.cos(theta_c)]

    diff=list(p-q for p,q in zip(P0,X_c))

    t= sum(p*q for p,q in zip(diff, n))/sum(p*q for p,q in zip(w, n))
    X_prime= list(p+q for p,q in zip(X_c,list(t*q for q in w)))

    X_x=X_prime[0]
    X_y=X_prime[1]
    X_z=X_prime[2]

    
    X=[X_x,X_y,X_z]
    
    print "Calculated x " + str(X[0]) + " (in meters)"
    print "Calculated y " + str(X[1]) + " (in meters)"
    print "Calculated z " + str(X[2]) + " (in meters)"
    return tuple(X)


def identifyAvailableBlocks(robotIP,motionProxy,postureProxy,expectedBlockCount,myBlocks,hisBlocks,Search):
    motionProxy.setStiffnesses("Head", 1.0)

    motionProxy.angleInterpolation(
         ["HeadPitch"],
         [0.3 ],
         [1  ],
         False
    )

    motionProxy.angleInterpolationWithSpeed("RElbowRoll",0.5,0.4)
    motionProxy.angleInterpolationWithSpeed("LElbowRoll",0.5,0.4)

##    listOfPiecesLabels=['red triangle','red square','red circle',
##                       'blue triangle', 'blue square', 'blue circle',
##                       'yellow triangle','yellow square','yellow circle']

    listOfShapesDetected = shapeDetectionModuleInterface.shapeDetectionMain(robotIP, 9559)

    blocks = []
    for i in range(0,9):
        if (len(listOfShapesDetected[i].getCenters()) > 0):
            blocks.append(listOfPiecesLabels[i])

    if (len(blocks) == expectedBlockCount):
        print "we did it"
    else:
        count = 0
        while (len(blocks) != expectedBlockCount):
            print "we failed: ",len(blocks)
##            print blocks
            
            if (count == 0):
                motionProxy.angleInterpolation(
                     ["HeadYaw"],
                     [0.4 ],
                     [1  ],
                     False
                )
                
            elif (count == 1):
                motionProxy.angleInterpolation(
                     ["HeadYaw"],
                     [-0.8 ],
                     [1  ],
                     False
                )
            elif (count == 2):
                motionProxy.angleInterpolation(
                     ["HeadYaw"],
                     [0.4 ],
                     [1  ],
                     False
                )
                if (Search):
                    motionProxy.moveTo(-.03, 0.0, 0.0)# walk back
                    count = -1
                else:
                    break
            else:
##                print "i give up"
                break

            count += 1

            listOfShapesDetected = shapeDetectionModuleInterface.shapeDetectionMain(robotIP, 9559)
            cur = len(blocks)
            for i in range(0,9):
                if (len(listOfShapesDetected[i].getCenters()) > 0):
                    found = False
                    for j in range(0,cur):
                        if (listOfPiecesLabels[i] == blocks[j]):
                            found = True
                            break

                    if (not found):
                        blocks.append(listOfPiecesLabels[i])

    print "\n\nmyBlocks: ",myBlocks
    print "hisBlocks: ",hisBlocks
    print "remaining blocks: ",blocks
    print "\n"

    errore = False
    for i in range(0,len(blocks)):
        for j in range(0,len(myBlocks)):
            if (blocks[i] == myBlocks[j]):
                errore = True
                break
        for j in range(0,len(hisBlocks)):
            if (blocks[i] == hisBlocks[j]):
                errore = True
                break

        if (errore):
            break

    if errore:
        print "caught an error; going to retry"
        motionProxy.angleInterpolation(
             ["HeadPitch"],
             [-0.3 ],
             [1  ],
             False
        )

        postureProxy.goToPosture("StandInit", 0.5)
        blocks = identifyAvailableBlocks(robotIP,motionProxy,postureProxy,expectedBlockCount,myBlocks,hisBlocks,Search)


##    print blocks

    return blocks


class orderedList:
    def __init__(self,obj,x,frm):
        self.obj = obj
        self.x = x
        self.frame = frm

    def printIt(self):
        print self.obj, ", ", self.x, ", ", self.frame

def idBlocks(robotIP,motionProxy,postureProxy,eBlocks):
    
    # look straight ahead and down .3 radians (from standard position)
    postureProxy.goToPosture("StandInit", 0.5)
    
    motionProxy.angleInterpolation(
         ["HeadPitch"],
         [0.3 ],
         [1  ],
         False
    )

    # identify blocks that are immediately recognizable
    listOfShapesDetected = shapeDetectionModuleInterface.shapeDetectionMain(robotIP, 9559)

    orderedBlocks = []
    
    for i in range(0,9):
        if (len(listOfShapesDetected[i].getCenters()) > 0):
            o = orderedList(listOfPiecesLabels[i],listOfShapesDetected[i].getCenters()[0][0],0)
            o.printIt()
##            print listOfPiecesLabels[i], ": ", listOfShapesDetected[i].getCenters()
##            addIt(orderedBlocks,listOfPiecesLabels[i], listOfShapesDetected[i].getCenters()[0])

    




