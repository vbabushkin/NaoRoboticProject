__author__ = 'vahan'

import cv2
import shapeDetectionModuleInterface
import shapeDetectionModule
import time
import random
from naoqi import ALProxy

"""
    To return current configuration of legos on the gameboard along with their centers
"""

def getCurrentGameboard():
    NUM_OF_TIMES=3
    THRESHOLD=2

    #first we scan the gameboard NUM_OF_TIMES times and store shapes detected during each time:
    detected=[[],[],[],[],[],[],[],[],[]]

    for times in range(0,NUM_OF_TIMES):
        listOfShapesDetected= shapeDetectionModuleInterface.shapeDetectionMain(IP, PORT)
        for shapeID in range(0,9):
            detected[times].append(listOfShapesDetected[shapeID])



    #mean coordinates
    meanOfCenters=[]

    #list of probabilities to detect a particular shape
    probList=[]

    #calculate probabilities that each figure appears on the gameboard
    for shapeID in range(0,9):
        shapeCentersListLength=0
        meanX=0
        meanY=0
        n=0
        for times in range(0,NUM_OF_TIMES):
            #only count those shapes, which are detected in single exemplars (i.e. no 2 red triangles)
            if(len(detected[times][shapeID].getCenters())==1 or len(detected[times][shapeID].getCenters())==0):
                shapeCentersListLength+=len(detected[times][shapeID].getCenters())
                if(len(detected[times][shapeID].getCenters())==1):
                    meanX+=detected[times][shapeID].getCenters()[0][0]
                    meanY+=detected[times][shapeID].getCenters()[0][1]
                    n+=1.0
            else:
                shapeCentersListLength+=0
        probList.append(shapeCentersListLength)
        if n==0:
            meanOfCenters.append((0, 0))
        else:
            meanOfCenters.append((meanX/n, meanY/n))


    #to remove noise
    for shapeID in range(0,9):
        if probList[shapeID]< THRESHOLD:
            meanOfCenters[shapeID]=(0,0)


    detectedPiecesIDs=[i for i,v in enumerate(probList) if v >= THRESHOLD]

    return (detectedPiecesIDs,meanOfCenters)
"""
    To select a random shape on the gameboard
    :param detectedPiecesIDs: IDs of shapes currently on the gameboard
"""
def selectShapeRandomly(detectedPiecesIDs):
    if len(detectedPiecesIDs)!=0:
        return random.choice(detectedPiecesIDs)
    else:
        return None


