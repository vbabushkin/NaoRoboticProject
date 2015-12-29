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
import random

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
#h=0.221
h=0.233

def detect(robotIP,motionProxy,shape,index):

    motionProxy.setStiffnesses("Head", 1.0)
    motionProxy.angleInterpolationWithSpeed(["HeadPitch"],[0.2],0.4)

    listOfShapesDetected = shapeDetectionModuleInterface.shapeDetectionMain(robotIP, 9559)

    count = 0
    while (len(listOfShapesDetected[listOfPiecesLabels.index(shape)].getCenters()) == 0):
        print "Look up"
        motionProxy.angleInterpolationWithSpeed(["HeadPitch"],[0.2],0.4)
        listOfShapesDetected = shapeDetectionModuleInterface.shapeDetectionMain(robotIP, 9559)

        if (len(listOfShapesDetected[listOfPiecesLabels.index(shape)].getCenters()) == 0):
            print "failed to detect desired block"
            print "index = ", index
            if (count == 0):
                if (index < 4):
                    motionProxy.moveTo(0.0, 0.06, 0.0);
                else:
                    motionProxy.moveTo(0.0, -0.06, 0.0);

            elif (count == 1):
                #if (index < 4):
                    #motionProxy.angleInterpolation(["HeadYaw"],[-0.8 ],[1  ],False)
                motionProxy.moveTo(-0.03, 0.0, 0.0);
                #else:
                    #motionProxy.angleInterpolation(["HeadYaw"],[0.8 ],[1  ],False)
                #    motionProxy.moveTo(-0.03, -0.0, 0.0);
            elif (count == 2):
                motionProxy.angleInterpolation(["HeadYaw"],[0.4],[1],False)
                motionProxy.moveTo(-.04, 0.0, 0.0)# walk back
                count = -1
            else:
                print "i give up"
                break

            count += 1

            motionProxy.angleInterpolation(["HeadPitch"],[0.3],[1],False)
            listOfShapesDetected = shapeDetectionModuleInterface.shapeDetectionMain(robotIP, 9559)


    x0,y0=listOfShapesDetected[listOfPiecesLabels.index(shape)].getCenters()[0]
    result = motionProxy.getPosition(currentCamera, motion.FRAME_ROBOT, True)

    P0=[0,0,h]
    X_c=result[0:3]

    #y_l=math.tan(math.radians(-ALPHA))
    y_h=math.tan(math.radians(ALPHA))
    #z_l=math.tan(math.radians(-BETA))
    z_h=math.tan(math.radians(BETA))

    # w_y=((320.0-x0)/320.0)*y_h
    # w_z=((240.0-y0)/240.0)*z_h

    #lower resolution
    w_y=((160.0-x0)/160.0)*y_h
    w_z=((120.0-y0)/120.0)*z_h

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

    print "Target: ", X[0], ", ", X[1], ", ", X[2]

    if (X[0] < 0.0):
        print "something went terribly wrong"
        detect(robotIP,motionProxy,shape,index)

    #print "Calculated x " + str(X[0]) + " (in meters)"
    #print "Calculated y " + str(X[1]) + " (in meters)"
    #print "Calculated z " + str(X[2]) + " (in meters)"
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

        #postureProxy.goToPosture("StandInit", 0.5)
        newInitPos(motionProxy)
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

def addIt(oblocks,o):
#    print "adding ", o.obj
    added = False
    for i in range(0,len(oblocks)):
        if (oblocks[i].frame > o.frame):
#            print "by frame"
            oblocks.insert(i,o)
            added = True
            break

        if (oblocks[i].x > o.x) and (oblocks[i].frame == o.frame):
#            print "by x"
            oblocks.insert(i,o)
            added = True
            break
    if (not added):
        oblocks.insert(len(oblocks),o)
    return oblocks

def foundIn(expectedBlocks,shape):
    for block in expectedBlocks:
        if (block == shape):
            return True

    return False


