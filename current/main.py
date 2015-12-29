# -*- encoding: UTF-8 -*- 

''' Whole Body Motion: Left or Right Arm position control '''

import sys
import motion
import time
import almath
import random
from naoqi import ALProxy
from vision.headPositionNaoSpace import *
##from speaker import speak
from mover import move
from grabber import grab


def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

##def locateAndPosition(robotIP,motionProxy,postureProxy,shape):
##    x,y,z=detect(robotIP,motionProxy,postureProxy,shape)
####    print "vision by art:"
####    print x,y,z
##
##    while (abs(y) < 0.02):
##        if (y < 0):
##            motionProxy.moveTo(0.0, 0.03, 0.0)# walk left
##        else:
##            motionProxy.moveTo(0.0, -0.03, 0.0)# walk right
##            
##        postureProxy.goToPosture("StandInit", 0.5)
##        x,y,z=detect(robotIP,motionProxy,postureProxy,shape)
##
##    while (abs(y) > 0.07):
##        my = abs(y) - 0.06
##        
##        if (y > 0):
##            motionProxy.moveTo(0.0, my, 0.0)# walk left
##        else:
##            motionProxy.moveTo(0.0, -my, 0.0)# walk right
##            
##        postureProxy.goToPosture("StandInit", 0.5)
##        x,y,z=detect(robotIP,motionProxy,postureProxy,shape)
##
##    while (x < 0.19):
##        mx = x - 0.20
##        
##        motionProxy.moveTo(mx, 0.0, 0.0)# walk back
##            
##        postureProxy.goToPosture("StandInit", 0.5)
##        x,y,z=detect(robotIP,motionProxy,postureProxy,shape)
##        print "vision by art:"
##        print x,y,z
##        
##    while (x > 0.215):
##        mx = x - 0.205
##        motionProxy.moveTo(mx, 0.0, 0.0)# walk forward
##            
##        postureProxy.goToPosture("StandInit", 0.5)
##        x,y,z=detect(robotIP,motionProxy,postureProxy,shape)
##        print "vision by art:"
##        print x,y,z
##    
##    return x,y,z

def locateAndPosition(robotIP,motionProxy,postureProxy,shape):
    x,y,z=detect(robotIP,motionProxy,postureProxy,shape)
##    print "vision by art:"
##    print x,y,z

##    2 < abs(y) 7
##    0.19 < x < .215

    while (abs(y) < 0.02) or (abs(y) > 0.07) or (x < 0.19) or (x > 0.215):
        my = 0.0
        mx = 0.0
        
        if (abs(y) < 0.02):
            if (y < 0):
                my = 0.03
            else:
                my = -0.03
        elif (abs(y) > 0.07):
            my = abs(y) - 0.06
            if (y < 0):
                my = -my

        if (x < 0.19):
            mx = x - 0.20
        elif (x > 0.215):
            mx = x - 0.205

        motionProxy.moveTo(mx, my, 0.0)
        
        postureProxy.goToPosture("StandInit", 0.5)
        x,y,z=detect(robotIP,motionProxy,postureProxy,shape)
    
    return x,y,z


def pickUpObject(robotIP,motionProxy,postureProxy,shape):
    StiffnessOn(motionProxy)

    postureProxy.goToPosture("StandInit", 0.5)

    rx_calib = -0.01
    ry_calib = -0.005
    lx_calib = -0.01
    ly_calib = -0.015
    
    x,y,z = locateAndPosition(robotIP,motionProxy,postureProxy,shape)

    if y>0.0:
        effectorName="LArm"
        effectorHand="LHand"
        shoulderPitch="LShoulderPitch"

        motionProxy.angleInterpolationWithSpeed("RElbowRoll",0.5,0.4)
    else:
        effectorName="RArm"
        effectorHand="RHand"
        shoulderPitch="RShoulderPitch"

        motionProxy.angleInterpolationWithSpeed("LElbowRoll",0.5,0.4)
    
    motionProxy.wbEnableEffectorControl(effectorName, True)

    if (effectorName == "LArm"):
        move(motionProxy,postureProxy,effectorName,[x+lx_calib,y+ly_calib,z+0.06])
    else:
        move(motionProxy,postureProxy,effectorName,[x+rx_calib,y+ry_calib,z+0.06])

    time.sleep(1)

    if effectorName =="RArm":
        motionProxy.angleInterpolationWithSpeed("RWristYaw",-1.3,0.4)
    else:
        motionProxy.angleInterpolationWithSpeed("LWristYaw",1.3,0.4)

    if effectorName == "LArm":
        motionProxy.openHand("LHand")
        move(motionProxy,postureProxy,effectorName,[x+lx_calib,y+ly_calib,z])
        motionProxy.closeHand("LHand")
    else:
        motionProxy.openHand("RHand")
        move(motionProxy,postureProxy,effectorName,[x+rx_calib,y+ry_calib,z])
        motionProxy.closeHand("RHand")
    
    move(motionProxy,postureProxy,effectorName,[x,y,z+0.09])
    time.sleep(1)
    motionProxy.wbEnableEffectorControl(effectorName, False)

    if effectorName == "RArm":
        motionProxy.angleInterpolationWithSpeed("RElbowYaw",2.5,0.2)
    else:
        motionProxy.angleInterpolationWithSpeed("LElbowYaw",-2.5,0.2)
    
    postureProxy.goToPosture("StandInit", 0.5)
    if effectorName == "RArm":
        motionProxy.angleInterpolationWithSpeed("RWristYaw",-1.3,0.4)
        motionProxy.openHand("RHand")
    else:
        motionProxy.angleInterpolationWithSpeed("LWristYaw",1.3,0.4)
        motionProxy.openHand("LHand")


