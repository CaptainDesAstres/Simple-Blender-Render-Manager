#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task list'''
import xml.etree.ElementTree as xmlMod
import os, re, math, threading, socket, time
from usefullFunctions import *
from save import *
from TaskList.Task import *
from TaskList.FileInfo.FileInfo import *

class TaskList:
	'''class to manage task list'''
	
	# constante value for runningMode
	OFF = 0 # not running
	UNTIL_LIST_END = 1 # running until all task have been rendered
	UNTIL_FRAME_END = 2 # running until end of rendering of the current frame
	UNTIL_SCENE_END = 3 # running until end of rendering of the current group
	UNTIL_TASK_END = 4 # running until end of rendering of the current task
	STOP_NOW = 5 # stop as soon as possible
	STOP_FORCED = 6 # stop by forcing blender to stop
	
	def __init__(self, xml= None):
		'''load task list'''
		self.status = 'stop' # Blender-Render-Manager status: stop or run
		self.current = None # current running task in running mode
		self.runningMode = self.OFF # running mode (see constant values)
		self.socket = None # socket to communicate with blender in running mode
		self.listenerThreads = None # same thing
		self.listenerSockets = None # same thing
		self.renderingSubprocess = None # contain blender subprocess in running mode
		
		self.tasks = [] # pending task list
		self.archive = [] # archived task list
		
		if xml is not None:
			self.fromXml(xml)
	
	
	
	
	
	def __del__(self):
		'''Erase lock file in case of crash'''
		eraseLockFile()
		if self.socket is not None:
			self.socket.close()
	
	
	
	
	
	def fromXml(self, xml):
		'''load pending and archived task list from xml'''
		for node in xml.find('tasks').findall('task'):
			self.tasks.append(Task(xml = node))
		
		for node in xml.find('archive').findall('task'):
			self.archive.append(Task(xml = node))
	
	
	
	
	
	def toXml(self):
		'''export task list into xml syntaxed string'''
		xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
		xml += '<tasklist>\n'
		
		xml += '<tasks>\n'
		for task in self.tasks:
			xml += task.toXml()
		xml += '</tasks>\n'
		
		xml += '<archive>\n'
		for task in self.archive:
			xml += task.toXml()
		xml += '</archive>\n'
		
		xml += '</tasklist>\n'
		return xml
	
	
	
	
	
	def menu(self, scriptPath, log, preferences):
		'''display Blender-Render-Manager main menu'''
		log.menuIn('Task List')
		page = 0
		
		while True:
			log.print()
			self.print(page)
			choice= input('action ? (h for help):').strip().lower()
			
			if choice in ['q', 'quit']:# quit Blender-Render-Manager
				log.menuOut()
				return
				
			elif choice in ['p', 'pref', 'preferences']:
				preferences.menu(log, self)# access preferences menu
				
			elif choice in ['r', 'run']:# Start task rendering
				self.run(scriptPath, log, preferences)
				saveTasks(preferences.output.path, self)
				
			elif choice in ['a', 'add', '+'] \
					and self.add(log, preferences):# add task to the list
				saveTasks( preferences.output.path, self )
				
			elif choice in ['d', '>', '']:# display next task page
				if page < math.floor((len(self.tasks)-1)/25):
					page += 1
					
				elif choice == '':
					page = 0
				
			elif choice in ['u', '<'] and page > 0:# display previous task page
				page -= 1
				
			elif choice in ['b', 'batch'] \
					and self.batchEdit(log, preferences):# edit task by batch
				self.save(preferences.output.path)
				
			elif choice in ['l', 'log']:# display archived task
				self.menuArchive(log)
				
			elif choice in ['h', 'help']:# display menu help
				log.menuIn('Help')
				log.print()
				
				input('''\n\n        \033[4mHELP :\033[0m

Scroll up the list : u or <
Scroll down the list : d or > or just type enter

Add task : a or add or +
Edit/inspect a task : type the index of the task
Batch editing : b or batch
Render tasks : r or run
See archived rendered task : l or log

Preferences access : p or pref or preferences
Help : h or help
Quit : q or quit


Press enter to continue''')
				log.menuOut()
				
			else:
				# determine targeted task
				try:
					choice = int(choice)
				except:
					log.error('Unknow request!', False)
					continue
				
				if choice < 0 or choice >= len(self.tasks):
					log.error('There is no task n°'+str(choice)+'!', False)
					continue
				
				# edit selected task
				if(self.tasks[choice].menu(log, choice, self, preferences)):
					self.save(preferences.output.path)
	
	
	
	
	
	def menuArchive(self, log):
		'''Archive managing menu'''
		log.menuIn('Archived Task List')
		page = 0
		
		while True:
			log.print()
			
			self.print(page, archive = True)
			
			choice= input('action (h for help):').strip().lower()
			if choice in ['q', 'quit']:
				log.menuOut()
				return
			
			if choice in ['d', '>', '']:
				if page < math.floor((len(self.archive)-1)/25):
					page += 1
				elif choice == '':
					page = 0
			elif choice in ['u', '<']:
				if page > 0:
					page -= 1
			elif choice in ['h', 'help']:
				log.menuIn('Help')
				log.print()
				
				print('''\n\n        \033[4mHELP :\033[0m

Scroll up the list : u or <
Scroll down the list : d or > or just type enter

Edit/inspect a task : type the index of the task

Help : h or help
Quit : q or quit

''')
				
				input('Press enter to continue')
				log.menuOut()
			else:
				try:
					choice = int(choice)
				except:
					log.error('Unknow request!', False)
					continue
				
				if choice < 0 or choice >= len(self.archive):
					log.error('There is no archived task n°'+str(choice)+'!', False)
					continue
				
				if(self.archive[choice].menuArchive(log, choice, self)):
					self.save(preferences.output.path)
	
	
	
	
	
	def print(self, page, selection = None, whole = False, archive = False):
		'''Display pending or selected or archived task list'''
		Psize = 25 # task by page
		
		# print page header
		print('''
\033[4mID |  File Name              |  Rendering All Scene?   |  Status                 |\033[0m''')
		if page > 0:
			print('▲▲▲|▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲|▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲|▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲|')
		
		if archive:# get archived task to display
			selected = self.archive[page*Psize:(page+1)*Psize]
			index = list(range(page*Psize, (page+1)*Psize))
		elif selection is None or whole:# get pending task to display
			selected = self.tasks[page*Psize:(page+1)*Psize]
			index = list(range(page*Psize, (page+1)*Psize))
		else:# get selected pending task to display
			selection.sort()
			index = selection
			selected = []
			for i in index:
				selected.append(self.tasks[i])
		
		
		for i,task in enumerate(selected):
			# get and print row content to display
			row = columnLimit( index[i], 3, 0)
			row += task.getRow()
			if whole and index[i] in selection:
				row = '\033[7m'+row+'\033[0m' # colorize selected task
			print(row)
		
		# print footer
		if selection is not None and (page+1)*Psize <= len(selected)\
			or selection is None and (\
					( not archive and (page+1)*Psize <= len(self.tasks) )\
										or\
					( archive and (page+1)*Psize <= len(self.archive) )\
										):
			print('▼▼▼|▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼|▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼|▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼|')
	
	
	
	
	
	def add(self, log, preferences):
		'''Add task to the list'''
		log.menuIn('Add Task')
		log.menuIn('File Path')
		
		while True:
			# get path to the new file
			log.print()
			path = input("\n\n        Add File :\n\n\nWhat's the absolute path of the file to add (empty input to quit)").strip()
			
			if path.lower() in ['', 'cancel', 'quit', 'q']:
				# quit without adding any task
				log.menuOut()
				log.menuOut()
				return False
			
			# remove quote mark and apostrophe in first and last character
			if path[0] in ['\'', '"'] and path[-1] == path[0]:
				path = path[1:len(path)-1]
			
			# check if path is absolute (begin by '/')
			if path[0] != '/':
				log.error('"'+path+'" path is not absolute (need to begin by "/").')
				continue
			
			# check if the file exist
			if not os.path.exists(path) \
					or not os.path.isfile(path) \
					or not os.access(path, os.R_OK):
				log.error('"'+path+'" didn\'t exist, is not a file or is not readable!')
				continue
			
			# check if path point to a .blend file
			if len(path) < 7 or re.search(r'.blend\d{0,10}$', path) is None:
				log.error('"'+path+'" path don\'t seemed to be a blender file (need .blend extension).')
				continue
			
			# accept path
			log.menuOut()
			break
		
		# open the file and get settings
		log.write('Try to add "'+path+'" task:')
		
		# try to open file and get infos
		command = '("'+preferences.blender.path\
						+'" -b "'+path+'" -P "'\
						+os.path.realpath(__file__+'/..')+'/getter/getFileTaskInfos.py")'\
						+' || echo \'BlenderVersionError\' '
		info = os.popen(command).read()
		
		if info.count('BlenderVersionError') != 0:
			log.error('Blender version call error! Try to verified the path of default blender version!', False)
			log.menuOut()
			log.write('  Blender Version Error : abort task adding')
			return False
		#print(info)# print debug info
		info = re.search(r'<\?xml(.|\n)*</fileInfo>',info).group(0)
		info = xmlMod.fromstring(info)
		info = FileInfo(info)
		
		# scene choice
		scene = info.sceneChoice(log)
		if scene is None:
			log.menuOut()
			return False
		
		
		# add the task
		self.tasks.append( Task(
							path = path,
							scene = scene,
							fileInfo = info
							) )
		log.write('  Task added')
		
		log.menuOut()
		return True
	
	
	
	
	
	def save(self, output):
		'''A method to save Tasks list'''
		saveTasks(output, self)
		
	
	
	
	
	
	def remove(self, log, selected):
		'''A method to remove task from the list'''
		log.menuIn('Task(s) Removing')
		log.print()
		print('\n\n        Removing Selected Task :\n')
		self.print(0, selected)
		
		confirm = input('Do you realy want to erase this task?(y) ').strip().lower()
		
		log.menuOut()
		if confirm == 'y':
			selected.sort(reverse = True)
			for i in selected:
				self.tasks.pop(i)
			return True
		else:
			return False
	
	
	
	
	
	def move(self, log, selected):
		'''A method to move tasks into the list'''
		log.menuIn('Task(s) Moving')
		change = False
		selected.sort()
		
		while True:
			log.print()
			print('\n\n        Moving Selected Task :\n')
			self.print(0, selected, True)
			
			choice = input('how to move selected task : (h for help) ').strip().lower()
			
			if choice in ['', 'q', 'quit', 'cancel']:
				log.menuOut()
				return change, selected
			elif choice in ['h', 'help']:
				log.menuIn('Help')
				log.print()
				input('''

        Help :

Move to
    Top of list :          t or top
    First selected task :  f or first
    Last selected task :   l or last
    Bottom of the list :   b or bottom
    Give row position :    Type the number of the row you want
Reverse order (if the task is not contiguous, they will be regroup after the first selected)
                           i or inverse or r or reverse
Save and quit :            empty string or q or quit or cancel
Help :                     h or help

Press enter to continue
''')
			elif re.search(r'^(t|f|l|b|(top)|(first)|(last)|(bottom)|(r)|(i)|(reverse)|(inverse)|(\d+))$', choice):
				reverse = choice in ['r', 'i', 'inverse', 'reverse']
				if choice in ['t', 'top']:
					choice = -1
				elif reverse or choice in ['f', 'first']:
					choice = selected[0]
				elif choice in ['l', 'last']:
					choice = selected[-1]
				elif choice in ['b', 'bottom']:
					choice = len(self.tasks)
				else:
					
					try:
						choice = int(choice)
					except ValueError:
						log.error('Unvalid action', False)
						continue
				
				selected = self.moveTo(log, selected, choice)
				
				if reverse:
					reorder = self.tasks[selected[0]: selected[-1]+1]
					reorder.reverse()
					self.tasks = self.tasks[0: selected[0] ] + reorder \
								+self.tasks[selected[-1]+1:]
				
				# correct task index in menu
				log.menuOut()
				log.menuOut()
				log.menuIn('Task n°'+','.join(str(x) for x in selected))
				log.menuIn('Task(s) Moving')
				
				change = True
			else:
				log.error('Unvalid action', False)
	
	
	
	
	
	def moveTo(self, log, selected, row):
		'''A method to move selected task to a position in the list'''
		selected.sort()
		isRange = selected == list(range(selected[0], selected[-1]+1))
		selected.reverse()
		selection = []
		
		for index in selected:
			selection.append(self.tasks.pop(index))
			if not isRange and row > index:
				row -= 1
		selection.reverse()
		
		if row <= 0:
			self.tasks = selection + self.tasks
			log.write('Task n°«'+','.join(str(x) for x in selected)+'» moved on top of the list')
			selected = list(range(0, len(selected)))
		elif row >= len(selection) + len(self.tasks):
			self.tasks += selection
			log.write('Task n°«'+','.join(str(x) for x in selected)+'» moved on bottom of the list')
			selected = list(range(len(self.tasks)-len(selected) , len(self.tasks)))
		else:
			self.tasks = self.tasks[0:row]+selection+self.tasks[row:]
			log.write('Task n°«'+','.join(str(x) for x in selected)+'» moved on row '+str(row)+' of the list')
			selected = list(range(row, row + len(selected)))
		
		return selected
	
	
	
	
	
	def batchEdit(self, log, preferences):
		'''A method to batch edit task'''
		log.menuIn('Batch Editing')
		select = self.batchSelect(log)
		if len(select) == 0 :
			log.menuOut()
			return False
		
		log.menuIn('Task n°'+','.join(str(x) for x in select))
		change = False
		while True:
			log.print()
			print('\n\n        Batch Edit :\n')
			
			self.print(0, select)
			choice = input('''\nMenu :
2- Copy
3- Regroup And Move
4- Remove
5- Lock
6- Unlock
9- Change Selection
0- Quit
''')
			
			if choice in ['q', 'quit', 'cancel', '0']:
				log.menuOut()
				log.menuOut()
				return change
			elif choice == '2':
				new, confirm = self.copyTasks(log, select, preferences)
				if confirm:
					select = new
					change = True
			elif choice == '3':
				change = (self.move(log, select) or change)
			elif choice == '4':
				if self.remove(log, select):
					log.menuOut()
					log.menuOut()
					return True
			elif choice == '5':
				self.lock(select, log)
				change = True
			elif choice == '6':
				self.unlock(select, log)
				change = True
			elif choice == '9':
				log.menuOut()
				select = self.batchSelect(log, select)
				log.menuIn('Task n°'+','.join(str(x) for x in select))
			else:
				log.error('Unvalid request',False)
	
	
	
	
	
	def lock(self, select, log):
		'''a method to batch lock task'''
		modified = []
		unmodified = []
		for i in select:
			task = self.tasks[i]
			if task.status in ['ready', 'pause']:
				task.status = 'pendinglock'
				modified.append(i)
			elif task.status == 'waiting':
				task.status = 'lock'
				modified.append(i)
			else:
				unmodified.append(i)
		
		if len(modified)>0:
			log.write('Task n°«'+','.join(str(x) for x in modified)+'» have been locked.')
		if len(unmodified)>0:
			log.write('Task n°«'+','.join(str(x) for x in unmodified)+'» were already lock or unlockable.')
	
	
	
	
	
	def unlock(self, select, log):
		'''a method to batch unlock task'''
		modified = []
		unmodified = []
		for i in select:
			task = self.tasks[i]
			if task.status == 'pendinglock':
				task.status = 'pause'
				modified.append(i)
			elif task.status == 'lock':
				task.status = 'waiting'
				modified.append(i)
			else:
				unmodified.append(i)
		
		if len(modified)>0:
			log.write('Task n°«'+','.join(str(x) for x in modified)+'» have been unlocked.')
		if len(unmodified)>0:
			log.write('Task n°«'+','.join(str(x) for x in unmodified)+'» were already unlock.')
	
	
	
	
	
	def batchSelect(self, log, select = None):
		'''A method to select multiple task'''
		log.menuIn('Multiple Task Selecting')
		if select is None:
			select = []
		page = 0
		mode = 'ADD'
		msg = 'What task to select [ADD mode] : '
		
		while True:
			log.print()
			print('\n\n        Multiple Selection :\n')
			self.print(page, select, True)
			
			choice = input(msg).strip().lower()
			
			if choice in ['quit', 'q', 'cancel']:
				log.menuOut()
				return select
			if choice in ['h', 'help']:
				log.menuIn('Help')
				log.print()
				
				print('''\n\n        \033[4mHELP :\033[0m

Scroll up the list : u or <
Scroll down the list : d or > or just type enter

\033[4mMode :\033[0m

Additive (ADD) mode : a or add or +
Subtractive (SUB) mode : s or sub or -
Switch (SWT) mode : switch or swt

In ADD mode, you select task by giving them number. In SUB mode, you unselect them the same way. In SWT mode, the same action will select those who are unselect and reciprocally.

\033[4mEnumerating :\033[0m

You can select task one by one by typing them number or select a range of task: 1-5 will select task 1 to 5 include. You can select all by typing all.

Help : h or help
Quit : q or quit

''')
				
				input('Press enter to continue')
				log.menuOut()
			elif choice  in ['u', '<']:
				if page > 0:
					page -= 1
			elif choice  in ['d', '>', '']:
				if page < math.floor((len(self.tasks)-1)/25):
					page += 1
				elif choice == '':
					page = 0
			elif choice  in ['a', 'add', '+']:
				mode = 'ADD'
				msg = 'What task to select [ADD mode] : '
			elif choice  in ['s', 'sub', '-']:
				mode = 'SUB'
				msg = 'What task to unselect [SUB mode] : '
			elif choice  in ['switch', 'swt']:
				mode = 'SWT'
				msg = 'What task to switch selecting [SWT mode] : '
			elif choice  in ['all']:
				if mode == 'ADD':
					select = list(range(0, len(self.tasks)))
				elif mode == 'SUB':
					select = []
				else:
					for i in range(0, len(self.tasks)):
						if i in select:
							select.remove(i)
						else:
							select.append(i)
			elif choice.count('-') == 1:
				try:
					choice = choice.split('-')
					last = min(int(choice.pop().strip()), len(self.tasks)-1)
					first = max(int(choice.pop().strip()), 0)
				except (ValueError, IndexError):
					log.error('your request is unvalid', False)
					continue
				
				inter = list(range(first, last+1))
				
				if mode == 'ADD':
					for i in inter:
						if i not in select:
							select.append(i)
					select.sort()
				elif mode == 'SUB':
					for i in inter:
						if i in select:
							select.remove(i)
				else:
					for i in inter:
						if i in select:
							select.remove(i)
						else:
							select.append(i)
					select.sort()
			else:
				try:
					choice = int(choice)
				except ValueError:
					log.error('your request ('+choice+') is unvalid', False)
					continue
				
				if mode == 'ADD' and choice not in select:
					select.append(choice)
					select.sort()
				elif mode == 'SUB' and choice in select:
					select.remove(choice)
				elif mode == 'SWT':
					if choice in select:
						select.remove(choice)
					else:
						select.append(choice)
						select.sort()
	
	
	
	
	
	def copyTasks(self, log, select, preferences):
		'''A method to copy a selection of task to apply them another preset'''
		log.menuIn('Batch Copy')
		
		log.menuIn('Position Choice')
		while True:
			log.print()
			print('\n\n        Copy : Positon Choice :\n\nChoice : \n\n1- Immediately after original task\n2- At the end of list\n0- Cancel')
			choice = input('choice : ').strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				log.menuOut()
				log.menuOut()
				return select, False
			
			if choice in ['1', '2']:
				row = int(choice)
				break
			else:
				log.error('unvalid choice, accepted choice is 0 1 or 2', False)
				continue
		log.menuOut()
		
		
		copies = []
		select.sort()
		for i in select:
			copies.append(self.tasks[i].copy())
		
		for t in copies:
			t.status = 'waiting'
			t.log = None
		
		if row == 2:
			newSelect = list(range(len(self.tasks),len(self.tasks) + len(copies)))
			self.tasks += copies
			log.write('Task n°«'+','.join(str(x) for x in select)+'» copied to row n°'+str(newSelect[0])+' to '+str(newSelect[-1])+'.')
			log.menuOut()
			return newSelect, True
		else:
			newSelect = []
			gap = 0
			for i in select:
				newSelect.append(i+1+gap)
				gap += 1
				self.tasks.insert(newSelect[-1], copies.pop(0))
			log.write('Task n°«'+','.join(str(x) for x in select)+'» copied to row n°'+','.join(str(x) for x in newSelect)+'.')
			log.menuOut()
			return newSelect, True
	
	
	
	
	
	def run(self, scriptPath, log, preferences):
		'''launch task list rendering'''
		log.menuIn('Run Tasks')
		
		# state that BRM is in run mode until all task is rendered
		run = True 
		self.status = 'run'
		self.runningMode = self.UNTIL_LIST_END
		self.current = 0 # current task
		
		# create a socket to communicate with blender script
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(('localhost', preferences.port))
		self.socket.listen(5)
		
		# initialize empty list
		self.listenerThreads = []
		self.listenerSockets = []
		self.renderingSubprocess = []
		
		# start to display run menu with a parallel thread
		runMenu = threading.Thread(target = self.runMenu , args=(log,))
		runMenu.start()
		
		for self.current,task in enumerate(self.tasks):# rendering each task
			# render unlock task
			if task.status not in ['lock', 'pendinglock']:
				run = task.run( self,\
								scriptPath,\
								log,\
								preferences\
							)
			
			# remove listener associate with closed thread
			self.checkListeners()
			
			# stop running on user request
			if not run or self.runningMode != self.UNTIL_LIST_END:
				break
		
		self.status = 'stop'# state that BRM quit run mode
		
		# waiting until there is no remaining socket listener
		while len(self.listenerThreads) > 0:
			self.checkListeners()
			time.sleep(1)
		
		# delete socket/process list
		self.listenerThreads = None
		self.listenerSockets = None
		self.renderingSubprocess = None
		
		# close socket
		self.socket.close()
		self.socket = None
		
		# archive fully rendered task
		print('check frame after quiting the running mode')
		self.checkAndArchive(preferences.archiveLimit)
		print('all done, press enter to continue!')
		
		# stop the thread who display the running mode menu and quit
		runMenu.join()
		log.menuOut()
	
	
	
	
	
	def checkListeners(self):
		'''remove dead thread'''
		for l in self.listenerThreads[:]:
			if not l.is_alive():
				self.listenerThreads.remove(l)
	
	
	
	
	
	def runMenu(self, log):
		'''display and manage action running mode action'''
		# run menu remaining message in log
		log.runMenu = 'What do you want to do? (h for help)'
		
		while True:
			# print run menu with current task and get user action
			self.tasks[self.current].printRunMenu(self.current+1, len(self.tasks), log)
			choice = input().lower().strip()
			
			
			if self.status == 'stop':# stop run menu on running mode end
				break
				
			elif choice in ['h', 'help']:
				# use help as remaining message on user demand
				log.runMenu = '''wait for all rendering to be done or
(option starting by # are not yet implement)
type:           for:
h        display this help
t        to stop rendering after the current task
s        to stop rendering after the current scene
c        to stop rendering after the current frame
n        to stop rendering immediatly (send terminated signal)
f        to force to stop rendering immediatly (send kill signal)
p        to get subprocess PID
What do you want to do? (type h for help)'''
				
			elif choice in ['c', 'current', 'frame']:
				# state that BRM running mode should stop after current frame rendering
				self.runningMode = self.UNTIL_FRAME_END
				# request all blender thread to stop after current frame rendering
				for l in self.listenerSockets[:]:
					l['socket'].sendall( (l['uid']+' stopAfterFrame() EOS').encode() )
				log.runMenu = 'Rendering will be stoped after current frame!\nWhat do you want to do? (type h for help)'
				log.write('Order to stop rendering after current frame.')
				
			elif choice in ['s', 'scene']:
				# request all blender thread to stop after current frame rendering
				for l in self.listenerSockets[:]:
					l['socket'].sendall( (l['uid']+' stopAfterScene() EOS').encode() )
				# state that BRM running mode should stop after current scene rendering
				self.runningMode = self.UNTIL_SCENE_END
				log.runMenu = 'Rendering will be stoped after current scene!\nWhat do you want to do? (type h for help)'
				log.write('Order to stop rendering after current scene.')
				
			elif choice in ['t', 'task']:
				# state that BRM running mode should stop after current task rendering
				self.runningMode = self.UNTIL_TASK_END
				log.runMenu = 'Rendering will be stoped after current task!\nWhat do you want to do? (type h for help)'
				log.write('Order to stop rendering after current task.')
				
			elif choice in ['p', 'pid']:
				# display all blender processe PID via remaining message
				log.runMenu = 'Subprocess PID List :\n'
				for subP in self.renderingSubprocess:
					log.runMenu += str(subP.pid)+'\n'
				log.runMenu += 'What do you want to do? (type h for help)'
				
			elif choice in ['n', 'now']:
				# regulary terminate all blender thread
				for subP in self.renderingSubprocess:
					subP.terminate()
				# state that BRM running mode should stop now
				self.runningMode = self.STOP_NOW
				log.runMenu = 'Try to stop rendering right now!\nWhat do you want to do? (type h for help)'
				log.write('Order to stop rendering now.')
				
			elif choice in ['f', 'force', 'forced']:
				# kill all blender thread
				for subP in self.renderingSubprocess:
					subP.kill()
				# state that BRM running mode should stop now by force
				self.runningMode = self.STOP_FORCED
				log.runMenu = 'Actually forcing rendering to stop!\nWhat do you want to do? (type h for help)'
				log.write('Order to force rendering to stop.')
				
			else:
				# unvalid choice
				log.runMenu = 'Ask for an unknow action «'+choice+'»! Retry!\nWhat do you want to do? (type h for help)'
		
		log.runMenu = None# delete remaining message
	
	
	
	
	
	def checkAndArchive(self, limit):
		'''Archive task after ensuring all frame rendering was finshed'''
		for task in self.tasks[:]:
			if ( task.log is not None and task.log.isComplete() )\
					or task.status == 'erased':# archive all finished task
				self.tasks.remove(task)
				self.archive.append(task)
		
		while len(self.archive) > limit:# respect archive limit size
			self.archive.pop(0)
	
	
	
	
	
	
