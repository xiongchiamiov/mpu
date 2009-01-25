#!/usr/bin/python

import sys
import irclib
import dirty_secrets

# Connection information
network = 'irc.freenode.net'
port = 6667
password = dirty_secrets.password
name = 'try !wthru'
owner = 'xiong_chiamiov'

# change some settings based on whether we're running the testing version or not
if(sys.argv[0].find('testing')!=-1):
	channel = '#mputesting'
	nick = 'MPU-testing'
else:
	channel = '#cplug'
	nick = 'MPU'

# Create an IRC object
irc = irclib.IRC()

# Create a server object, connect and join the channel
server = irc.server()
server.connect(network, port, nick, password=password, ircname=name)
server.join(channel)

# a shortened way to send messages to the channel
def say(message):
	server.privmsg(channel, message)

# Forward private messages to me
def handlePrivateMessage(connection, event):
	userFrom = event.source().split('!')[0]
	userMessage = event.arguments()[0]
	server.privmsg(owner, userFrom+" said: "+userMessage)

# Take a look at public messages and see if we need to do anything with them
def handlePublicMessage(connection, event):
	userMessage = event.arguments()[0]

	if(userMessage[0]!='!'):
		return False

	#if(userMessage[1:]=='test'):
	#	server.privmsg(channel, "test worked")
	if(userMessage[1:]=='wthru'):
		say("MPU is owned by "+owner)
		say("ED: Who are you? Eh? What? What did you just say?")
		say("SATELLITE: Who, you? Here, always.")
		say("ED: Edward. A net diver from Earth.")
		say("SATELLITE: Earth?")
		say("ED: Yup, Hey, what's your name?")
		say("SATELLITE: I am the satellite control program on the D-135 artificial satellite.")
		say("ED: What's that? Don't you have a nickname? Then Ed will give you one. I know! Because you're a computer, you can be MPU! MPU! Cool name!")
		say("MPU: Um...")
	if(userMessage[1:]=='motivation'):
		say("Don't believe in yourself. Believe in me. Believe in me, who believes in you!")

# Add handlers
irc.add_global_handler('privmsg', handlePrivateMessage)
irc.add_global_handler('pubmsg', handlePublicMessage)

# Jump into an infinite loop
irc.process_forever()
