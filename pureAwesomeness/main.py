# -*- encoding: UTF-8 -*- 

''' Whole Body Motion: Left or Right Arm position control '''

import sys
import motion
import time
import almath
import random
import socket
from naoqi import ALProxy
from vision.headPositionNaoSpace import *
##from speaker import speak
from mover import move
# from grabber import grab


def locateAndPosition(robotIP,motionProxy,shape,index):
    x,y,z=detect(robotIP,motionProxy,shape,index)

#   perfect points: (.20,0.05); (.20,-0.05)
    while (abs(y) < 0.02) or (abs(y) > 0.07) or (x < 0.19) or (x > 0.215):
        my = 0.0
        mx = 0.0

        if (y < 0.0):
            my = y - (-0.05)
        else:
            my = y - 0.05

        mx = 0
        if x < 0.19:
            mx = x - 0.205
        elif x > 0.215:
            mx = x - 0.20

        print "Move: ",mx,", ",my

        motionProxy.moveTo(mx, my, 0.0)

        newInitPos_sinCabeza(motionProxy)
        x,y,z=detect(robotIP,motionProxy,shape,index)


    #postureProxy.goToPosture("StandInit", 0.5)
    
    return x,y,z


# def transferRight2Left(robotIP,motionProxy,postureProxy):
#     postureProxy.goToPosture("StandInit", 0.5)
#
#     #motionProxy.setAngles("RShoulderPitch",[0.8],0.2)
#     motionProxy.setAngles("RShoulderPitch",[0.9],0.2)
#     #motionProxy.setAngles("RShoulderRoll",[0.0],0.2)
#     motionProxy.setAngles("RShoulderRoll",[-0.0],0.2)
#     #motionProxy.setAngles("RElbowYaw",[0.6],0.2)
#     motionProxy.setAngles("RElbowYaw",[0.3],0.2)
#     motionProxy.setAngles("RElbowRoll",[1.5],0.2)
#     motionProxy.setAngles("RWristYaw",[-0.5],0.2)
#
#
# motionProxy.openHand("LHand")
# motionProxy.setAngles("LElbowRoll",[-1.5],0.2)
# motionProxy.setAngles("LShoulderRoll",[0.0],0.2)
# motionProxy.setAngles("LShoulderPitch",[1.2],0.2)
# motionProxy.setAngles("LWristYaw",[0.3],0.2)
#
#
#
#     motionProxy.openHand("LHand")
#     motionProxy.setAngles("LWristYaw",[-1.2],0.2)
#     motionProxy.setAngles("LShoulderRoll",[0.1],0.2)
#     motionProxy.setAngles("LShoulderPitch",[1.2],0.2)
#     motionProxy.setAngles("LElbowRoll",[-1.33],0.2)
#     motionProxy.setAngles("LElbowYaw",[-0.9],0.2)
#
#
#     #motionProxy.setAngles("RElbowRoll",[1.6],0.2)
#     #motionProxy.setAngles("RElbowYaw",[0.9],0.2)
#     #motionProxy.setAngles("RShoulderRoll",[0.0],0.2)
#
#     motionProxy.closeHand("LHand")
#     motionProxy.closeHand("LHand")
#     motionProxy.openHand("RHand")
#
#     postureProxy.goToPosture("StandInit", 0.5)



def setDownBlock(motionProxy,effectorName):
    initCuerpo(motionProxy)

    if effectorName == "RArm":
        motionProxy.setAngles("RElbowRoll",1.5,0.2)
        motionProxy.setAngles("RElbowYaw",2.1,0.2)
        motionProxy.angleInterpolationWithSpeed("RShoulderPitch",1.9,0.2)
    else:
        motionProxy.setAngles("LElbowRoll",-1.5,0.2)
        motionProxy.setAngles("LElbowYaw",-2.1,0.2)
        motionProxy.angleInterpolationWithSpeed("LShoulderPitch",1.9,0.2)


    if effectorName == "RArm":
        motionProxy.openHand("RHand")
        motionProxy.closeHand("RHand")
    else:
        motionProxy.openHand("LHand")
        motionProxy.closeHand("LHand")

    newInitPos(motionProxy)


