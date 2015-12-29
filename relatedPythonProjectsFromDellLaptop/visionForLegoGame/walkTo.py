# -*- encoding: UTF-8 -*- 

'''Move To: Small example to make Nao Move To an Objective'''

import math
import almath as m # python's wrapping of almath
import almath
import sys
import time
from naoqi import ALProxy
import random


def StiffnessOn(proxy, value=1.0):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = value
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)


def detectTar(ip):

    try:           
        memoryProxy = ALProxy("ALMemory", ip, 9559)
        landmarkProxy = ALProxy("ALLandMarkDetection", ip, 9559)
        motionProxy = ALProxy("ALMotion", ip, 9559)
    except Exception,e:
        print "Faults in objects"
        print "ERRORS: ", e

    # Set here the size of the landmark in meters.
    landmarkTheoreticalSize = 0.01#19 #in meters; small mark=0.019,big=0.05
    # Set here the current camera ("CameraTop" or "CameraBottom").
    currentCamera = "CameraTop"

    # Subscribe to LandmarkDetected event from ALLandMarkDetection proxy.
    landmarkProxy.subscribe("landmarkTest")

    # Wait for a mark to be detected.
    markData = memoryProxy.getData("LandmarkDetected")
    while (len(markData) == 0):
        markData = memoryProxy.getData("LandmarkDetected")
##    print "This is mark data: ", markData
    # Retrieve landmark center position in radians.
    wzCamera = markData[1][0][0][1]
    wyCamera = markData[1][0][0][2]

    # Retrieve landmark angular size in radians.
    angularSize = markData[1][0][0][3]

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
    print "to landmark: ", robotToLandmark
    x,y,z=robotToLandmark.r1_c4,robotToLandmark.r2_c4,robotToLandmark.r3_c4
    print "Detected x " + str(x) + " (in meters)"
    print "Detected y " + str(y) + " (in meters)"
    print "Detected z " + str(z) + " (in meters)"
    landmarkProxy.unsubscribe("landmarkTest")
    # as suggested in tutorial
    d=math.sqrt(x**2+y**2)
    x,y,theta=d*0.75,y,math.atan(y/x)
    return x,y,theta                

def main(robotIP):
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


    # Set NAO in stiffness On
    StiffnessOn(motionProxy)

    #####################
    ## Enable arms control by move algorithm
    #####################
    motionProxy.setWalkArmsEnabled(True, True)

##  kill the walk task when the robot is lifted  
    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    #####################
    ## get robot position before move
    #####################
    initRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))
##    print "init position: ", initRobotPosition

    try:
        X,Y,Theta = detectTar(robotIP)
##        print "X,Y,Z: ",X,Y,Theta
    except Exception, e:
        print "problem with detectTar"
        print "Error is: ",e

##this block is for walking robot to Naomark using proportional control.
##    try:
##        while X>0.2:
##            print "here we go*****"
##            motionProxy.post.moveTo(X,Y,Theta)
##            time.sleep(2.0)
##            motionProxy.post.move(0.0,0.0,0.0)
##            time.sleep(2.0)
##            X,Y,Theta = detectTar(robotIP)
##        
##        motionProxy.post.move(0.0,0.0,0.0)
##        print "Target is within reach."
##    except (KeyboardInterrupt, SystemExit):
##        time.sleep(0.5)
##        postureProxy.goToPosture("Crouch",0.5)
##        time.sleep(0.5)
##        StiffnessOn(motionProxy,0.0)
##        print "User Interruption called"
##    except Exception, e:
##        print "Something happened in the while"
##        print "ERRORS: ",e

       
            

    

    #####################
    ## get robot position after move
    #####################
    endRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))
##    print "Stop here: ", endRobotPosition
    #####################
    ## compute and print the robot motion
    #####################
##    robotMove = m.pose2DInverse(initRobotPosition)*endRobotPosition
##    print "Robot Move :", robotMove
    # Set NAO in stiffness Off
    time.sleep(0.5)
    postureProxy.goToPosture("Crouch",0.5)
    time.sleep(0.5)
    StiffnessOn(motionProxy,0.0)




main("10.104.64.227")
