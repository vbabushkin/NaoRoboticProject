import socket
import sys
import naoqi
from naoqi import ALProxy

mew = ALProxy("ALTextToSpeech",'10.104.67.181', 9559)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

##server_address = ('localhost', 4000)
server_address = ('10.104.67.79', 4000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.connect(server_address)

print "connection"

##rawData = sock.recv(1024)
##print rawData

while True:
        # Look for the response
    	rawData = sock.recv(1024)
    	data = rawData.split('*')
##    	print rawData
    	mew.say(data[0])

    	sock.sendall("ready")

    	print >>sys.stderr, 'received "%s"' % data
    	
##	data = rawData.split('$')
##	for x in data:
##		if (x == "1"): # Preventer (cautious but happy)(Eyes flash yellow three times then turn green)
##			mew.say("Please don't cheat me! Let's work towards an equal payoff.")
##
##		elif (x == "2"):
##			mew.say("Here is the deal, Let's cooperate with each other.")
##
##		elif (x == "3"):
##			mew.say("We can do this by taking turns receiving the higher payout.")
##
##		elif (x == "4"):
##			mew.say("If you don't do your part, I will make you pay.")
##
##		elif (x == "5"):
##			mew.say("Let's take turns.")
##
##		elif (x == "6"):
##			mew.say("I get higher payoff each round.")
##
##		elif (x == "7"):
##			mew.say("Otherwise, I will make you pay in future rounds.")
##
##		elif (x == "8"):
##			mew.say("Otherwise, I will make you pay in future moves.")
##
##		elif (x == "9"):
##			mew.say("Let's cooperate with each other.")
##
##		elif (x == "10"):
##			mew.say("Excellent")
##
##		elif (x == "11"):
##			mew.say("That was selfish of you.")
##
##		elif (x == "12"):
##			mew.say("You have confused me.")
##
##		elif (x == "13"):
##			mew.say("That's what I had hoped for.")
##
##		elif (x == "14"):
##			mew.say("Fine.")
##
##		elif (x == "15"):
##			mew.say("You dupe! I deserved better than that. I am going to punish you.")
##
##		elif (x == "16"):
##			mew.say("Serves you right, jerk.")
##
##		elif (x == "17"):
##			mew.say("Why did you do that for?")
##
##		elif (x == "18"):
##			mew.say("Okay. I forgive you.")
##
##		elif (x == "19"):
##			mew.say("Good. That's fair")
##
##		elif (x == "20"):
##			mew.say("I am happy with this.")
##
##		elif (x == "21"):
##			mew.say("On second thought, I'll forgive you for now.")
##
##		elif (x == "22"):
##			mew.say("I have changed my mind.")
##
##		elif (x == "23"):
##			
##			mew.say("You betrayed me! I expected you to")
##			mew.say(data[1])
##			mew.say("...")
##
##		elif (x == "24"):
##			mew.say("That is nicer than I expected")
##
##		elif (x == "25"):
##			mew.say("You FOOL!  I trusted you to") 
##			mew.say(data[1])
##
##		elif (x == "26"):
##			mew.say("I'm going to teach you a lesson you will never forget.")
##
##		elif (x == "27"):
##			mew.say("Take that, jerk!")
##
##		elif (x == "28"):
##			mew.say("I will not cheat you if you don't cheat me.")
##
##		elif (x == "29"):
##			mew.say("It's my turn now.  You'll get a higher payout next time.")
##
##		elif (x == "30"):
##			mew.say("It's your turn to get a higher payout.")
##
##		elif (x == "31"):
##			mew.say("I'm just feeling things out.")
##
##		elif (x == "32"):
##			mew.say("I'm going into defense mode now.")
##
##		elif (x == "33"):
##			mew.say("We could both do better than this.")
##
##	sock.sendall("ready")
##
##    	print >>sys.stderr, 'received "%s"' % data
	
	