def pickUpObject(robotIP,motionProxy,postureProxy,shape,index):
    newInitPos(motionProxy)
    #postureProxy.goToPosture("StandInit", 0.5)

    rx_calib = -0.011
    ry_calib = -0.005
    lx_calib = -0.011
    ly_calib = -0.015
    
    x,y,z = locateAndPosition(robotIP,motionProxy,shape,index)
    postureProxy.goToPosture("StandInit", 0.5)

    if y>0.0:
        effectorName="LArm"
        #motionProxy.angleInterpolationWithSpeed(["RElbowRoll","LElbowRoll"],[0.0,-0.9],0.4)
        #motionProxy.angleInterpolationWithSpeed(["RShoulderPitch"],[1.9],0.4)
        #motionProxy.setAngles(["RElbowRoll","LElbowRoll"],[0.0,-1.0],0.4)
    else:
        effectorName="RArm"
        #motionProxy.angleInterpolationWithSpeed(["LElbowRoll","RElbowRoll",],[0.0,0.9],0.4)
        #motionProxy.angleInterpolationWithSpeed(["LShoulderPitch"],[1.9],0.4)
        #motionProxy.setAngles(["LElbowRoll","RElbowRoll"],[0.0,1.0],0.4)

    time.sleep(2)
    #motionProxy.stopMove()

    motionProxy.wbEnableEffectorControl(effectorName, True)

    if (effectorName == "LArm"):
        move(motionProxy,postureProxy,effectorName,[x+lx_calib,y+ly_calib,z+0.06])
    else:
        move(motionProxy,postureProxy,effectorName,[x+rx_calib,y+ry_calib,z+0.06])

    time.sleep(1)

    if effectorName =="RArm":
        motionProxy.angleInterpolationWithSpeed("RWristYaw",-1.3,0.4)
    else:
        motionProxy.angleInterpolationWithSpeed("LWristYaw",1.3,0.4)

    if effectorName == "LArm":
        motionProxy.openHand("LHand")
        move(motionProxy,postureProxy,effectorName,[x+lx_calib,y+ly_calib,z-0.005])
        motionProxy.closeHand("LHand")
    else:
        motionProxy.openHand("RHand")
        move(motionProxy,postureProxy,effectorName,[x+rx_calib,y+ry_calib,z-0.005])
        motionProxy.closeHand("RHand")
    
    move(motionProxy,postureProxy,effectorName,[x,y,z+0.09])

    time.sleep(1)
    motionProxy.wbEnableEffectorControl(effectorName, False)

    setDownBlock(motionProxy,effectorName)



def removeBlock(blocks,shape):
    nblocks = []

    for i in range(0,len(blocks)):
        if (blocks[i] != shape):
            nblocks.append(blocks[i])

    return nblocks


def compareList(blocks,nblocks):
    for i in range(0,len(blocks)):
        taken = True
        for j in range(0,len(nblocks)):
            if (blocks[i] == nblocks[j]):
                taken = False

        if (taken):
            return blocks[i]

    print "this is an error"
    
    return -1


def lookup(oList,shape):
    for i in range(0,len(oList)):
        if (oList[i].obj == shape):
            return i
    return -1


def myMoveSlave(robotIP,motionProxy,postureProxy,initialBlocks,currentBlocks,myBlocks,shape):
    index = lookup(initialBlocks,shape)
    print shape, "in position ", index
    pickUpObject(robotIP,motionProxy,postureProxy,shape,index)

    currentBlocks2 = []
    for i in range(0,len(currentBlocks)):
        if (currentBlocks[i].obj != shape):
            currentBlocks2.append(currentBlocks[i])
    myBlocks.append(shape)

    print "myBlocks: ", myBlocks
    print "remaining blocks: "
    for i in range(0,len(currentBlocks2)):
        sys.stdout.write(currentBlocks2[i].obj)
        sys.stdout.write(', ')

    print ""

    return myBlocks, currentBlocks2