def takeScan(robotIP,motionProxy,postureProxy,expectedBlocks,foundBlocks,hpitch,hyaw):
    newInitPos_sinCabeza(motionProxy)

    motionProxy.setAngles(["HeadPitch","HeadYaw"],[hpitch, hyaw],0.2)
    time.sleep(2)
    marginx = 30

    # identify blocks that are immediately recognizable
    listOfShapesDetected = shapeDetectionModuleInterface.shapeDetectionMain(robotIP, 9559)

    orderedBlocks = []
    for i in range(0,len(foundBlocks)):
        orderedBlocks.insert(i,foundBlocks[i])

    cameraAngle = 0
    if (hyaw > 0.0):
        cameraAngle = -1
    elif (hyaw < -0.0):
        cameraAngle = 1

    for i in range(0,9):
        if (len(listOfShapesDetected[i].getCenters()) > 0):

            if ((listOfShapesDetected[i].getCenters()[0][0] > marginx) and (listOfShapesDetected[i].getCenters()[0][0] < 640-marginx)):
                ya = False
                for j in range(0,len(foundBlocks)):
                    if (foundBlocks[j].obj == listOfPiecesLabels[i]):
                        ya = True
                        break

                if (not ya):
                    o = orderedList(listOfPiecesLabels[i],listOfShapesDetected[i].getCenters()[0][0],cameraAngle)
                    orderedBlocks = addIt(orderedBlocks,o)

    # verify that the identified blocks are all in expectedBlocks, otherwise we have a detection error
    errore = False
    index = -1
    for i in range(0,len(orderedBlocks)):
        if (not foundIn(expectedBlocks,orderedBlocks[i].obj)):
            index = i
            errore = True
            break

    if errore:
        print "I detected a piece I should not have detected:"

        #for blocks in orderedBlocks:
        #    print blocks.obj
        print "Detected: ", orderedBlocks[index].obj
        print "I'm going to rescan after repositioning myself"
        print "CHANGE THIS TO SEE IF WE CAN SCAN *FIRST* INSTEAD OF MOVING"

        countLeft = 0
        for blocks in orderedBlocks:
            countLeft += blocks.frame

        amounty = random.choice([0.02,0.03,0.04])
        amountx = random.choice([0.02,0.0,-0.03])
        if (countLeft < 0):
            motionProxy.moveTo(amountx, amounty, 0.0)
        else:
            motionProxy.moveTo(amountx, -amounty, 0.0)

        orderedBlocks = []#takeScan(robotIP,motionProxy,postureProxy,expectedBlocks,foundBlocks,hpitch,hyaw)

    return orderedBlocks

def compareLists(orderedBlocks,expectedBlocks):
    theMissing = []
    theMissingPositions = []


    for i in range(0,len(expectedBlocks)):
        encontrado = False
        for j in range(0,len(orderedBlocks)):
            if (orderedBlocks[j].obj == expectedBlocks[i]):
                encontrado = True
                break
        if (not encontrado):
            theMissing.append(expectedBlocks[i])
            theMissingPositions.append(i - (len(expectedBlocks)/2))

    return theMissing,theMissingPositions

def idBlocks(robotIP,motionProxy,postureProxy,expectedBlocks,sorted,mustCount):
    orderedBlocks = takeScan(robotIP,motionProxy,postureProxy,expectedBlocks,[],0.3,0.0)

    hpitch = 0.3
    hyaw = 0.4

    pitchangles = [-0.05,0.0,0.15,0.2]
    count = 2
    # figure out which way to look first
    while (len(orderedBlocks) < mustCount):#len(expectedBlocks)):
        print "lalooping: ",len(orderedBlocks),"vs ",len(expectedBlocks)

        dummy,missingSide = compareLists(orderedBlocks,expectedBlocks)

        #print missingSide

        if (missingSide[0] < 0):
            orderedBlocks = takeScan(robotIP,motionProxy,postureProxy,expectedBlocks,orderedBlocks,hpitch,hyaw)
        else:
            orderedBlocks = takeScan(robotIP,motionProxy,postureProxy,expectedBlocks,orderedBlocks,hpitch,-hyaw)

        if (len(orderedBlocks) < len(expectedBlocks)) and ((not sorted) or (len(missingSide) > 1)):
            if (missingSide[0] >= 0):
                orderedBlocks = takeScan(robotIP,motionProxy,postureProxy,expectedBlocks,orderedBlocks,hpitch,hyaw)
            else:
                orderedBlocks = takeScan(robotIP,motionProxy,postureProxy,expectedBlocks,orderedBlocks,hpitch,-hyaw)

        if (len(orderedBlocks) < mustCount):
            missing,missingPos = compareLists(orderedBlocks,expectedBlocks)
            print "I didn't find: ", missing
            print "Going to change head angle and scan again"
            hpitch = 0.3 - pitchangles[count]
            count = count + 1
            if (count > 3):
                count = 0
            hyaw = hyaw + 0.05#random.choice([-0.05,0.0,0.025,0.05,0.075,0.1])
            print "HeadPitch: ",hpitch,"; HeadYaw: ",hyaw
            orderedBlocks = takeScan(robotIP,motionProxy,postureProxy,expectedBlocks,[],hpitch,0.0)


    print "I ID'd the blocks"

    # if (len(orderedBlocks) < mustCount):
    #     # find out what is missing and the position (if sorted)
    #     missing,missingPos = compareLists(orderedBlocks,expectedBlocks)
    #     print "Pieces: ", missing
    #     print "Position: ", missingPos
    #
    #     # I need to look for more pieces.  Go left if more pieces were found glancing to the left; otherwise go right
    #     countLeft = 0
    #     for blocks in orderedBlocks:
    #         countLeft += blocks.frame
    #
    #     amounty = random.choice([0.02,0.03,0.04])
    #     amountx = random.choice([0.02,0.0,-0.02])
    #     if (countLeft < 0):
    #         motionProxy.moveTo(amountx, amounty, 0.0)
    #     else:
    #         motionProxy.moveTo(amountx, -amounty, 0.0)
    #
    #     orderedBlocks = idBlocks(robotIP,motionProxy,postureProxy,expectedBlocks,sorted,mustCount)


    return orderedBlocks


