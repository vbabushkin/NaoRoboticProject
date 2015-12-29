from naoqi import ALProxy
import time
import sys


def StiffnessOn(proxy, value=1.0):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = value
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)
def err_msg():
    print ""
    print "*For terminal use only*"
    print "-"*9+"USAGE"+"-"*9
    print "python stop.py ip [--options]"
    print "--options: 1.standinit 2.crouch"
    print "crouch is default for options"
    pass
def kill(name):
    if name in ["vahan","Vahan"]:
        return "vahan.local"
    elif name == "me":
        return "me.local"
    else:
        err_msg()
        sys.exit(1)

    
def main(robotIP,action = "crouch"):
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
## this will make robot crouch and sleep
    if action == "crouch":
        StiffnessOn(motionProxy,1.0)
        postureProxy.goToPosture("Crouch",0.5)
        time.sleep(0.5)
        StiffnessOn(motionProxy,0.0)
    elif action == "standinit":
        postureProxy.goToPosture("StandInit",0.5)
    else:
        err_msg()
        
if __name__ == "__main__":
    robotIp = "127.0.0.1"
    if len(sys.argv) <= 1:
        err_msg()
    elif len(sys.argv) == 2:
        robotIP = kill(str(sys.argv[1]))
        main(robotIP)
    elif len(sys.argv) == 3:
        robotIP = kill(str(sys.argv[1]))
##        print 
        main(str(robotIP),str(sys.argv[2]))
    else:
        err_msg()
##main("me.local")
	