def myMove(robotIP,motionProxy,postureProxy,initialBlocks,currentBlocks,myBlocks):

    shape = random.choice(currentBlocks).obj
    index = lookup(initialBlocks,shape)
    print shape, "in position ", index
    pickUpObject(robotIP,motionProxy,postureProxy,shape,index)

    currentBlocks2 = []
    for i in range(0,len(currentBlocks)):
        if (currentBlocks[i].obj != shape):
            currentBlocks2.append(currentBlocks[i])
    myBlocks.append(shape)

    print "myBlocks: ", myBlocks
    print "remaining blocks: "
    for i in range(0,len(currentBlocks2)):
        #currentBlocks2[i].printIt()
        sys.stdout.write(currentBlocks2[i].obj)
        sys.stdout.write(', ')

    print ""

    return myBlocks, currentBlocks2


def hisMove(robotIP,motionProxy,postureProxy,currentBlocks2,hisBlocks):
    taken = detectOpponentsMove(robotIP,motionProxy,postureProxy,currentBlocks2)

    currentBlocks = []
    for i in range(0,len(currentBlocks2)):
        if (currentBlocks2[i].obj != taken):
            currentBlocks.append(currentBlocks2[i])
    hisBlocks.append(taken)

    return hisBlocks,currentBlocks


def playRound2_second(robotIP,motionProxy,postureProxy):

    #tts = ALProxy("ALTextToSpeech", robotIP, 9559)

    initialPieces = ['yellow square','blue triangle','blue square','yellow circle','red square','yellow triangle',
                   'red circle','red triangle','blue circle']

    myBlocks = []
    hisBlocks = []

    #postureProxy.goToPosture("StandInit", 0.5)
    newInitPos_fast(motionProxy)
    currentBlocks = idBlocks(robotIP,motionProxy,postureProxy,listOfPiecesLabels,False,len(initialPieces))
    initialBlocks = []
    for i in range(0,len(currentBlocks)):
        initialBlocks.append(currentBlocks[i])

    for count in range(0,3):

        #tts.say('Your move')

        hisBlocks,currentBlocks2 = hisMove(robotIP,motionProxy,postureProxy,currentBlocks,hisBlocks)

        #tts.say('My move')

        myBlocks,currentBlocks = myMove(robotIP,motionProxy,postureProxy,initialBlocks,currentBlocks2,myBlocks)

        #print "He tookted ", taken

        print "myBlocks: ", myBlocks
        print "hisBlocks: ", hisBlocks

def returnShape2(shape,currentBlocks):
    theshapes = ["red square", "blue square", "yellow square", "red triangle", "blue triangle", "yellow triangle", "red circle", "blue circle", "yellow circle"]

    #print "the moov is: ",moov

    #c = 0
    for i in range(0,9):
        #if (lookup(currentBlocks,theshapes[i]) != -1):
        if (theshapes[i] == shape):
            return i
        #c += 1


    print "Houston, I didn't find that shape"
    return -1

def returnShape(moov,currentBlocks):
    theshapes = ["red square", "blue square", "yellow square", "red triangle", "blue triangle", "yellow triangle", "red circle", "blue circle", "yellow circle"]

    return theshapes[moov]

