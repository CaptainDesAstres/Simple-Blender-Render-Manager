#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task settings'''
import xml.etree.ElementTree as xmlMod
import os, uuid, subprocess, shlex, time, datetime, threading
from save import *
from usefullFunctions import *
from TaskList.FileInfo.FileInfo import *
from TaskList.TaskLog.TaskLog import *

class Task:
	'''class to manage task settings'''
	
	
	def __init__(self, path = None, scene = None, fileInfo = None, xml= None):
		'''initialize task object with default settings or saved settings'''
		self.running = False
		if xml is None:
			self.defaultInit( path, scene, fileInfo )
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self, path, scene, fileInfo):
		'''initialize Task object with default settings'''
		self.path = path
		self.scene = scene
		self.info = fileInfo
		self.uid = uuid.uuid4().hex
		self.log = None
		self.status = 'waiting'
#		self.status possible values:
#		waiting    > the task have been set and is waiting to be run
#		lock       > the task is protected against running
#		pendinglock> same thing for a task that already have been started
#		ready      > the task have been run once and task.log is set
#		running    > the task is running
#		pause      > the task have been started but is now waiting to be continued
#		ended      > the task have been totaly rendered
#		erased     > the task have been erased
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize Task object with savedd settings'''
		self.path = xml.get('path')
		self.scene = xml.get('scene')
		self.uid = xml.get('uid', uuid.uuid4().hex)
		self.status = xml.get('status')
		self.info = FileInfo(xml.find('fileInfo'))
		
		node = xml.find('log')
		if node is not None:
			self.log = TaskLog(xml = node)
		else:
			self.log = None
	
	
	
	
	
	def toXml(self):
		'''export task settings into xml syntaxed string'''
		xml = '<task path="'+XML.encode(self.path)+'" scene="'+str(self.scene)\
				+'" uid="'+self.uid+'" status="'+self.status+'" >\n'\
				+self.info.toXml()
		if self.log is not None:
			xml += self.log.toXml()
		xml += '</task>\n'
		return xml
		
	
	
	
	
	
	def menu(self, log, index, tasks, preferences):
		'''method to edit task settings'''
		log.menuIn('Task n°'+str(index))
		change = False
		started = self.log is not None
		
		if started:
			menu = '''
    Menu :
(TASK ALREADY STARTED : SOME OPTIONS IS NOT AVAILABLE!)
5- Change list row
6- Lock/Unlock task
7- Erase task
8- Copy task
9- See Rendering Log
0- Quit and save

'''
		else:
			menu = '''
    Menu :
1- Change scene
5- Change list row
6- Lock/Unlock task
7- Erase task
8- Copy task
0- Quit and save

'''
		
		while True:
			log.print()
			
			print('\n        Edit Task n°'+str(index)+' :')
			self.print()
			print(menu)
			
			
			choice= input('action : ').strip().lower()
			if choice in ['0', 'q', 'quit', 'cancel']:
				log.menuOut()
				return change
			elif choice == '1' and not started:
				
				self.scene = not self.scene
				if self.scene:
					log.write('  all scene of task n°'+str(index)+' will be rendered.')
				else:
					log.write('  only active scene of task n°'+str(index)+' will be rendered.')
				change = True
				
			elif choice == '5':
				
				confirm, select = tasks.move(log, [index])
				if confirm:
					change = True
					index = select[0]
				
			elif choice == '6':
				
				if self.status in ['ready', 'pause']:
					self.status = 'pendinglock'
					change = True
					log.write('Task n°'+str(index)+' locked')
				elif self.status == 'waiting':
					self.status = 'lock'
					change = True
					log.write('Task n°'+str(index)+' locked')
				elif self.status == 'pendinglock':
					self.status = 'pause'
					change = True
					log.write('Task n°'+str(index)+' unlocked')
				elif self.status == 'lock':
					self.status = 'waiting'
					change = True
					log.write('Task n°'+str(index)+' unlocked')
				else:
					log.error('Task n°'+str(index)+' is not lockable/unlockable')
				
				
			elif choice == '7':
				
				if tasks.remove(log, [index]):
					log.menuOut()
					log.write('Task n°'+str(index)+' removed')
					return True
				
			elif choice == '8':
				
				new = self.copy()
				new.status = 'waiting'
				new.log = None
				tasks.tasks.append(new)
				log.write('a copy of the task n°'+str(index)+' have been added at the bottom of the task list')
				change = True
				
			elif choice == '9' and started:
				self.log.menu(log, index)
			else:
				log.error('Unknow request!', False)
	
	
	
	
	
	def menuArchive(self, log, index, tasks):
		'''method to edit task settings'''
		log.menuIn('Archived Task n°'+str(index))
		change = False
		while True:
			log.print()
			
			print('\n        Task n°'+str(index)+' Log :')
			self.print()
			choice = input('''
    Menu :
