#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''functions to save config file and queue file '''
import os, re


def savePreferences(s):
	'''Save preferences file'''
	with open(os.getcwd()+'/preferences','w') as prefFile:
		prefFile.write(s.toXml())

def saveTasks(output, t):
	'''Save Tasks file'''
	with open(output+'Tasks','w') as tasksFile:
		tasksFile.write(t.toXml())

def eraseLockFile():
	'''Erase lock file'''
	os.remove(os.getcwd()+'/lock')

def checkLogLimit(limit):
	'''limit the session log number'''
	# get log file list
	content = os.listdir(os.getcwd()+'/log/')
	
	if len(content) > limit:
		
		# link log to timestamp computed from creation date
		logRegex = re.compile(r'^session (\d{2})\.(\d{2})\.(\d{4})-(\d{2}):(\d{2}):(\d{2})\.log$')
		logs = {}
		for f in content:
			match = logRegex.match(f)
			if match is not None:
				timestamp = int(match.group(3))*12+int(match.group(2)) # month
				timestamp = timestamp*31+int(match.group(1)) # days (approximation)
				timestamp = timestamp*24+int(match.group(4)) # hour
				timestamp = timestamp*60+int(match.group(5)) # minute
				timestamp = timestamp*60+int(match.group(6)) # second
				
				logs[timestamp] = f
		
		# erase oldest log(s) until it's match the limit settings
		keys = list(logs.keys())
		keys.sort()
		while len(logs) > limit:
			k = keys.pop(0)
			f = logs.pop(k)
			os.remove(os.getcwd()+'/log/'+f)




