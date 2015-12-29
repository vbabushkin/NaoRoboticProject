# -*- encoding: UTF-8 -*-

'''Cartesian control: Arm trajectory example'''
''' This example is only compatible with NAO '''

import argparse
import motion
import math
from naoqi import ALProxy
import sys
import time

def main(robotIP):
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)

    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e

    # Send NAO to Pose Init
    postureProxy.goToPosture("Crouch", 0.5)

    # Example moving the left hand up a little using transforms
    # Note that this is easier to do with positionInterpolation
    chainName  = 'LArm'
    # Defined in 'Torso' space
    space  = motion.FRAME_TORSO
    # We will use a single transform
    # | R R R x |
    # | R R R y |
    # | R R R z |
    # | 0 0 0 1 |
    # Get the current transform, in 'Torso' space using
    # the command angles.
    useSensorValue = False
    initialTransform = motionProxy.getTransform('LArm', space, useSensorValue)
    # Copy the current transform
    targetTransform = initialTransform
    # add 2cm to the z axis, making the arm move upwards
    targetTransform[11] = initialTransform[11] + 0.02
    # construct a path with only one transform
    path  = [targetTransform]
    # The arm does not have enough degees of freedom
    # to be able to constrain all the axes of movement,
    # so here, we will choose an axis mask of 7, which
    # will contrain position only
    # x = 1, y = 2, z = 4, wx = 8, wy = 16, wz = 32
    # 1 + 2 + 4 = 7
    axisMask  = 7
    # Allow three seconds for the movement
    duration  = [3.0]
    isAbsolute  = False
    motionProxy.transformInterpolation(chainName, space, path,
    axisMask, duration, isAbsolute)
    finalTransform = motionProxy.getTransform('LArm', motion.FRAME_TORSO, False)
    print 'Initial', initialTransform
    print 'Target', targetTransform
    print 'Final', finalTransform

    time.sleep(1.0)

    # # Example moving the left hand up a little using transforms
    # # Note that this is easier to do with positionInterpolation
    #
    # space      = motion.FRAME_ROBOT
    # axisMask   = motion.AXIS_MASK_ALL   # full control
    # isAbsolute = False
    # # Lower the Torso and move to the side
    # effector   = "Torso"
    # path       = [1.0, 0.0, 0.0, 0.0,
    #               0.0, 1.0, 0.0, -0.07,
    #               0.0, 0.0, 1.0, -0.03]
    # duration   = 2.0                    # seconds
    # motionProxy.transformInterpolation(effector, space, path,
    #                              axisMask, duration, isAbsolute)
    # # LLeg motion
    # effector   = "LLeg"
    # cs = math.cos(45.0*math.pi/180.0)
    # ss = math.cos(45.0*math.pi/180.0)
    # path       = [ cs, -ss, 0.0, 0.0,
    #                ss,  cs, 0.0, 0.06,
    #               0.0, 0.0, 1.0, 0.0]
    # duration   = 2.0                    # seconds
    # motionProxy.transformInterpolation(effector, space, path,
    #                              axisMask, duration, isAbsolute)

    StiffnessOff(motionProxy)

# def main(robotIP, PORT=9559):
#     ''' Example showing a path of two positions
#     Warning: Needs a PoseInit before executing
#     '''
#
#     motionProxy  = ALProxy("ALMotion", robotIP, PORT)
#     postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
#
#     # Wake up robot
#     motionProxy.wakeUp()
#
#     # Send NAO to Pose Init
#     postureProxy.goToPosture("Crouch", 0.5)
#
#     effector   = "LArm"
#     frame      = motion.FRAME_ROBOT
#     axisMask   = almath.AXIS_MASK_VEL # just control position
#     useSensorValues = False
#
#     path = []
#     currentTf = motionProxy.getTransform(effector, frame, useSensorValues)
#     targetTf  = almath.Transform(currentTf)
#
#
#     targetTf.r1_c4 += 0.207688775972 # x
#     targetTf.r2_c4 += 0.0175064466894 # y
#
#     path.append(list(targetTf.toVector()))
#     path.append(currentTf)
#
#     # Go to the target and back again
#     times      = [2.0, 4.0] # seconds
#
#     motionProxy.transformInterpolation(effector, frame, path, axisMask, times,True)
#
#     # Go to rest position
#     motionProxy.rest()

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


if __name__ == "__main__":
    robotIp = "10.104.4.40"
    main(robotIp)



    #
    # # Init proxies.
    # try:
    #     motionProxy = ALProxy("ALMotion", robotIP, 9559)
    # except Exception, e:
    #     print "Could not create proxy to ALMotion"
    #     print "Error was: ", e
    #
    # try:
    #     postureProxy = ALProxy("ALRobotPosture", robotIP, 9559)
    # except Exception, e:
    #     print "Could not create proxy to ALRobotPosture"
    #     print "Error was: ", e
    #
    # # Set NAO in Stiffness On
    # StiffnessOn(motionProxy)
    #
    # # Send NAO to Pose Init
    # postureProxy.goToPosture("Crouch", 0.5)
    #
    #
    # #####################
    # ## get robot position before move
    # #####################
    # initRobotPosition = almath.Pose2D(motionProxy.getRobotPosition(False))
    #
    #
    # print initRobotPosition
    #
    #
    # arm_transform = motionProxy.getTransform("LArm",2,True)
    # robot2Arm = almath.Transform(almath.vectorFloat(arm_transform))
    # print "robot LArm: ",robot2Arm
    #
    #
    # effector   = "LArm"
    # space      = motion.FRAME_ROBOT
    # axisMask   = almath.AXIS_MASK_VEL    # just control position
    # isAbsolute = False
    #
    # # Since we are in relative, the current position is zero
    # currentPos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    #
    # print x, y, z, theta
    # # Define the changes relative to the current position
    # dx         =  x      # translation axis X (meters)
    # dy         =  y      # translation axis Y (meters)
    # dz         =  z      # translation axis Z (meters)
    # dwx        =  0.00      # rotation axis X (radians)
    # dwy        =  0.00      # rotation axis Y (radians)
    # dwz        =  theta      # rotation axis Z (radians)
    # targetPos  = [dx, dy, dz, dwx, dwy, dwz]
    #
    # # Go to the target and back again
    # path       = [currentPos,targetPos]
    # times      = [3.0,6.0] # seconds
    #
    # motionProxy.positionInterpolation(effector, space, path,axisMask, times, isAbsolute)
    #
    #
    # # Simple command for the HeadYaw joint at 10% max speed
    # names            = "LWristYaw"
    # angles           = 70.0*almath.TO_RAD
    # fractionMaxSpeed = 0.1
    # motionProxy.setAngles(names,angles,fractionMaxSpeed)
    #
    # motionProxy.openHand('LHand')
    # time.sleep(3)
    # motionProxy.closeHand('LHand')
    #
    #
    # postureProxy.goToPosture("Crouch", 0.5)
    # StiffnessOff(motionProxy)
