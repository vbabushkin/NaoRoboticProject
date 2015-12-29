__author__ = 'vahan'

import sys
from naoqi import ALProxy
import motion
import math
import almath
import pickle
import numpy as np
import time
import shapeDetectionMain

# Set here the current camera ("CameraTop" or "CameraBottom").
currentCamera            = "CameraBottom"

# Set here the size of the landmark in meters.
landmarkTheoreticalSize = 0.0195



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



def main(robotIP):
    PORT = 9559
    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)

    space           = motion.FRAME_ROBOT
    useSensorValues = True
    #Vector containing the Position6D using meters and radians (x, y, z, wx, wy, wz)
    result          = motionProxy.getPosition(currentCamera, space, useSensorValues)

    print "Camera position: FRAME_ROBOT"
    print result


    x,y,z = detectTar(robotIP)
    print ""
    print "*"*50
    print ""
    print "Actual distance to landmark: "#, robotToLandmark
    print "Detected x " + str(x) + " (in meters)"
    print "Detected y " + str(y) + " (in meters)"
    print "Detected z " + str(z) + " (in meters)"

    # print ""
    # print "*"*50
    # print ""

    print math.atan((0.091/2)/(0.179-result[0]))
    print math.atan((0.121/2)/(0.179-result[0]))
    StiffnessOff(motionProxy)


def StiffnessOn(proxy):
  #We use the "Body" name to signify the collection of all joints
  pNames = "Body"
  pStiffnessLists = 1.0
  pTimeLists = 1.0
  proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def StiffnessOff(proxy):
  #We use the "Body" name to signify the collection of all joints
  pNames = "Body"
  pStiffnessLists = 0.0
  pTimeLists = 1.0
  proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)



#for loading dictionary of Shape objects
def load_obj(name ):
    with open(name + '.pkl', 'r') as f:
        return pickle.load(f)

if __name__ == "__main__":
    robotIp = "10.104.67.182"

    if len(sys.argv) <= 1:
        print "Usage python almotion_advancedcreaterotation.py robotIP (optional default: 127.0.0.1)"
    else:
        robotIp = sys.argv[1]

    main(robotIp)