def detectOpponentsMove(robotIP,motionProxy,postureProxy,currentBlocks):
    expectedBlocks = []
    for i in range(0,len(currentBlocks)):
        expectedBlocks.append(currentBlocks[i].obj)

    while (True):
        print "Looping"
        newBlocks = idBlocks(robotIP,motionProxy,postureProxy,expectedBlocks,True,len(currentBlocks)-1)
        print "Done with idBlocks"

        if (len(newBlocks) == (len(expectedBlocks)-1)):
            taken,side = compareLists(newBlocks,expectedBlocks)
            print "He took the ", taken[0]
            return taken[0]
        else:
            print "Did find all: ", len(newBlocks)
            print "remaining blocks: "
            for i in range(0,len(newBlocks)):
                #currentBlocks2[i].printIt()
                sys.stdout.write(newBlocks[i].obj)
                sys.stdout.write(', ')
            print ""



def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)


def initCuerpo_fast(motionProxy):
    jnts = ["LKneePitch","RKneePitch","LAnklePitch","RAnklePitch","LAnkleRoll","RAnkleRoll","RHipRoll","LHipRoll","RHipPitch","LHipPitch","RHipYawPitch","LHipYawPitch","HeadPitch","HeadYaw"]
    angls = [0.7,0.7,-0.35,-0.35,0.0,0.0,0.0,0.0,-0.45,-0.45,0.0,0.0,0.0,0.0]
    motionProxy.angleInterpolationWithSpeed(jnts,angls,0.2)

def newInitPos_fast(motionProxy):
    StiffnessOn(motionProxy)
    initCuerpo_fast(motionProxy)

    jnts = ["RShoulderPitch","RShoulderRoll","RElbowRoll","RElbowYaw","LShoulderPitch","LShoulderRoll","LElbowRoll","LElbowYaw","LWristYaw","RWristYaw"]
    angls = [1.5,-0.3,-0.3,1.2,1.5,0.3,-0.3,-1.2,0.0,0.0]
    motionProxy.angleInterpolationWithSpeed(jnts,angls,0.3)


def initCuerpo(motionProxy):
    jnts = ["LKneePitch","RKneePitch","LAnklePitch","RAnklePitch","LAnkleRoll","RAnkleRoll","RHipRoll","LHipRoll","RHipPitch","LHipPitch","RHipYawPitch","LHipYawPitch","HeadPitch","HeadYaw"]
    angls = [0.7,0.7,-0.35,-0.35,0.0,0.0,0.0,0.0,-0.45,-0.45,0.0,0.0,0.0,0.0]
    motionProxy.angleInterpolationWithSpeed(jnts,angls,0.05)

def newInitPos(motionProxy):
    StiffnessOn(motionProxy)
    initCuerpo(motionProxy)

    jnts = ["RShoulderPitch","RShoulderRoll","RElbowRoll","RElbowYaw","LShoulderPitch","LShoulderRoll","LElbowRoll","LElbowYaw","LWristYaw","RWristYaw"]
    angls = [1.5,-0.3,-0.3,1.2,1.5,0.3,-0.3,-1.2,0.0,0.0]
    motionProxy.angleInterpolationWithSpeed(jnts,angls,0.3)

    # jnts = ["LAnklePitch","RAnklePitch","LAnkleRoll","RAnkleRoll","RHipRoll","LHipRoll","RHipPitch","LHipPitch","RShoulderPitch","RShoulderRoll","RElbowRoll","RElbowYaw","LShoulderPitch","LShoulderRoll","LElbowRoll","LElbowYaw","LWristYaw","RWristYaw"]
    # angls = [-0.35,-0.35,0.0,0.0,0.0,0.0,-0.45,-0.45,1.5,-0.3,-0.3,1.2,1.5,0.3,-0.3,-1.2,0.0,0.0]
    # motionProxy.angleInterpolationWithSpeed(jnts,angls,0.05)

def initCuerpo_sinCabeza(motionProxy):
    jnts = ["LKneePitch","RKneePitch","LAnklePitch","RAnklePitch","LAnkleRoll","RAnkleRoll","RHipRoll","LHipRoll","RHipPitch","LHipPitch","RHipYawPitch","LHipYawPitch"]
    angls = [0.7,0.7,-0.35,-0.35,0.0,0.0,0.0,0.0,-0.45,-0.45,0.0,0.0]
    motionProxy.angleInterpolationWithSpeed(jnts,angls,0.05)

def newInitPos_sinCabeza(motionProxy):

    StiffnessOn(motionProxy)
    initCuerpo_sinCabeza(motionProxy)

    jnts = ["RShoulderPitch","RShoulderRoll","RElbowRoll","RElbowYaw","LShoulderPitch","LShoulderRoll","LElbowRoll","LElbowYaw","LWristYaw","RWristYaw"]
    angls = [1.5,-0.3,-0.3,1.2,1.5,0.3,-0.3,-1.2,0.0,0.0]
    motionProxy.angleInterpolationWithSpeed(jnts,angls,0.3)



