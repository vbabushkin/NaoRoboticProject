import sys
import motion
import almath
import time
from naoqi import ALProxy


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

def main(robotIP):
    ''' Example showing a path of two positions
    Warning: Needs a PoseInit before executing
    '''

    # Init proxies.
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

    # Set NAO in Stiffness On
    StiffnessOn(motionProxy)

    # Send NAO to Pose Init
    postureProxy.goToPosture("Crouch", 0.5)

    effector   = "LArm"
    space      = motion.FRAME_ROBOT
    axisMask   = almath.AXIS_MASK_VEL    # just control position
    isAbsolute = False

    # Since we are in relative, the current position is zero
    currentPos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # Define the changes relative to the current position
    dx         =  0.05      # translation axis X (meters)
    dy         =  0.03      # translation axis Y (meters)
    dz         =  0.08      # translation axis Z (meters)
    dwx        =  0.00      # rotation axis X (radians)
    dwy        =  0.00      # rotation axis Y (radians)
    dwz        =  0.00      # rotation axis Z (radians)
    targetPos  = [dx, dy, dz, dwx, dwy, dwz]

    # Go to the target and back again
    path       = [targetPos]
    times      = [3.0] # seconds

    motionProxy.positionInterpolation(effector, space, path,axisMask, times, isAbsolute)


    # Simple command for the HeadYaw joint at 10% max speed
    names            = "LWristYaw"
    angles           = 70.0*almath.TO_RAD
    fractionMaxSpeed = 0.1
    motionProxy.setAngles(names,angles,fractionMaxSpeed)

    motionProxy.openHand('LHand')
    time.sleep(3)
    motionProxy.closeHand('LHand')


    postureProxy.goToPosture("Crouch", 0.5)
    StiffnessOff(motionProxy)

if __name__ == "__main__":
    robotIp = "127.0.0.1"

    if len(sys.argv) <= 1:
        print "Usage python motion_cartesianArm1.py robotIP (optional default: 127.0.0.1)"
    else:
        robotIp = sys.argv[1]





main("10.104.64.106")
