# -*- encoding: UTF-8 -*-

import sys
from naoqi import ALProxy
import time
import almath

def search(robotIP):
    PORT = 9559

    try:
        memoryProxy = ALProxy("ALMemory", robotIP, 9559)
        landmarkProxy = ALProxy("ALLandMarkDetection", robotIP, 9559)
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)

    motionProxy.setStiffnesses("Head", 1.0)
    
    # Set here the size of the landmark in meters.
##    landmarkTheoreticalSize = 0.0195 #in meters
    # Set here the current camera ("CameraTop" or "CameraBottom").
    currentCamera = "CameraBottom"
    # Subscribe to LandmarkDetected event from ALLandMarkDetection proxy.
    landmarkProxy.subscribe("landmarkTest")
    # Simple command for the HeadYaw joint at 10% max speed
    #yaw 119.52 to -119.52	-25.73	18.91
    
    markData = memoryProxy.getData("LandmarkDetected")
    
    names            = ["HeadYaw","HeadPitch"]
    pack=[[0,29],[-27,24],[27,24],[-43,21],[43,21],[0,29]]
    fractionMaxSpeed = 0.01
    for s in pack:
        if len(markData) !=0:
            head_angle = motionProxy.getAngles("Head", True)
##            print head_angle
            motionProxy.setAngles(names,head_angle,fractionMaxSpeed)
            break
        else:
            angles           = [i*almath.TO_RAD for i in s]
            motionProxy.setAngles(names,angles,fractionMaxSpeed)
            markData = memoryProxy.getData("LandmarkDetected")
            time.sleep(2.0)
    motionProxy.setStiffnesses("Head", 0.0)
    return markData



