#!/usr/bin/python

'''
MPU bot by James Pearson
licensed under the WTF license
'''

import sys
from time import strftime, sleep
import irclib
import dirty_secrets


## Beginning Setup
# Connection information
network = 'irc.freenode.net'
port = 6667
password = dirty_secrets.password
name = 'try !wthru or !MPU-help'
owner = 'xiong_chiamiov'

# change some settings based on whether we're running the testing version or not
if(sys.argv[0].find('testing')!=-1):
	channel = '#mputesting'
	nick = 'MPU-testing'
	irclib.DEBUG = True
else:
	channel = '#cplug'
	nick = 'MPU'

gagged = False

# Create an IRC object
irc = irclib.IRC()

# Create a server object, connect and join the channel
server = irc.server()
server.connect(network, port, nick, password=password, ircname=name)
server.join(channel)

## Methods
# a shortened way to send messages to the channel
def say(message):
	if(not gagged):
		server.privmsg(channel, message)
		sleep(1)

def help(command=None):
	if(command=='MPU-help'):
		say("Type 'MPU-help [command]' to get more info about command.")
		say("If called by itself, MPU-help will list all available commands.")
		return True
	if(command=='wthru'):
		say('Returns a response to the question, "Who the hell are you?".')
		return True
	if(command=='motivation'):
		say("Gives a motivating quote from Kamina (Gurren Lagann).")
		return True
	if(command=='MPU-source'):
		say("Gives the address of the Git repository of MPU's code.")
		return True
	if(command=='MPU-report'):
		say("Will send whatever follows to "+owner+" in a PM, or log it if he's offline.")
		return True
	if(command=='MPU-kill'):
		say("Disconnects MPU from "+network+".")
		return True
	if(command=='MPU-gag'):
		say("Prevents MPU from speaking until ungagged.")
		return True
	if(command=='MPU-ungag'):
		say("Allows MPU to speak again after being gagged.")
		return True
	if(command=='info'):
		return True
	else:
		say("Available commands: " + (' '.join(sorted(handleFlags.keys()))))
		return True

def wthru():
	say("MPU is owned by "+owner)
	say("ED: Who are you? Eh? What? What did you just say?")
	say("SATELLITE: Who, you? Here, always.")
	say("ED: Edward. A net diver from Earth.")
	say("SATELLITE: Earth?")
	say("ED: Yup, Hey, what's your name?")
	say("SATELLITE: I am the satellite control program on the D-135 artificial satellite.")
	say("ED: What's that? Don't you have a nickname? Then Ed will give you one. I know! Because you're a computer, you can be MPU! MPU! Cool name!")
	say("MPU: Um...")

	return True

def motivation():
	return say("Don't believe in yourself. Believe in me. Believe in me, who believes in you!")

def source():
	return say("You can view my source at http://github.com/xiongchiamiov/mpu/ .")

def report(userFrom, message):
	# FIXME
	# some magic to determine if owner is online
	#if(True):
	#	server.privmsg(owner, userFrom+" has something to say: "+message)
	#	return True
	#else:
	#	# log it to a file
	#	logFile = open('MPU.log', 'a')
	#	return logFile.write(userFrom+" had something to say: "+message+"\n") and logFile.close()

	# temporary while I determine what magic to use above
	server.privmsg(owner, userFrom+" has something to say: "+message)
	logFile = open('MPU.log', 'a')
	return logFile.write(strftime("%Y-%m-%d %H:%M:%S")+" -- "+userFrom+" had something to say: "+message+"\n") and logFile.close()

def kill():
	server.privmsg(owner, "I've been killed!")
	logFile = open('MPU.log', 'a')
	logFile.write(strftime("%Y-%m-%d %H:%M:%S")+" -- "+"Got killed!\n")
	server.disconnect()

def gag():
	global gagged
	gagged = True
	return True

def ungag():
	global gagged
	gagged = False
	return True


## Handle Input
handleFlags = {
	'MPU-help':     lambda userFrom, command: help(command),
	'wthru':        lambda userFrom, command: wthru(),
	'motivation':   lambda userFrom, command: motivation(),
	'MPU-source':   lambda userFrom, command: source(),
	'MPU-report':   lambda userFrom, command: report(userFrom, command),
	'MPU-kill':     lambda userFrom, command: kill(),
	'MPU-gag':      lambda userFrom, command: gag(),
	'MPU-ungag':    lambda userFrom, command: ungag(),
	#'info':         lambda(userFrom, command): info(userFrom=userFrom, command=command),
}

# Treat PMs like public flags, except output is sent back in a PM to the user
def handlePrivateMessage(connection, event):
	# get the user the message came from
	userFrom = event.source().split('!')[0]
	# separate message into flag and rest
	try:
		splitMessage = event.arguments()[0].split()
		flag = splitMessage[0]
		command = splitMessage[1:]
	except:
		flag = even.arguments()[0]
		command = []
	
	# make say() send messages back in PMs
	global channel
	temp = channel
	channel = userFrom
	
	try:
		handleFlags[flag](userFrom, ' '.join(command))
		channel = temp
	except:
		handleFlags['MPU-help'](userFrom, '')
		channel = temp
	return True

# Take a look at public messages and see if we need to do anything with them
def handlePublicMessage(connection, event):
	# get the user the message came from
	userFrom = event.source().split('!')[0]
	# separate message into flag and rest
	try:
		splitMessage = event.arguments()[0].split()
		flag = splitMessage[0]
		command = splitMessage[1:]
	except:
		flag = event.arguments()[0]
		command = []

	if(flag[0]!='!'):
		return False
	else:
		try:
			return handleFlags[flag[1:]](userFrom, ' '.join(command))
		except:
			return True


## Final Setup
# Add handlers
irc.add_global_handler('privmsg', handlePrivateMessage)
irc.add_global_handler('pubmsg', handlePublicMessage)

# Jump into an infinite loop
irc.process_forever()
