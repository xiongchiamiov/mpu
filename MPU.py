#!/usr/bin/python

'''
MPU bot by James Pearson
licensed under the WTF license
'''

import sys
from time import strftime, sleep
import cPickle as pickle
import commands
import re
import irclib
import dirty_secrets


## Beginning Setup
# Connection information
network = 'irc.freenode.net'
port = 6667
password = dirty_secrets.password
name = '/msg MPU MPU-help'
owner = 'xiong_chiamiov'
users = {}
users['cabal'] = ('xiong_chiamiov',)

gagged = False

# Create an IRC object
irc = irclib.IRC()

## Methods
# a shortened way to send messages to the channel
def say(message):
	if(not gagged):
		server.privmsg(channel, message)
		sleep(1)

def help(command=None):
	if command=='mpu-help':
		say("If called by itself, MPU-help will list all available commands. Followed by another command, MPU-help will give more information on that command.")
		return True
	elif command=='wthru':
		say('Returns a response to the question, "Who the hell are you?".')
		return True
	elif command=='motivation':
		say("Gives a motivating quote from Kamina (Gurren Lagann).")
		return True
	elif command=='mpu-source':
		say("Gives the address of the Git repository of MPU's code.")
		return True
	elif command=='mpu-report':
		say("Will send whatever follows to "+owner+" in a PM, or log it if he's offline.")
		return True
	elif command=='mpu-kill':
		say("Disconnects MPU from "+network+".")
		return True
	elif command=='mpu-gag':
		say("Prevents MPU from speaking until ungagged.")
		return True
	elif command=='mpu-ungag':
		say("Allows MPU to speak again after being gagged.")
		return True
	elif command=='info':
		say("Gets information on a user.")
		say("Usage: 'info [username]' to list infos, 'info [username] [info1, info2...]' to get infos.")
		return True
	elif command=='infoset':
		say("Sets information about you.")
		say("Usage: infoset [info] [details]")
		return True
	elif command=='mpu-changelog':
		say("Tells what's been changed recently.  If given an argument, get all changes since then.")
		say('Example: mpu-changelog 2weeks, mpu-changelog "12 march"')
		return True
	elif command=='whatis':
		say("Let's you know what everyone's talking about.  Best used via pm.")
		say("Example: whatis foo, whatis set foo a common metasyntatic variable")
		return True
	else:
		say("Available commands: " + (' '.join(sorted(handleFlags.keys()))))
		say("Type 'MPU-help [command]' to get more info about command.")
		say("I also respond to PMs; just remember you don't need ! in front of the command.")
		return True

def wthru():
	say("MPU is owned by "+owner+" and responds to PMs just as well as channel flags (save the spam!)")
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

def kill(userFrom):
	if userFrom == owner:
		server.privmsg(owner, "I've been killed!")
		logFile = open('MPU.log', 'a')
		logFile.write(strftime("%Y-%m-%d %H:%M:%S")+" -- "+"Got killed!\n")
		server.disconnect()
		sys.exit()
	else:
		say("You can kill a man, but you can't kill an idea manifested in Python.")

def gag():
	global gagged
	gagged = True
	return True

def ungag():
	global gagged
	gagged = False
	return True

def info(command):
	global userData
	split = command.split()

	if (len(split)==0):
		handleFlags['mpu-help'](None, 'info')
		return True

	user = split[0]

	if (len(split)<2):
		output = "I have the following information on "+user+": "
		try:
			for info in sorted(userData[user].keys()):
				output += info+", "
			# trim off the extra comma at the end
			output = output[0:-2]
		except:
			pass
		say(output)
	else:
		output = "Here's your requested info on "+user+": "
		infos = split[1:]
		for info in infos:
			try:
				output += info+": "+userData[user][info]+", "
			except KeyError:
				output += info+": No info, "

		# trim off the extra comma at the end
		output = output[0:-2]

		say(output)
	return True

