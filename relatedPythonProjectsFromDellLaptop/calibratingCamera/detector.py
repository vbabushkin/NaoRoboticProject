import sys
import motion
import time
import math
import almath
from naoqi import ALProxy
import numpy as np
import shapeDetectionMain
import pickle
from timer import timeout
from searcher import search
# Set here the current camera ("CameraTop" or "CameraBottom").
currentCamera            = "CameraBottom"

# Set here the size of the landmark in meters.
landmarkTheoreticalSize = 0.0195
ALPHA=21.8#22.8#21.8#30.485#22#21.8#
BETA=16.14#17#16.14#23.82#22#22.69#
def detect(robotIP):

#     try:
#         memoryProxy = ALProxy("ALMemory", ip, 9559)
#         landmarkProxy = ALProxy("ALLandMarkDetection", ip, 9559)
#         motionProxy = ALProxy("ALMotion", ip, 9559)
#     except Exception,e:
#         print "Faults in objects"
#         print "ERRORS: ", e
#
#     # Set here the size of the landmark in meters.
#     landmarkTheoreticalSize = 0.032 #in meters
#     # Set here the current camera ("CameraTop" or "CameraBottom").
#     currentCamera = "CameraBottom"
#     # Subscribe to LandmarkDetected event from ALLandMarkDetection proxy.
#     landmarkProxy.subscribe("landmarkTest")
#
#     markData = memoryProxy.getData("LandmarkDetected")
#     # Wait for a mark to be detected.
#     @timeout(6)
#     def find_mark(markData):
#         while (len(markData) == 0):
#             markData = memoryProxy.getData("LandmarkDetected")
#         return markData
#     try:
#         markData= find_mark(markData)
#     except Exception, e:
#         print "time out, head's gonna move"
#         result=search(ip)
#         if len(result)==0:
#             print "timeout completely"
#             sys.exit(1)
#         else:
#             markData=result
#             print "just found it"
#
#
#     motionProxy.setStiffnesses("Head", 1.0)
#     # Retrieve landmark center position in radians.
#     wzCamera = markData[1][0][0][1]
#     wyCamera = markData[1][0][0][2]
#
#     # Retrieve landmark angular size in radians.
#     angularSize = markData[1][0][0][3]
#     space=motion.FRAME_ROBOT
#
#     # Compute distance to landmark.
#     distanceFromCameraToLandmark = landmarkTheoreticalSize / ( 2 * math.tan( angularSize / 2))
# ##    print "distance to landmark: ",distanceFromCameraToLandmark
#
#
#     # Get current camera position in NAO space.
#     transform = motionProxy.getTransform(currentCamera, space, True)
#     transformList = almath.vectorFloat(transform)
#     robotToCamera = almath.Transform(transformList)
#
#     # Compute the rotation to point towards the landmark.
#     cameraToLandmarkRotationTransform = almath.Transform_from3DRotation(0, wyCamera, wzCamera)
#
#     # Compute the translation to reach the landmark.
#     cameraToLandmarkTranslationTransform = almath.Transform(distanceFromCameraToLandmark, 0, 0)
#
#     # Combine all transformations to get the landmark position in NAO space.
#     robotToLandmark = robotToCamera * cameraToLandmarkRotationTransform *cameraToLandmarkTranslationTransform
#     print robotToLandmark
#     x,y,z=robotToLandmark.r1_c4,robotToLandmark.r2_c4,robotToLandmark.r3_c4
#     print "Mark position: ", x,y,z
#
#     landmarkProxy.unsubscribe("landmarkTest")
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
        postureProxy = ALProxy("ALRobotPosture", robotIP, 9559)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)
    # postureProxy.goToPosture("Crouch", 0.5)


    # Set NAO in Stiffness On
    StiffnessOn(motionProxy)

    # Send NAO to Pose Init
    postureProxy.goToPosture("Crouch", 0.5)
    motionProxy.setStiffnesses("Head", 1.0)

    motionProxy.post.angleInterpolation(
        ["HeadPitch"],
        [0.2 ],
        [1  ],
        False
    )


    time.sleep(2)
    # Example showing how to get the position of the top camera

    useSensors = False
    robotPosition     = almath.Pose2D(motionProxy.getRobotPosition(useSensors))
    nextRobotPosition = almath.Pose2D(motionProxy.getNextRobotPosition())

    print "ROBOT POSITION IS:"
    print robotPosition
    position=robotPosition.toVector()

    robotPosition_x0=position[0]
    robotPosition_y0=position[1]
    robotPosition_theta0=position[2]
    print "robotPosition_x0"
    print robotPosition_x0
    print "robotPosition_y0"
    print robotPosition_y0
    print "robotPosition_theta0"
    print robotPosition_theta0

    # print "ROBOT NEXT POSITION IS:"
    # print nextRobotPosition

    #detect shape and store its center in dictOfCenters
    shapeDetectionMain.mainModule(robotIP, PORT)


    space           = motion.FRAME_ROBOT
    useSensorValues = True
    #Vector containing the Position6D using meters and radians (x, y, z, wx, wy, wz)
    result          = motionProxy.getPosition(currentCamera, space, useSensorValues)

    print "Camera position: FRAME_ROBOT"
    print result

    #Coordinates of center in pixels
    dict = load_obj("dictOfCenters")
    x0= dict["blue"]["square"][0][0]
    y0= dict["blue"]["square"][0][1]

    # x0= dict["blue"]["circle"][0][0]
    # y0= dict["blue"]["circle"][0][1]



    h=0.13 #meters --height of the plane
    P0=[0,0,h]
    theta_c=result[4]
    print "THETA:"+ str(theta_c)
    X_c=result[0:3]#[result[0]-robotPosition_x0, result[1]-robotPosition_y0, result[2]]#
    print "X_c:"+ str(X_c)



    y_l=math.tan(math.radians(-ALPHA))
    print "y_l:"+ str(y_l)
    y_h=math.tan(math.radians(ALPHA))
    print "y_h:"+ str(y_h)
    z_l=math.tan(math.radians(-BETA))
    print "z_l:"+ str(z_l)
    z_h=math.tan(math.radians(BETA))
    print "z_h:"+ str(z_h)

    print (x0,y0)
    w_y=((320.0-x0)/320.0)*y_h
    print "w_y:"+ str(w_y)
    w_z=((240.0-y0)/240.0)*z_h
    print "w_z:"+ str(w_z)

    #coefficient=0.0573268048465
    # print (x0,y0)
    # w_y=((320.0-x0)/50.0)*coefficient
    # print "NEW w_y:"+ str(w_y)
    # w_z=((240.0-y0)/50.0)*coefficient
    # print "NEW w_z:"+ str(w_z)

    w=[1,w_y,w_z]
    print "w"
    print w


    print "Camera position:"
    print result

    wx=result[3]
    wy=result[4]
    wz=result[5]
    print "wx"
    print wx
    print "wy"
    print wy
    print "wz"
    print wz



   # wz=wz-robotPosition_theta0



    R_x = np.matrix([[1,0, 0],[0, math.cos(wx), -math.sin(wx)], [0, math.sin(wx),math.cos(wx)]])
    # print R_x

    R_y = np.matrix([[math.cos(-wy),0, math.sin(-wy)],[0, 1, 0], [-math.sin(-wy), 0,math.cos(-wy)]])
    # print R_y

    R_z = np.matrix([[math.cos(wz),- math.sin(wz),0],[math.sin(wz),math.cos(wz),0],[0, 0, 1]])
    # print R_z

    # w=[1,0,0]

    w_prime= ((w*R_y)*R_x)*R_z

    #T=almath.rotationFromRotZ(wz)*almath.rotationFromRotY(wy)*almath.rotationFromRotX(wx)

    print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
    # print almath.rotationFromRotZ(wz)




    # print "MATRIX TRANSFORM"
    # print ((R_y)*R_x)*R_z
    # print "TRANSFORM"
    # transform=np.array(list(T.toVector())).reshape(3,3)
    # print transform

    # #one way to transform
    # #print "w_prime with one transform"
    # #w_prime=w*transform
    #
    # print "w_prime with other transform"
    # prew_prime=((w*np.array(list(almath.rotationFromRotZ(wz).toVector())).reshape(3,3))*np.array(list(almath.rotationFromRotY(wy).toVector())).reshape(3,3))*np.array(list(almath.rotationFromRotX(wx).toVector())).reshape(3,3)
    # w_prime=[prew_prime[0][0],prew_prime[1][1],prew_prime[2][2]]
    #print w_prime

    print "w BEFORE ROTATION"
    print w
    #
    # print "w'="
    # print w_prime


    w=w_prime.tolist()[0]
    print "w AFTER ROTATION "
    print w
    # w=w_prime
    # print w





    n=[0,0,1]#[-math.sin(theta_c),0,math.cos(theta_c)]
    print "normal"
    print n

    diff=list(p-q for p,q in zip(P0,X_c))

    print "P0-X_c"
    print diff
    print "X_c"
    print X_c
    print "P0"
    print P0

    print "p0-X_c * n"
    print sum(p*q for p,q in zip(diff, n))
    print "w*n"
    print sum(p*q for p,q in zip(w, n))
    t= sum(p*q for p,q in zip(diff, n))/sum(p*q for p,q in zip(w, n))

    print "t="+str(t)
    X_prime= list(p+q for p,q in zip(X_c,list(t*q for q in w)))
    print X_prime

    #X_prime=[[X_prime[0]],[X_prime[1]],[X_prime[2]]]
    #transform =[[math.cos(-theta_c),0, math.sin(-theta_c)],[0,1,0],[-math.sin(-theta_c),0,math.cos(-theta_c)]]
    #X = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*transform)] for X_row in X_prime]

    X_x=X_prime[0]
    X_y=X_prime[1]
    X_z=X_prime[2]

    #X=[X_x*math.cos(-theta_c)+(-X_z*math.sin(-theta_c)),X_y, X_x*math.sin(-theta_c)+X_z*math.cos(-theta_c)]
    X=[X_x,X_y,X_z]
    # print "Position of", currentCamera, " in World is:"
    # print result
    print ""
    print "*"*50
    print ""
    print "Calculated distance in meters:"
    print "Calculated x " + str(X[0]) + " (in meters)"
    print "Calculated y " + str(X[1]) + " (in meters)"
    print "Calculated z " + str(X[2]) + " (in meters)"


    StiffnessOff(motionProxy)
    return X[0],X[1],X[2]

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
##detect("me.local")
#for loading dictionary of Shape objects
def load_obj(name ):
    with open(name + '.pkl', 'r') as f:
        return pickle.load(f)