1- See Rendering Log
2- Copy Task In Rendering List
3- Erase Archived Task
0- Quit and save


action : ''').strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				log.menuOut()
				return change
			elif choice == '1':
				self.log.menu(log, index)
			elif choice == '2':
				
				new = self.copy()
				new.status = 'waiting'
				new.log = None
				tasks.tasks.append(new)
				log.write('A copy of the archived task n°'+str(index)+' have been added at the bottom of the pending task list.')
				change = True
				
			elif choice == '3':
				conf = input('\n\nThe task gone be definitly erased. Confirm action (y) :').strip().lower()
				if conf in ['y', 'yes']:
					tasks.archive.pop(index)
					log.write('The archived task n°'+str(index)+' have been erased.')
					log.menuOut()
					return True
			else:
				log.error('Unknow request!', False)
	
	
	
	
	
	def print(self):
		'''A method to print task information'''
		print('\n\nStatus :        '+self.status)
		print('Path :          '+self.path)
		print('File Name :     '+self.path.split('/').pop())
		print('Scene :         '+str(self.scene))
		print('\n')
	
	
	
	
	
	def getRow(self):
		'''A method to get row to print task list'''
		name = self.path.split('/').pop()
		return columnLimit('  '+name, 25, 5)\
				+columnLimit('  '+str(self.scene), 25, 5)\
				+columnLimit('  '+self.status, 25, 5)
	
	
	
	
	
	def copy(self):
		xml = '<?xml version="1.0" encoding="UTF-8"?>\n'+self.toXml()
		xml = xmlMod.fromstring(xml)
		copy = Task(xml = xml)
		copy.uid = uuid.uuid4().hex
		return copy
	
	
	
	
	
	def printRunMenu(self, index, count, log):
		'''print current runninge state'''
		log.print()
		print('\n\nRun task n°'+str(index)+' of '+str(count)+' :\n\n')
		if self.log is not None:
			self.log.print()
		log.runPrint()
	
	
	
	
	
	def run(self, index, taskList, scriptPath, log, preferences):
		'''A method to execute the task'''
		log.menuIn('run Task '+str(index)+' from '+str(len(taskList.tasks)))
		
		if self.log is None:
			# task never have been run before
			self.log = TaskLog(pref = preferences, task = self)
			preferences.output.checkAndCreate(self, preferences, taskList)
		
		self.printRunMenu(index, len(taskList.tasks), log)
		
		metapreset = self.log.preset
		if type(metapreset) is Preset:
			if self.log.groups[0].remaining() > 0:
				versions = { metapreset.engine.version : '[default]' }
		else:
			versions = {}
			for group in self.log.groups:
				if group.remaining() > 0:
					if group.preset.engine.version in versions.keys():
						versions[group.preset.engine.version].append(group.name)
					else:
						versions[group.preset.engine.version] = [group.name]
		
		script = self.createTaskScript(scriptPath, preferences)
		
		results = ''
		try:
			l = threading.Thread(target = self.socketAcceptClient,
								args=(taskList, index, log))
			l.start()
			taskList.listenerThreads.append(l)
			
			sub = subprocess.Popen(\
						shlex.split(\
							preferences.blender.path+' -b "'+self.path+'" -P "'\
							+script+'"'),\
						stdout = subprocess.PIPE,\
						stdin = subprocess.PIPE,\
						stderr = subprocess.PIPE)
			taskList.renderingSubprocess.append(sub)
			
			result = sub.communicate()
			taskList.renderingSubprocess.remove(sub)
			results += result[0].decode()+result[1].decode()+'\n\n\n'
		except FileNotFoundError:
			log.write('\033[31mTask n°'+str(index)+' : Blender call error! Try to verify the path of blender!\033[0m')
		
		self.eraseTaskScript(script)
		
		log.menuOut()
		return True
	
	
	
	
	
	def socketAcceptClient(self, taskList, index, log):
		'''A method to manage client connexion when running'''
		client = taskList.socket.accept()[0]
		taskList.listenerSockets.append( 
										{
									'socket':client,
									'uid':self.uid
										} 
										)
		msg = ''
		while taskList.runningMode < taskList.STOP_NOW:
			msg += client.recv(1024).decode()
			if msg == '':
				time.sleep(1)
			elif msg == self.uid+' VersionEnded EOS':
				break
			else:
				msg = self.treatSocketMessage(msg, taskList, index, log)
		client.close()
	
	
	
	
	
	def treatSocketMessage(self, msg, taskList, index, log):
		'''a method to interpret socket message'''
		if msg[-4:] != ' EOS':
			return msg
		
		messages = msg.split(' EOS')
		messages.pop()
		
		for m in messages:
			# normally, the message is to confirm the rendering of a frame, it must follow this sytaxe:
			#uid action(group,frame,date,computingTime) EOS
			#fc9b9d6fd2af4e0fb3f09066f9902f90 ConfirmFrame(groupe1,15,10:09:2014:10:30:40,11111111111111) EOS
			uid = m[0:32]
			action = m[33:m.find('(')]
			info = m[46:-1]
			if uid == self.uid and action == 'debugMsg':
				log.write(info)
			elif uid == self.uid and action == 'ConfirmFrame':
				info = info.split(',')
				group = info[0]
				frame = int(info[1])
				computingTime = float(info[3])
				
				date = info[2].split(':')
				date = datetime.datetime(
							year = int(date[2]),
							month = int(date[1]),
							day = int(date[0]),
							hour = int(date[3]),
							minute = int(date[4]),
							second = int(date[5])
										)
				
				self.log.getGroup(group).confirmFrame(frame, date, computingTime)
				self.printRunMenu(index, len(taskList.tasks), log)
		
		if messages[-1] == self.uid+' VersionEnded':
			return messages[-1]+' EOS'
		else:
			return ''
	
	
	
	
	
	def createTaskScript(self, scriptPath, preferences):
		'''create a script for each blender versions to run the task'''
		
		script = '''#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
''\'module to manage metapreset''\'
import sys
sys.path.append("'''+scriptPath+'''")
import xml.etree.ElementTree as xmlMod
from Preferences.Preferences import *
from TaskList.RenderingTask.RenderingTask import *
from TaskList.Task import *

preferences = Preferences( xml = xmlMod.fromstring(''\''''+preferences.toXml(False)+'''''\') )
task = Task( xml = xmlMod.fromstring(''\'<?xml version="1.0" encoding="UTF-8"?>\n'''+self.toXml()+'''''\'))

RenderingTask(task, preferences)'''
		
		path = scriptPath+'/TaskList/RenderingTask/TaskScripts/'+self.uid+'.py'
		with open(path,'w') as taskScriptFile:
			taskScriptFile.write( script )
		
		return path
	
	
	
	
	
	def eraseTaskScript(self, path):
		'''erase Task Script files'''
		
		os.remove(path)
	
	
	
	
	
