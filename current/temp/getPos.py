# -*- encoding: UTF-8 -*-

import sys
from naoqi import ALProxy

def update_pos(robotIP,name):
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)

    # Example showing how to get the end of the right arm as a transform
    # represented in torso space. The result is a 4 by 4 matrix composed
    # of a 3*3 rotation matrix and a column vector of positions.
    name  = 'RArm'
    ##0 for torso, 1 for the world, 2 for the robot
    space  = 2
    useSensorValues  = True
    result = motionProxy.getTransform(name, space, useSensorValues)
    print result
    return result
##    for i in range(0, 4):
##        for j in range(0, 4):
##            print result[4*i + j],
##        print ''


update_pos("me.local", 'RArm')
