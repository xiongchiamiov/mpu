#!/usr/bin/python

import sys
import irclib
import dirty_secrets

# Connection information
network = 'irc.freenode.net'
port = 6667
password = dirty_secrets.password
name = '!wthru'
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
		server.privmsg(channel, "MPU is owned by "+owner)
		server.privmsg(channel, "ED: Who are you? Eh? What? What did you just say?")
		server.privmsg(channel, "SATELLITE: Who, you? Here, always.")
		server.privmsg(channel, "ED: Edward. A net diver from Earth.")
		server.privmsg(channel, "SATELLITE: Earth?")
		server.privmsg(channel, "ED: Yup, Hey, what's your name?")
		server.privmsg(channel, "SATELLITE: I am the satellite control program on the D-135 artificial satellite.")
		server.privmsg(channel, "ED: What's that? Don't you have a nickname? Then Ed will give you one. I know! Because you're a computer, you can be MPU! MPU! Cool name!")
		server.privmsg(channel, "MPU: Um...")

# Add handlers
irc.add_global_handler('privmsg', handlePrivateMessage)
irc.add_global_handler('pubmsg', handlePublicMessage)

# Jump into an infinite loop
irc.process_forever()
