import sys
import motion
import time
from naoqi import ALProxy

def move(motionProxy,postureProxy, effectorName,coordinate):
    ''' Example of a whole body Left or Right Arm position control
        Warning: Needs a PoseInit before executing
                 Whole body balancer must be inactivated at the end of the script
    '''

    # Init proxies.
##    try:
##        motionProxy = ALProxy("ALMotion", robotIP, 9559)
##    except Exception, e:
##        print "Could not create proxy to ALMotion"
##        print "Error was: ", e
##
##    try:
##        postureProxy = ALProxy("ALRobotPosture", robotIP, 9559)
##    except Exception, e:
##        print "Could not create proxy to ALRobotPosture"
##        print "Error was: ", e

    # X Axis LArm Position feasible movement = [ +0.00, +0.12] meter
    # Y Axis LArm Position feasible movement = [ -0.05, +0.10] meter
    # Y Axis RArm Position feasible movement = [ -0.10, +0.05] meter
    # Z Axis LArm Position feasible movement = [ -0.10, +0.10] meter

##    coef = 1.0
##    if (effectorName == "LArm"):
##        coef = +1.0
##    elif (effectorName == "RArm"):
##        coef = -1.0
##
##    coordinate[1]=coordinate[1]*coef
        
    motionProxy.wbSetEffectorControl(effectorName, coordinate)       