def playRound2_first(robotIP,motionProxy,postureProxy):
    initialPieces = ['yellow square','blue triangle','blue square','yellow circle','red square','yellow triangle',
                   'red circle','red triangle','blue circle']

    myBlocks = []
    hisBlocks = []

    #postureProxy.goToPosture("StandInit", 0.5)
    newInitPos_fast(motionProxy)
    currentBlocks = idBlocks(robotIP,motionProxy,postureProxy,listOfPiecesLabels,False,len(initialPieces))
    initialBlocks = []
    for i in range(0,len(currentBlocks)):
        initialBlocks.append(currentBlocks[i])

    for count in range(0,3):
        myBlocks,currentBlocks2 = myMove(robotIP,motionProxy,postureProxy,initialBlocks,currentBlocks,myBlocks)
        print "myBlocks: ", myBlocks

        hisBlocks,currentBlocks = hisMove(robotIP,motionProxy,postureProxy,currentBlocks2,hisBlocks)

        print "hisBlocks: ", hisBlocks

def playRound2_first_slave(robotIP,motionProxy,postureProxy,conn):
    initialPieces = ['yellow square','blue triangle','blue square','yellow circle','red square','yellow triangle',
                   'red circle','red triangle','blue circle']

    myBlocks = []
    hisBlocks = []

    #postureProxy.goToPosture("StandInit", 0.5)
    newInitPos_fast(motionProxy)
    currentBlocks = idBlocks(robotIP,motionProxy,postureProxy,listOfPiecesLabels,False,len(initialPieces))
    initialBlocks = []
    for i in range(0,len(currentBlocks)):
        initialBlocks.append(currentBlocks[i])

    for count in range(0,3):
        print "My move"

        moov = conn.recv(1024)
        shape = returnShape(int(moov),currentBlocks)
        print "told to pick up ",shape

        myBlocks,currentBlocks2 = myMoveSlave(robotIP,motionProxy,postureProxy,initialBlocks,currentBlocks,myBlocks,shape)
        msg = "acts: "+str(moov)+" 0\n"
        conn.send(msg)

        print "Sent: ",msg

        #tts.say('Your move')
        print "Your move"

        moov = conn.recv(1024)
        hisBlocks,currentBlocks = hisMove(robotIP,motionProxy,postureProxy,currentBlocks2,hisBlocks)
        print "He tookted the ", hisBlocks[count]
        moov = returnShape2(hisBlocks[count],currentBlocks2)
        print "action: ", moov
        msg = "acts: 0 "+str(moov)+"\n"
        conn.send(msg)
        print "Sent: ",msg

        print "myBlocks: ", myBlocks
        print "hisBlocks: ", hisBlocks


def preliminaries():
    myipaddress = '10.102.15.52'


    # create a socket connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.bind(('10.104.67.181', 3000))
    s.bind((myipaddress, 3000))
    s.listen(1)
    conn, adr = s.accept()

    # read a nickname
    mynickname = conn.recv(1024)
    print "received nickname: ", mynickname

    # send nicknames
    nicknamestr = mynickname + " realhmn"
    conn.send(nicknamestr)

    #time.sleep(2)
    raw_input("press enter when ready ... ")

    print "going to send the ready command"

    # send the "ready" command
    conn.send('ready')

    moov = conn.recv(1024)

    return s, conn

def playGame(robotIP,motionProxy,postureProxy,conn,iters):

    for i in range(0,iters):
        playRound2_first_slave(robotIP,motionProxy,postureProxy,conn)

        print "round ",i," finished"

        # wait for keyboard input
        raw_input("press enter when ready ... ")



def server(robotIP,motionProxy,postureProxy):

    s, conn = preliminaries()

    playGame(robotIP,motionProxy,postureProxy,conn,10)

    conn.close()


def main(robotIP,motionProxy,postureProxy):

    playRound2_first(robotIP,motionProxy,postureProxy)
#     server(robotIP,motionProxy,postureProxy)



    
if __name__ == '__main__':
  
    robotIP="10.104.67.181"
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

    main(robotIP,motionProxy,postureProxy)

##main(robotIP,motionProxy,postureProxy)
##motionProxy = ALProxy("ALMotion", "10.104.67.181", 9559)