#main module
if __name__ == '__main__':
    IP = "10.104.67.182"
    PORT = 9559

    tts    = ALProxy("ALTextToSpeech", IP, PORT)


    t0 = time.time()


    listOfPiecesLabels=['red triangle','red square','red circle',
                       'blue triangle', 'blue square', 'blue circle',
                       'yellow triangle','yellow square','yellow circle']

    print "****************************************************************************"
    print "START"
    tts.say("Hello. Nice to meet you")


    #scan the gameboard
    (detectedPiecesIDs,meanOfCenters)=getCurrentGameboard()

    #initial number of shapes
    numOfShapes=len(detectedPiecesIDs)
    print "THERE ARE FOLLOWING PIECES ON THE GAMEBOARD:"
    tts.say("THERE ARE FOLLOWING PIECES ON THE GAMEBOARD:")
    for id in detectedPiecesIDs:
        tts.say(listOfPiecesLabels[id])
        print listOfPiecesLabels[id]
        #print meanOfCenters[id]

    #randomly select who plays first
    #if 1 -- robot
    #if 0 -- human
    playsFirst=random.randint(0, 1)
    while(numOfShapes!=3):
        if(playsFirst==1):
            #first NAO selects a piece then the user:
            #NAO selects a piece
            pickedPieceID=selectShapeRandomly(detectedPiecesIDs)
            if(pickedPieceID != None):
                print "NAO SELECTS THE FOLLOWING PIECE:"
                tts.say("I am selecting the")
                tts.say(listOfPiecesLabels[pickedPieceID])
                print listOfPiecesLabels[pickedPieceID]
                print "in position"
                print meanOfCenters[pickedPieceID]
                numOfShapes=len(detectedPiecesIDs)
            else:
                print "There is nothing to select"
                tts.say("There is nothing to select")
                quit()


            #scan the gameboard again
            (detectedPiecesIDs,meanOfCenters)=getCurrentGameboard()
            #wait between two turns for 5 sec
            time.sleep(5)
            #user selects a piece:
            print "IT IS YOUR TURN NOW. PLEASE SELECT A PIECE"
            tts.say("It is your turn now. Please select a piece.")
            while True:
                #prevoius configuration
                previousPiecesIDs=detectedPiecesIDs
                #wait 5 seconds
                time.sleep(5)
                #then scan the gameboard again
                (detectedPiecesIDs,meanOfCenters)=getCurrentGameboard()

                pieceSelected=list(set(previousPiecesIDs) - set(detectedPiecesIDs))

                if(len(pieceSelected)==0):
                    print "YOU HAVEN'T SELECTED A PIECE!!! PLEASE SELECT A PIECE"
                    tts.say("YOU HAVEN'T SELECTED A PIECE!!! PLEASE SELECT A PIECE")
                    continue
                else:
                    print "YOU HAVE SELECTED THE FOLLOWING PIECE:"
                    tts.say("you have selected a "+listOfPiecesLabels[pieceSelected[0]])
                    print listOfPiecesLabels[pieceSelected[0]]
                    numOfShapes=len(detectedPiecesIDs)
                    break

            # while(len(detectedPiecesIDs)==numOfShapes):
            #     print "YOU HAVEN'T SELECTED A PIECE!!! PLEASE SELECT A PIECE"
            #     (detectedPiecesIDs,meanOfCenters)=getCurrentGameboard()
            #     time.sleep(5)
        else:
            #user selects a piece:
            print "IT IS YOUR TURN NOW. PLEASE SELECT A PIECE"
            tts.say("It is your turn now. Please select a piece.")
            while True:
                #prevoius configuration
                previousPiecesIDs=detectedPiecesIDs
                #wait 5 seconds
                time.sleep(5)
                #then scan the gameboard again
                (detectedPiecesIDs,meanOfCenters)=getCurrentGameboard()

                pieceSelected=list(set(previousPiecesIDs) - set(detectedPiecesIDs))

                if(len(pieceSelected)==0):
                    print "YOU HAVEN'T SELECTED A PIECE!!! PLEASE SELECT A PIECE"
                    tts.say("YOU HAVEN'T SELECTED A PIECE!!! PLEASE SELECT A PIECE")
                    continue
                else:
                    print "YOU HAVE SELECTED THE FOLLOWING PIECE:"
                    tts.say("you have selected a "+listOfPiecesLabels[pieceSelected[0]])
                    print listOfPiecesLabels[pieceSelected[0]]
                    numOfShapes=len(detectedPiecesIDs)
                    break



            #scan the gameboard again
            (detectedPiecesIDs,meanOfCenters)=getCurrentGameboard()
            #wait between two turns for 5 sec
            time.sleep(5)
            #NAO selects a piece
            pickedPieceID=selectShapeRandomly(detectedPiecesIDs)
            if(pickedPieceID != None):
                print "NAO SELECTS THE FOLLOWING PIECE:"
                tts.say("I am selecting the")
                tts.say(listOfPiecesLabels[pickedPieceID])
                print listOfPiecesLabels[pickedPieceID]
                print "in position"
                print meanOfCenters[pickedPieceID]
                numOfShapes=len(detectedPiecesIDs)
            else:
                print "There is nothing to select"
                tts.say("There is nothing to select")
                quit()

        #wait between rounds for 5 sec
        time.sleep(5)
        print "****************************************************************************"
        print "NEXT ROUND"

        #scan the gameboard
        (detectedPiecesIDs,meanOfCenters)=getCurrentGameboard()

        #remaining number of shapes
        numOfShapes=len(detectedPiecesIDs)
        tts.say("NEXT ROUND")
        print "THERE ARE FOLLOWING PIECES ON THE GAMEBOARD:"
        tts.say("THERE ARE FOLLOWING PIECES ON THE GAMEBOARD:")
        for id in detectedPiecesIDs:
            tts.say(listOfPiecesLabels[id])
            print listOfPiecesLabels[id]


    print "****************************************************************************"
    print "END"
    tts.say("The game is over")


    t1 = time.time()

    total = t1-t0
    print "TOTAL TIME REQUIRED: "
    print total