def removeBlock(blocks,shape):
    nblocks = []

    for i in range(0,len(blocks)):
        if (blocks[i] != shape):
            nblocks.append(blocks[i])

    return nblocks


def compareList(blocks,nblocks):
    for i in range(0,len(blocks)):
        taken = True
        for j in range(0,len(nblocks)):
            if (blocks[i] == nblocks[j]):
                taken = False

        if (taken):
            return blocks[i]

    print "this is an error"
    
    return -1

def playRound(robotIP,motionProxy,postureProxy):
    myBlocks = []
    hisBlocks = []
    expected = 9


    #identify available blocks
    StiffnessOn(motionProxy)
    postureProxy.goToPosture("StandInit", 0.5)        
    blocks=identifyAvailableBlocks(robotIP,motionProxy,postureProxy,expected,myBlocks,hisBlocks,True)

    count = 0
    while count < 3:
##        if (count > 0):
##            blocks = newBlocks
        
        # select a block
        print "\nRandomly select a block from this set:\n",blocks
        shape = random.choice(blocks)
        print shape
        myBlocks.append(shape)

        blocks = removeBlock(blocks,shape)
        
##        blocks = list(set(blocks) - set(shape))

        print "Shapes that remain after my pick:\n",blocks

        # pick up the block
        pickUpObject(robotIP,motionProxy,postureProxy,shape)
        expected -= 1

        # wait for the other guy to pick one up (detect which block is gone)
##        print "\r\n\r\nTrying to detect the other guys move\r\n\r\n"
        numBlocks = expected
        while (numBlocks == expected):
##            print "scanning again"
            postureProxy.goToPosture("StandInit", 0.5)
            time.sleep(1)
            newBlocks = identifyAvailableBlocks(robotIP,motionProxy,postureProxy,expected,myBlocks,hisBlocks,False)
            numBlocks = len(newBlocks)            
            
##            print numBlocks," vs. ",expected

        took = compareList(blocks,newBlocks)
        print "he took: ",took
        blocks = removeBlock(blocks,took)
        
        hisBlocks.append(took)

        print "there are ",numBlocks," left"
        print blocks

        expected -= 1

        count += 1

    print "my blocks: ",myBlocks
    print "his blocks: ",hisBlocks


def main(robotIP,motionProxy,postureProxy):
    ''' Example of a whole body Left or Right Arm position control
        Warning: Needs a PoseInit before executing
                 Whole body balancer must be inactivated at the end of the script
    '''

##    x,y,z=detect(robotIP,motionProxy,postureProxy,"red square")
    
##    pickUpObject(robotIP,motionProxy,postureProxy,"red square")

##    playRound(robotIP,motionProxy,postureProxy)

    idBlocks(robotIP,motionProxy,postureProxy,9)
    
    
if __name__ == '__main__':
  
    robotIP="10.104.67.181"
    try:
        motionProxy = ALProxy("ALMotion", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e

    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e    

    main(robotIP,motionProxy,postureProxy)

##main(robotIP,motionProxy,postureProxy)
##motionProxy = ALProxy("ALMotion", "10.104.67.181", 9559)