def infoset(userFrom, command):
	global userData
	global userDataFile
	split = command.split()
	info = split[0]
	try:
		data = ' '.join(split[1:])
	except:
		data = ''
	
	try:
		userData[userFrom][info] = data
	except:
		userData[userFrom] = {}
		userData[userFrom][info] = data
	
	# pickle userData
	pickleFile = open(userDataFile, 'w')
	pickle.dump(userData, pickleFile)
	pickleFile.close()

	say("Field "+info+" updated.")

def changelog(command):
	if command and re.match('^[\w\d "]+$', command):
		output = commands.getstatusoutput('git --no-pager log --pretty=format:%%s --since=%s' % command)
	else:
		output = commands.getstatusoutput('git --no-pager log --pretty=format:%s -1')
	if output[0] or (command and not re.match('^[\w\d "]+$', command)):
		help('mpu-changelog')
		return False
	else:
		for summary in output[1].split('\n'):
			say(summary)
	return True

def whatis(userFrom, command):
	# are we recording new information?
	if command[:4] == 'set ':
		return whatis_set(userFrom, command[4:])

	global jeeves

	if command in jeeves:
		say(command+": "+jeeves[command])
		return True
	else:
		say("I don't know nothin' 'bout "+command)
		return False

def whatis_set(userFrom, definition):
	global users
	global jeeves
	global files

	if userFrom in users['cabal']:
		command = definition.split()[0]
		definition = definition[len(command)+1:]

		if definition:
			jeeves[command] = definition
			say("New definition for "+command+" set.")
		else:
			del jeeves[command]
			say("Definition unset for "+command+".")

		# pickle jeeves
		pickleFile = open(files['jeeves'], 'w')
		pickle.dump(jeeves, pickleFile)
		pickleFile.close()

		return True
	else:
		say("I'm sorry, but I don't trust you.  Y'know, the darting eyes and all.")
		return False


## Handle Input
handleFlags = {
	'mpu-help':     lambda userFrom, command: help(command),
	'wthru':        lambda userFrom, command: wthru(),
	'motivation':   lambda userFrom, command: motivation(),
	'mpu-source':   lambda userFrom, command: source(),
	'mpu-report':   lambda userFrom, command: report(userFrom, command),
	'mpu-kill':     lambda userFrom, command: kill(userFrom),
	'mpu-gag':      lambda userFrom, command: gag(),
	'mpu-ungag':    lambda userFrom, command: ungag(),
	'info':         lambda userFrom, command: info(command),
	'infoset':	lambda userFrom, command: infoset(userFrom, command),
	'mpu-changelog':lambda userFrom, command: changelog(command),
	'whatis':	lambda userFrom, command: whatis(userFrom, command),
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
		handleFlags[flag.lower()](userFrom, ' '.join(command))
		channel = temp
	except KeyError:
		handleFlags['mpu-help'](userFrom, '')
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
			return handleFlags[flag[1:].lower()](userFrom, ' '.join(command))
		except KeyError:
			return True


## Final Setup
# Add handlers
irc.add_global_handler('privmsg', handlePrivateMessage)
irc.add_global_handler('pubmsg', handlePublicMessage)

# Jump into an infinite loop
while(True):
	try:
		# dictionary to group information about files we need
		files = {}

		# change some settings based on whether we're running the testing version or not
		if(sys.argv[0].find('testing')!=-1):
			userDataFile = 'userData_testing.pickle'
			files['jeeves'] = 'jeeves_testing.pickle'
			channel = '#mputesting'
			nick = 'MPU-testing'
			irclib.DEBUG = True
		else:
			userDataFile = 'userData.pickle'
			files['jeeves'] = 'jeeves.pickle'
			channel = '#cplug'
			nick = 'MPU'

		# load the pickled files
		try:
			pickleFile = open(userDataFile, 'r')
			userData = pickle.load(pickleFile)
		except:
			userData = {}
		try:
			pickleFile = open(files['jeeves'], 'r')
			jeeves = pickle.load(pickleFile)
			pickleFile.close()
		except:
			jeeves = {}
		
		# Create a server object, connect and join the channel
		server = irc.server()
		server.connect(network, port, nick, password=password, ircname=name)
		server.join(channel)

		irc.process_forever(timeout=10.0)
	except irclib.ServerNotConnectedError:
		sleep(5)
