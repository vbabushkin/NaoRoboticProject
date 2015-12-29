from naoqi import ALProxy
import sys
def speak(IP,text):
    PORT = 9559
    try:
        tts = ALProxy("ALTextToSpeech", IP, PORT)
    except Exception,e:
        print "Could not create proxy to ALTextToSpeech"
        print "Error was: ",e
        sys.exit(1)
        
    #Says a test std::string
    tts.say(text)
