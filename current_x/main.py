# -*- encoding: UTF-8 -*- 

''' Whole Body Motion: Left or Right Arm position control '''

import sys
import motion
import time
import almath
from naoqi import ALProxy
from vision.headPositionNaoSpace import detect
##from detector import detect
from speaker import speak
from mover import move
from grabber import grab


def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)
def onZ(z_f,z_m):
    if z_f+0.01<=z_m:
        return True
    else:
        return False
#this checks whether target is within reach
##    # X Axis LArm Position feasible movement = [ +0.00, +0.12] meter
##    # Y Axis LArm Position feasible movement = [ -0.05, +0.10] meter
##    # Y Axis RArm Position feasible movement = [ -0.10, +0.05] meter
##    # Z Axis LArm Position feasible movement = [ -0.10, +0.10] meter
def within_reach(effectInit,x,y,z):
    axis={}
    if effectInit[0]<x-0.12:
        axis['x']='x'
    if effectInit[1]<y-0.10:
        axis['y']='y'
    if effectInit[2]<z-0.10:
        axis['z']='z'
    return axis
def arm_dist(motionProxy,effectorName,x,y,z):
    # arm transformation in robot space
    arm_transform = motionProxy.getTransform(effectorName,2,True)
    robot2Arm = almath.Transform(almath.vectorFloat(arm_transform))
    rot=almath.position6DFromTransform(robot2Arm)
##    print effectorName,"position",robot2Arm.r1_c4,robot2Arm.r2_c4,robot2Arm.r3_c4
    mx,my,mz=rot.wx,rot.wy,rot.wz
    x_d,y_d,z_d=x-robot2Arm.r1_c4,y-robot2Arm.r2_c4,z-robot2Arm.r3_c4
##    print "distances update:"
##    print x_d,y_d,z_d
    return [x_d,y_d,z_d],mx

def aline_joints(motionProxy,effectorName):
    if effectorName=="LArm":
        coef=-1.0
        hand=motionProxy.getPosition("LHand", 2, False)
        elbow = motionProxy.getPosition("LElbowRoll", 2, False)
        joint="LElbowRoll"
    else:
        coef=1.0
        hand=motionProxy.getPosition("RHand", 2, False)
        elbow = motionProxy.getPosition("RElbowRoll", 2, False)
        joint="RElbowRoll"
    ##upper limit of arm joint
    while elbow[2]>hand[2] and elbow[2]-hand[2]>0.09:
        print "working on the joints"
        ##fix the angles on respective joints
        ##first find the angle
        elbow_angle = motionProxy.getAngles(joint, True)
        if -1.5621<elbow_angle<-0.0174:
            motionProxy.angleInterpolationWithSpeed(joint,elbow_angle+coef*5*almath.TO_RAD,0.4)
        else:
            print "Elbow roll is reaching to upper limit"
            motionProxy.angleInterpolationWithSpeed(joint,coef*1.5621,0.4)
            break
    ##lower limit of arm joint
    while elbow[2]<hand[2] and hand[2]-elbow[2]>0.04:
        print "working on the joints"
        elbow_angle = motionProxy.getAngles(joint, True)
        if -1.5621<elbow_angle<-0.0174:
            motionProxy.angleInterpolationWithSpeed(joint,elbow_angle+coef*5*almath.TO_RAD,0.4)
        else:
            print "Elbow roll is reaching to lower limit!"
            motionProxy.angleInterpolationWithSpeed(joint,coef*1.5621,0.4)
            break

    

def main(robotIP):
    ''' Example of a whole body Left or Right Arm position control
        Warning: Needs a PoseInit before executing
                 Whole body balancer must be inactivated at the end of the script
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
    postureProxy.goToPosture("StandInit", 0.5)
##    # Active LArm tracking
    print detect(robotIP)
    x,y,z=detect(robotIP)
    print "vision by art:"
    print x,y,z

    ##this will select right or left hand according to the y axis of naomark
    if y>0:
        effectorName="LArm"
        effectorHand="LHand"
        shoulderPitch="LShoulderPitch"
        coef=-1
    else:
        effectorName="RArm"
        effectorHand="RHand"
        shoulderPitch="RShoulderPitch"
        coef=1
    print "I chose ",effectorName,"cuz y= ",y
    
    nao2mark=arm_dist(motionProxy,effectorName,x,y,z)
    dist_x,dist_y,dist_z=tuple(nao2mark[0])
    w_x=nao2mark[1]
    
    isEnabled = True
    motionProxy.wbEnableEffectorControl(effectorName, isEnabled)
    space     = motion.FRAME_ROBOT
    useSensor = False
    HandInit = motionProxy.getPosition(effectorHand, space, useSensor)
##    position the hand on obove
    while HandInit[2]<z+0.1:
##        print HandInit[2]
        shoulder_angle = motionProxy.getAngles(shoulderPitch, True)
        motionProxy.angleInterpolationWithSpeed(shoulderPitch,shoulder_angle[0]-6*almath.TO_RAD,0.4)
        HandInit = motionProxy.getPosition(effectorHand, space, useSensor)
    ##initiate the move
    effectorInit = motionProxy.getPosition(effectorName, space, useSensor)
    move(robotIP,effectorName,[effectorInit[0]-0.01,effectorInit[1],z+0.065])
    aline_joints(motionProxy,effectorName)
    
    while abs(dist_x) >0.02 and abs(dist_y) > 0.02 and abs(dist_z) >0.06:
        effectorInit = motionProxy.getPosition(effectorName, space, useSensor)
        aline_joints(motionProxy,effectorName)
        move(robotIP,effectorName,[effectorInit[0]+dist_x*0.2,effectorInit[1]+dist_y*0.2,z+0.06])
        x,y,z=detect(robotIP)
        nao2mark=arm_dist(motionProxy,effectorName,x,y,z)
        dist_x,dist_y,dist_z=tuple(nao2mark[0])
        
        ##testing how reliable the mark detection
        print 'next vision art',x,y,z
    aline_joints(motionProxy,effectorName)
    effectorInit = motionProxy.getPosition(effectorName, space, useSensor)
    x,y,z=detect(robotIP)
    nao2mark=arm_dist(motionProxy,effectorName,x,y,z)
    dist_x,dist_y,dist_z=tuple(nao2mark[0])
    move(robotIP,effectorName,[x,y,z+0.06])
    move(robotIP,effectorName,[effectorInit[0]+dist_x,effectorInit[1]+dist_y,z+0.06])
    w_x=nao2mark[1]
##    move(robotIP,effectorName,[x,y,z+0.04])
##    HandPos = motionProxy.getPosition(effectorHand, space, useSensor)
##    print "hand rotates: ",HandPos[3]*almath.TO_DEG
    if effectorName =="RArm":
        motionProxy.angleInterpolationWithSpeed("RWristYaw",1.0-w_x,0.4)
    else:
        motionProxy.angleInterpolationWithSpeed("LWristYaw",1.0-w_x,0.4)
    ##this opens a hand
    grab(robotIP,effectorName,'o')
    ##and moves down toward target
    move(robotIP,effectorName,[x,y,z-0.02])
    ##then closes the hand
    grab(robotIP,effectorName,'c')
    effectorInit = motionProxy.getPosition(effectorName, space, useSensor)
##    print "last position of hand: ",effectorInit

    
    # Deactivate Head tracking
    isEnabled    = False
    motionProxy.wbEnableEffectorControl(effectorName, isEnabled)


main("10.104.67.182")
