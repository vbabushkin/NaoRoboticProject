# -*- encoding: UTF-8 -*-
import time
import sys
from naoqi import ALProxy


def grab(robotIP,effectorName,sig):
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)
    #facing stright down to mark
    if effectorName == "LArm":
        hand="LHand"
    else:
        hand="RHand"
    if sig=='o':
        motionProxy.openHand(hand)
    elif sig=='c':
        motionProxy.closeHand(hand)
    else:
        print "wrong cammand for the grabber"
        sys.exit(1)

##grab("me.local","LArm","o")
