import sys
import time
import math

from naoqi import ALProxy

import almath
def StiffnessOn(proxy,value=1.0):
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
    try:
        postureProxy = ALProxy("ALRobotPosture", ip, 9559)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e
    try:
        motionProxy = ALProxy("ALMotion", ip, 9559)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e
##    # Set NAO in Stiffness On
##    StiffnessOn(motionProxy)
##
##    # Send NAO to Pose Init
##    postureProxy.goToPosture("StandInit", 0.5)
##    
    # Set here the size of the landmark in meters.
    landmarkTheoreticalSize = 0.020 #in meters
    # Set here the current camera ("CameraTop" or "CameraBottom").
    currentCamera = "CameraBottom"

    # Subscribe to LandmarkDetected event from ALLandMarkDetection proxy.
    landmarkProxy.subscribe("landmarkTest")

    # Wait for a mark to be detected.
    markData = memoryProxy.getData("LandmarkDetected")
    while (len(markData) == 0):
        markData = memoryProxy.getData("LandmarkDetected")
##    print "markdata: "
##    for i in markData:
##        print i
    # Retrieve landmark center position in radians.
    wzCamera = markData[1][0][0][1]
    wyCamera = markData[1][0][0][2]

    # Retrieve landmark angular size in radians.
    angularSize = markData[1][0][0][3]

    # Compute distance to landmark.
    distanceFromCameraToLandmark = landmarkTheoreticalSize / ( 2 * math.tan( angularSize / 2))

    

    # Get current camera position in NAO space.
    # print 4X4 matrix values
    # after getTrasform, the value has to converted to vectorFloat
    transform = motionProxy.getTransform(currentCamera, 2, True)
##    print "the transform: ",transform
##    for i in range(len(transform)):
##        if i+4>16:
##            break
##        temp=[transform[idx] for idx in range(i,i+4)]
##        print "-"*len(str(temp))
##        print temp
##        i=i+4
    transformList = almath.vectorFloat(transform)
##    print transformList
    robotToCamera = almath.Transform(transformList)
    
##    print "Robot 2 camera: ",robotToCamera
    # Compute the rotation to point towards the landmark.
    cameraToLandmarkRotationTransform = almath.Transform_from3DRotation(0, wyCamera, wzCamera)
    print cameraToLandmarkRotationTransform
    print "--"
##    print type(cameraToLandmarkRotationTransform)
    # Compute the translation to reach the landmark.
    cameraToLandmarkTranslationTransform = almath.Transform(distanceFromCameraToLandmark, 0, 0)
    print "translation: ", cameraToLandmarkTranslationTransform
    
    # Combine all transformations to get the landmark position in NAO space.
    robotToLandmark = robotToCamera * cameraToLandmarkRotationTransform *cameraToLandmarkTranslationTransform
    x,y,z=robotToLandmark.r1_c4,robotToLandmark.r2_c4,robotToLandmark.r3_c4
##    print "Robot2Landmark: ",x,y,z
    # get position of the effector
    #
    arm_transform = motionProxy.getTransform("LArm",2,True)
    robot2Arm = almath.Transform(almath.vectorFloat(arm_transform))
#    print "robot LArm: ",robot2Arm
    #get naomark position in LArm coordinates
    print "-"*15

    print "lArmToNaomark: arm movement"
    print x-robot2Arm.r1_c4,y-robot2Arm.r2_c4,z-robot2Arm.r3_c4
    # some = robot2Arm*[[x][y][z]]
    # print "some",some


    print "Detected x " + str(x) + " (in meters)"
    print "Detected y " + str(y) + " (in meters)"
    print "Detected z " + str(z) + " (in meters)"
    landmarkProxy.unsubscribe("landmarkTest")
##    return x,y,z
detectTar("10.104.4.40")
