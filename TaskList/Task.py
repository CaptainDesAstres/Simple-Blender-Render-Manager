#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task settings'''
import xml.etree.ElementTree as xmlMod
import os, uuid, subprocess, shlex, time, datetime, threading, shutil
from usefullFunctions import *
from TaskList.FileInfo.FileInfo import *
from TaskList.TaskLog.TaskLog import *

class Task:
	'''class to manage task settings'''
	
	
	def __init__(self, path = None, scene = None, percentOW = None, fileInfo = None, xml= None):
		'''load task settings'''
		self.log = None # task rendering log
		
		if xml is None:
			self.defaultInit( path, scene, percentOW, fileInfo )
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self, path, scene, percentOW, fileInfo):
		'''load new Task settings'''
		self.path = path # path to the original blender file
		
		# task name
		self.name = path.split('/').pop().split('.')
		self.name.pop()
		self.name = '.'.join(self.name)
		
		self.scene = scene # False = render only active scene, True = render all scene
		self.percentOW = percentOW # OverWrite file resolution pourcent setting if True
		self.info = fileInfo # FileInfo object, contain blender file information
		self.uid = uuid.uuid4().hex # unique ident
		self.status = 'waiting'
#		self.status possible values:
#		waiting    > the task have been set and is waiting to be run
#		lock       > the task is protected against running
#		pendinglock> same thing for a task that already have been started
#		ready      > the task have been run once and task.log is set
#		running    > the task is running
#		pause      > the task have been started but is now waiting to be continued
#		ended      > the task have been totaly rendered
	
	
	
	
	
	def fromXml(self, xml):
		'''Load Task settings from xml'''
		self.path = XML.decode(xml.get('path'))
		self.name = XML.decode(xml.get('name'))
		self.scene = (xml.get('scene') == 'True' )
		self.percentOW = (xml.get('percentOW') == 'True' )
		self.uid = xml.get('uid', uuid.uuid4().hex)
		self.status = xml.get('status')
		self.info = FileInfo( xml.find('fileInfo') )
		
		node = xml.find('log')
		if node is not None:
			self.log = TaskLog(xml = node)
	
	
	
	
	
	def toXml(self):
		'''export in xml'''
		xml = '<task name="'+XML.encode(self.name)+'" path="'+XML.encode(self.path)\
				+'" scene="'+str(self.scene)\
				+'" uid="'+self.uid+'" status="'+self.status+'" percentOW="'+str(self.percentOW)+'" >\n'\
				+self.info.toXml()
		
		# export rendering task log
		if self.log is not None:
			xml += self.log.toXml()
		
		xml += '</task>\n'
		return xml
		
	
	
	
	
	
	def menu(self, log, index, tasks, preferences):
		'''edit task settings'''
		log.menuIn('Task n°'+str(index))
		change = False
		started = self.log is not None
		
		if started: # menu if task rendering started
			menu = '''
    Menu :
(TASK ALREADY STARTED : SOME OPTIONS IS NOT AVAILABLE!)
3- Change list row
4- Lock/Unlock task
5- Erase task
6- Copy task
9- See Rendering Log
0- Quit and save

'''
		else: # menu if task rendering never started
			menu = '''
    Menu :
1- Switch render All/Active scene(s)
2- Switch force 100% resolution
3- Change list row
4- Lock/Unlock task
5- Erase task
6- Copy task
0- Quit and save

'''
		
		while True:
			log.print()
			print('\n        Edit Task n°'+str(index)+' :')
			self.print()
			# get user menu choice
			choice= input(menu+'\nAction ? ').strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				# confirm edit and quit
				log.menuOut()
				return change
				
			elif choice == '1' and not started:
				# switch scene settings
				self.scene = not self.scene
				# repport change in log
				if self.scene:
					log.write('  all scene of task n°'+str(index)+' will be rendered.')
				else:
					log.write('  only active scene of task n°'+str(index)+' will be rendered.')
				change = True
				
			elif choice == '2' and not started:
				# switch resolution percentage overwrite setting settings
				self.percentOW = not self.percentOW
				# repport change in log
				if self.percentOW:
					log.write('  task n°'+str(index)+' will be rendered with 100% resolution settings.')
				else:
					log.write('  task n°'+str(index)+' will be rendered with file resolution percentage settings.')
				change = True
				
			elif choice == '3':
				# move task
				confirm, select = tasks.move(log, [index])
				if confirm:
					change = True
					index = select[0]
				
			elif choice == '4':
				# switch to lock/unlock the task
				if self.status == 'started':
					self.status = 'pendinglock'
					change = True
					log.write('Task n°'+str(index)+' locked')
					
				elif self.status == 'waiting':
					self.status = 'lock'
					change = True
					log.write('Task n°'+str(index)+' locked')
					
				elif self.status == 'pendinglock':
					self.status = 'started'
					change = True
					log.write('Task n°'+str(index)+' unlocked')
					
				elif self.status == 'lock':
					self.status = 'waiting'
					change = True
					log.write('Task n°'+str(index)+' unlocked')
					
				else:
					log.error('Task n°'+str(index)+' is not lockable/unlockable')
				
				
			elif choice == '5':
				# delete task
				if tasks.remove(preferences, log, [index]):
					log.menuOut()
					log.write('Task n°'+str(index)+' removed')
					return True
				
			elif choice == '6':
				# made a copy of the task
				if os.path.exists(preferences.output.path+'source/'+self.name+'.blend'):
					tasks.tasks.append(self.copy(tasks, preferences, False))
					# repport in log
					log.write('The task n°'+str(index)\
						+' have been copied and added to the list')
					change = True
				else:
					log.error('Unable to copy of the pending task n°'+str(index)\
						+': can\'t find the source blender file in the working directory.')
				
			elif choice == '9' and started:
				# access the rendering log
				self.log.menu(log, index)
				
			else:
				log.error('Unknow request!', False)
	
	
	
	
	
	def menuArchive(self, log, index, tasks, preferences):
		'''Display task archived menu'''
		log.menuIn('Archived Task n°'+str(index))
		change = False
		
		while True:
			log.print()
			print('\n        Task n°'+str(index)+' Log :')
			self.print()
			
			# display menu and get user choice
			choice = input('''
    Menu :
1- See Rendering Log
2- Copy Task In Rendering List
3- Erase Archived Task
0- Quit and save


action : ''').strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				# Quit menu (return to archive list menu)
				log.menuOut()
				return change
			
			if choice == '1':
				# Display task rendering log
				self.log.menu(log, index)
				
			elif choice == '2':
				# check source file exists
				if os.path.exists(preferences.output.path+'render/'\
						+self.name+'/'+self.name+'.blend'):
					# create a new rendering task, copy of this one
					tasks.tasks.append(self.copy(tasks, preferences, True))
					log.write('A copy of the archived task n°'+str(index)\
						+' have been added at the bottom of the pending task list.')
					change = True
				else:
					log.error('Unable to copy of the archived task n°'+str(index)\
						+': can\'t find the archived blender file.')
				
			elif choice == '3':
				# erase task archive after confirmation
				if input('\n\nThe task gone be definitly erased. Confirm action (y) :').strip().lower() in ['y', 'yes']:
					tasks.archive.pop(index)
					log.write('The archived task n°'+str(index)+' have been erased.')
					log.menuOut()
					return True
				
			else:
				log.error('Unknow request!', False)
	
	
	
	
	
	def print(self):
		'''Display task information'''
		print('\n\nStatus :                 ' + self.status\
				+'\nOriginal file path :     ' + self.path\
				+'\nName :                   ' + self.name\
				+'\nRender All Scene :       ' + str(self.scene)\
				+'\n100% Resolution :        ' + str(self.percentOW) + '\n'
				)
	
	
	
	
	
	def getRow(self):
		'''return task row to display in a table'''
		return columnLimit('  '+self.name, 25, 5)\
				+columnLimit('  '+str(self.scene), 19, 5)\
				+columnLimit('  '+str(self.percentOW), 13, 5)\
				+columnLimit('  '+self.status, 13, 5)
	
	
	
	
	
	def copy(self, tasks, preferences, archived):
		'''Return a full copy of self'''
		# create the copy
		xml = '<?xml version="1.0" encoding="UTF-8"?>\n'+self.toXml()
		xml = xmlMod.fromstring(xml)
		copy = Task(xml = xml)
		
		# init copy path, name, uid, status and log
		copy.uid = uuid.uuid4().hex
		copy.status = 'waiting'
		copy.log = None
		if archived:
			copy.path = preferences.output.path+'render/'+self.name+'/'+self.name+'.blend'
		else:
			copy.path = preferences.output.path+'source/'+self.name+'.blend'
		copy.name = tasks.getUnusedTaskName( copy.name, preferences )
		
		#copy original file
		shutil.copy(\
				copy.path,\
				preferences.output.path+'source/'+copy.name+'.blend'\
					)
		
		return copy
	
	
	
	
	
	def printRunMenu(self, index, count, log):
		'''display run state'''
		log.print()
		print('\n\nRun task n°'+str(index)+' of '+str(count)+' :\n\n')
		if self.log is not None:
			self.log.print()
		log.runPrint()
	
	
	
	
	
	def run(self, taskList, scriptPath, log, preferences):
		'''Render the task'''
		index = taskList.current
		log.menuIn('run Task '+str(index)+' from '+str(len(taskList.tasks)))
		
		# create task log on first running
		if self.log is None:
			self.log = TaskLog(task = self)
		self.status = 'started'
		
		# ensure we can write in working directory
		if not self.checkOutput(preferences):
			log.error('You need permission to write in task output path!')
			log.menuOut()
			return True
		
		# refresh displaying
		self.printRunMenu(index, len(taskList.tasks), log)
		
		# create script for blender
		script = self.createTaskScript(scriptPath, preferences)
		
		#results = ''
		try:
			# create a socket listener dedicated to the task blender thread
			l = threading.Thread(target = self.socketAcceptClient,
								args=(taskList, index, log))
			l.start()
			taskList.listenerThreads.append(l)
			
			# create and launch the task blender thread 
			path = preferences.output.path+'source/'+self.name+'.blend'
			sub = subprocess.Popen(\
						shlex.split(\
							'\''+preferences.blender.path+'\' -b "'+path+'" -P "'\
							+script+'"'),\
						stdout = subprocess.PIPE,\
						stdin = subprocess.PIPE,\
						stderr = subprocess.PIPE)
			taskList.renderingSubprocess.append(sub)
			
			# get blender thread terminal output
			result = sub.communicate()
			#results += result[0].decode()+result[1].decode()+'\n\n\n'
			
			# remove dead blender thread
			taskList.renderingSubprocess.remove(sub)
			
		except FileNotFoundError:
			# log and display all blender error
			log.write('\033[31mTask n°'+str(index)+' : Blender call error! Try to verify the path of blender!\033[0m')
		
		# erase dedicated task script
		os.remove(script)
		
		#log.write('###\n'+results+'###\n')# debuging output
		
		log.menuOut()
		return True
	
	
	
	
	
	def socketAcceptClient(self, taskList, index, log):
		'''manage blender new connexion'''
		# add new client connexion
		client = taskList.socket.accept()[0]
		taskList.listenerSockets.append( 
										{
									'socket':client,
									'uid':self.uid
										} 
										)
		
		msg = ''
		while taskList.runningMode < taskList.STOP_NOW:# while running mode continue
			msg += client.recv(1024).decode()
			
			if msg == '' or msg[-4:] != ' EOS':
				time.sleep(1)
				continue
			
			# split messages
			messages = msg.split(' EOS')
			messages.pop()# pop empty last element
			
			for m in messages:
				if m != self.uid+' TaskEnded':# treat all other kind of signal
					self.treatSocketMessage(m, taskList, index, log)
				else:
					# when task finished, close listener and erase from listener list
					client.close()
					for l in taskList.listenerSockets:
						if l['uid'] == self.uid:
							taskList.listenerSockets.remove(l)
							return
			
			msg = ''# initialize for new message
	
	
	
	
	
	def treatSocketMessage(self, msg, taskList, index, log):
		'''treat all blender socket message'''
		# normally, the message is to confirm the rendering of a frame, it must follow this sytaxe:
		#uid action(group,frame,date,computingTime) EOS
		#fc9b9d6fd2af4e0fb3f09066f9902f90 ConfirmFrame(groupe1,15,10:09:2014:10:30:40,11111111111111) EOS
		
		# parse message info
		uid = msg[0:32]
		action = msg[33:msg.find('(')]
		info = msg[46:-1]
		
		if uid == self.uid and action == 'debugMsg':# display debuging messages
			log.write( msg[msg.find('(')+1 : -1] )
			
		elif uid == self.uid and action == 'ConfirmFrame':
			# confirm a frame rendering
			#get frame info
			info = info.split(',')
			scene = info[0]
			frame = int(info[1])
			computingTime = float(info[3])
			
			# get rendering datetime
			date = info[2].split(':')
			date = datetime.datetime(
						year = int(date[2]),
						month = int(date[1]),
						day = int(date[0]),
						hour = int(date[3]),
						minute = int(date[4]),
						second = int(date[5])
									)
			
			# log the frame as finished in the corresponding scene log
			for s in self.log.scenes:
				if s.name == scene:
					s.confirmFrame(frame, date, computingTime)
			
			# refresh displaying
			self.printRunMenu(index, len(taskList.tasks), log)
		
	
	
	
	
	
	def checkOutput(self, pref):
		'''create output path if needed'''
		path = pref.output.path+'render/'+self.name+'/'
		
		scenes = self.log.scenes
		for s in scenes:
			p = path+s.name+'/'
			
			# creat output directory for each scene of the task
			if not os.path.exists(p):
				os.makedirs(p)
			
			# Ensure to have writing access permission
			if not os.access( p, os.W_OK ):
				return False
		
		return True
	
	
	
	
	
	def createTaskScript(self, scriptPath, preferences):
		'''create a blender script file customize for the task'''
		# script custom content
		script = '''#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
''\'module to manage metapreset''\'
import sys
sys.path.append("'''+scriptPath+'''")
import xml.etree.ElementTree as xmlMod
from Preferences.Preferences import *
from TaskList.RenderingTask.RenderingTask import *
from TaskList.Task import *

preferences = Preferences( xml = xmlMod.fromstring(''\''''+preferences.toXml()+'''''\') )
task = Task( xml = xmlMod.fromstring(''\'<?xml version="1.0" encoding="UTF-8"?>
'''+self.toXml()+'''''\'))

RenderingTask(task, preferences)'''
		
		# save script in a file
		path = scriptPath+'/TaskList/RenderingTask/TaskScripts/'+self.uid+'.py'
		with open(path,'w') as taskScriptFile:
			taskScriptFile.write( script )
		
		# return custom script path
		return path
	
	
	
	
	
