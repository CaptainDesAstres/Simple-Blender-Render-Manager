#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task list'''
import xml.etree.ElementTree as xmlMod
import os, re, math, threading, socket, time, shutil
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
		'''Erase lock file at script end or in case of crash'''
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
		'''export in xml'''
		xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
		
		# export pending task list
		xml += '<tasklist>\n<tasks>\n'
		for task in self.tasks:
			xml += task.toXml()
		
		# export archived task list
		xml += '</tasks>\n<archive>\n'
		for task in self.archive:
			xml += task.toXml()
		
		xml += '</archive>\n</tasklist>\n'
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
				
			elif choice in ['a', 'add', '+']:
				if self.add(log, preferences):# add task to the list
					saveTasks( preferences.output.path, self )
				
			elif choice in ['d', '>', '']:# display next task page
				if page < math.floor((len(self.tasks)-1)/25):
					page += 1
					
				elif choice == '':
					page = 0
				
			elif choice in ['u', '<'] and page > 0:# display previous task page
				page -= 1
				
			elif choice in ['b', 'batch']:
				if self.batchEdit(log, preferences):# edit task by batch
					self.save(preferences.output.path)
				
			elif choice in ['l', 'log']:# display archived task
				self.menuArchive(log, preferences)
				
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
	
	
	
	
	
	def menuArchive(self, log, preferences):
		'''Display Archive list'''
		log.menuIn('Archived Task List')
		page = 0
		
		while True:
			log.print()
			# Display current page of archive list
			self.print(page, archive = True)
			choice= input('Action (h for help):').strip().lower()
			
			if choice in ['q', 'quit']:
				# Quit menu (return to main menu)
				log.menuOut()
				return
			
			if choice in ['d', '>', '']:
				# Display next archive list page
				if page < math.floor((len(self.archive)-1)/25):
					page += 1
				elif choice == '':
					page = 0
				
			elif choice in ['u', '<']:
				# Display previous archive list page
				if page > 0:
					page -= 1
				
			elif choice in ['h', 'help']:
				# Display help
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
				# get archived task choice
				try:
					choice = int(choice)
				except:
					log.error('Unknow request!', False)
					continue
				
				# if no task with this number
				if choice < 0 or choice >= len(self.archive):
					log.error('There is no archived task n°'+str(choice)+'!', False)
					continue
				
				# display archived task menu
				if(self.archive[choice].menuArchive(log, choice, self, preferences)):
					self.save(preferences.output.path)
	
	
	
	
	
	def print(self, page, selection = None, whole = False, archive = False):
		'''Display pending or selected or archived task list'''
		Psize = 25 # task by page
		
		# print page header
		print('''
\033[4mID |  File Name              |  Render All Scene |  Percent OW |  Status     |\033[0m''')
		if page > 0:
			print('▲▲▲|▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲|▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲|▲▲▲▲▲▲▲▲▲▲▲▲▲|▲▲▲▲▲▲▲▲▲▲▲▲▲|')
		
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
			print('▼▼▼|▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼|▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼|▼▼▼▼▼▼▼▼▼▼▼▼▼|▼▼▼▼▼▼▼▼▼▼▼▼▼|')
	
	
	
	
	
	def add(self, log, preferences):
		'''Add task to the list'''
		log.menuIn('Add Task')
		log.menuIn('Task(s) Path')
		
		while True:
			# get path to the new file
			log.print()
			path = input("\n\n        Add Task(s) :\n\n\nGive the path of a blender file (or the path of a directory containing multiple blender file to add them all, or empty input to quit) :").strip()
			
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
					or (not os.path.isfile(path) and not os.path.isdir(path) )\
					or not os.access(path, os.R_OK):
				log.error('"'+path+'" didn\'t exist or you don\'t have the permission to read it')
				continue
			
			# check if path point to a .blend file
			if os.path.isfile(path) and \
					(len(path) < 7 or re.search(r'.blend\d{0,10}$', path) is None):
				log.error('"'+path+'" path don\'t seemed to be a blender file (need a .blend extension) nor a directory.')
				continue
			
			# accept path
			log.menuOut()
			break
		
		if os.path.isfile(path):
			confirm = self.addFile(log, preferences, path)
		else:
			confirm = self.addDirectory(log, preferences, path)
		
		log.menuOut()
		return confirm
	
	
	
	
	
	def addFile(self, log, preferences, path):
		'''Add a task from a path'''
		log.write('Try to add "'+path+'" task:')
		
		# try to open file and get scene infos
		command = '("'+preferences.blender.path\
						+'" -b "'+path+'" -P "'\
						+os.path.realpath(__file__+'/..')+'/getter/getFileTaskInfos.py")'\
						+' || echo \'BlenderVersionError\' '
		info = os.popen(command).read()
		
		if info.count('BlenderVersionError') != 0:
			# treat blender running error
			log.error('Blender version call error! Try to verified the path of default blender version!', False)
			log.menuOut()
			log.write('  Blender Version Error : abort task adding')
			return False
		
		# parse file information
		#print(info)# print debug info
		info = re.search(r'<\?xml(.|\n)*</fileInfo>',info).group(0)
		info = xmlMod.fromstring(info)
		info = FileInfo(info)
		
		# render all scene and resolution percentage overwriting choice
		scene, percentOW = info.setChoice(log, preferences)
		if scene is None:
			log.menuOut()
			return False
		
		# create the task
		task = Task(		path = path,
							scene = scene,
							percentOW= percentOW,
							fileInfo = info
							)
		
		# insure against name collision
		task.name = self.getUnusedTaskName(task.name, preferences, log )
		
		# copy file in task list directory
		preferences.output.checkAndCreate()# check all output directory exists
		shutil.copy(\
				task.path,\
				preferences.output.path+'source/'+task.name+'.blend'\
					)
		
		# add the task
		self.tasks.append( task )
		log.write('  add task «'+path+'»')
		
		return True
	
	
	
	
	
	def addDirectory(self, log, preferences, path):
		'''Add a task for each blender file of a directory'''
		# Set default recursive mode, backup mode, scene mode
		recursive = False
		backup = False
		allScene = True
		
		# get default resolution overwriting mode
		percentOW = (preferences.percentOW == 'always')
		
		log.menuIn('Add directory task(s) content')
		log.menuIn('Add mode')
		
		# get user choice:
		while True:
			log.print()
			
			print('\t\t\tDirectory task add mode:\n\n')
			
			# print recursive mode
			if recursive:
				print('1- Search in subfolder')
			else:
				print('1- Ignore subfolder')
			
			# print backup mode
			if backup:
				print('2- Add blender backup files too («.blend1», «.blend2», etc…)')
			else:
				print('2- Only add «.blend» files')
			
			# print scene mode
			if allScene:
				print('3- Render all scenes of each files')
			else:
				print('3- Only render active scenes of each files')
			
			# print percent overwriting mode
			if percentOW:
				print('4- Force to render with 100% resolution')
			else:
				print('4- Respect files resolution percentage settings')
			
			print('0- Abort and quit')
			
			# get user confirmation or demand
			choice = input('\n\nPress enter to continue, or 0 to abort, or a number between 1 and 4 to switch mode : ').strip().lower()
			
			# follow user quit order
			if choice in ['0', 'q', 'quit', 'cancel', 'abort']:
				log.menuOut()
				log.menuOut()
				return False
			
			# follow user confirmation order
			if choice in ['', 'confirm', 'yes', 'y', 'ok', 'continue']:
				log.menuOut()
				break
			
			# follow user switch command
			if choice == '1':
				recursive = not recursive
				
			elif choice == '2':
				backup = not backup
				
			elif choice == '3':
				allScene = not allScene
				
			elif choice == '4':
				percentOW = not percentOW
				
			else:
				# reject unvalid order
				log.error('Unvalid operation')
		
		# get task paths
		paths = self.getTasksPaths( path, recursive, backup )
		
		# add a task for each path
		
		
		# try to open file and get scene infos
		
		
		# treat blender running error
		
		
		# parse file information
		
		
		# create the task
		
		
		# insure against name collision
		
		
		# copy file in task list directory
		
		
		# add the task and confirm in log
		
		
		# confirm and quit
		log.menuOut()
		return True
	
	
	
	
	
	def getTasksPaths( self, path, recursive, backup ):
		'''return a list of paths to blender files inside a directory'''
		# ensure path end by /
		if path[-1] != '/':
			path += '/'
		
		# get directory content
		content = os.listdir(path).sort()
		
		#init path and subdirectory list
		paths = []
		subdirectory = []
		
		if backup:
			# get all blender file path (including backup file)
			for f in content:
				if os.path.isfile(path+f) and  re.search(r'.blend\d{0,10}$', f) is not None):
					paths.append(path+f)
					
				elif os.path.isdir(path+f):
					subdirectory.append(path+f)
			
		else:
			# get all blender file path (excluding backup file)
			for f in content:
				if os.path.isfile(path+f) and len(f) > 6 and f[-6:] == '.blend':
					paths.append(path+f)
					
				elif os.path.isdir(path+f):
					subdirectory.append(path+f)
		
		# get all blender file in sub folder
		for s in subdirectory:
			paths += self.getTasksPaths( path+s, recursive, backup )
		
		return paths
	
	
	
	
	
	def isTaskNameFree(self, name, preferences):
		'''Check if task name is free for use'''
		# check if the name is already used by a pending task
		for t in self.tasks:
			if t.name == name:
				return False
		
		# check if the name is already used by an archived task
		for t in self.archive:
			if t.name == name:
				return False
		
		# Check if there is a source name with this name
		if os.path.exists(preferences.output.path+'source/'+name+'.blend'):
			return False
		
		# Check if there is a output dircetory with this name
		if os.path.exists(preferences.output.path+'render/'+name+'/'):
			return False
		
		return True
	
	
	
	
	
	def getUnusedTaskName(self, name, preferences, log = None ):
		'''Return a free of use task name'''
		new = name.strip()
		
		# return original name if unused
		if self.isTaskNameFree(new, preferences):
			return new
		
		if not new[-1].isdigit():
			i = 1
		else:
			# get original name index
			i=''
			while new[-1].isdigit():
				i = new[-1]+i
				new = new[0:-1]
			new = new.strip()
			i = int(i)+1
		
		# generate a new name if needed
		while(not self.isTaskNameFree(new+' '+str(i), preferences)):
			i+=1
		
		if log is not None:
			log.error('Task name already used. task name changed to «'\
						+new+' '+str(i)+'»')
		
		return new+' '+str(i)
		
	
	
	
	
	
	def save(self, output):
		'''Save Tasks list'''
		saveTasks(output, self)
		
	
	
	
	
	
	def remove(self,preferences, log, selected):
		'''remove task after confirmation'''
		log.menuIn('Task(s) Removing')
		log.print()
		print('\n\n        Removing Selected Task :\n')
		self.print(0, selected)
		
		# get user confirmation
		confirm = input('Do you realy want to erase all this task?(y) ').strip().lower()
		
		log.menuOut()
		if confirm == 'y':
			# create output path for security
			preferences.output.checkAndCreate()
			selected.sort(reverse = True)
			# remove selected task
			for i in selected:
				# remove task from the list
				t = self.tasks.pop(i)
				
				# move task file to trash directory
				if os.path.exists(preferences.output.path+'source/'+t.name+'.blend'):
					shutil.move(\
						preferences.output.path+'source/'+t.name+'.blend',\
						preferences.output.path+'trash/'+t.name+'.blend'
						)
			
			return True
		else:
			# quit without task removing
			return False
	
	
	
	
	
	def move(self, log, selected):
		'''move selected tasks inside the list'''
		log.menuIn('Task(s) Moving')
		change = False
		selected.sort()
		
		while True:
			log.print()
			print('\n\n        Moving Selected Task :\n')
			self.print(0, selected, True)
			
			# get user move instruction
			choice = input('how to move selected task : (h for help) ').strip().lower()
			
			if choice in ['', 'q', 'quit', 'cancel']:
				# confirm move and quit
				log.menuOut()
				return change, selected
				
			elif choice in ['h', 'help']:
				#display moving help
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
				# reverse selection order?
				reverse = choice in ['r', 'i', 'inverse', 'reverse']
				
				if choice in ['t', 'top']:# move to list top
					choice = -1
					
				elif reverse or choice in ['f', 'first']:
					# move to the position of the first selected task
					choice = selected[0]
					
				elif choice in ['l', 'last']:
					# move to the position of the last selected task
					choice = selected[-1]
					
				elif choice in ['b', 'bottom']:# move to list bottom
					choice = len(self.tasks)
					
				else:
					# try to get manual index choice
					try:
						choice = int(choice)
					except ValueError:
						log.error('Unvalid action', False)
						continue
				
				# move selection inside the list to the specified index
				selected = self.moveTo(log, selected, choice)
				
				if reverse:# reverse selection order
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
		'''move selected task to specified row'''
		selected.sort()
		# do the selection in countinuous?
		isRange = selected == list(range(selected[0], selected[-1]+1))
		selected.reverse()
		selection = []
		
		# get all task by pop them from the list and adapt row if needed
		for index in selected:
			selection.append(self.tasks.pop(index))
			if not isRange and row > index:
				row -= 1
		selection.reverse()
		
		if row <= 0: 
			# put selection in top of the list
			self.tasks = selection + self.tasks
			log.write('Task n°«'+','.join(str(x) for x in selected)+'» moved on top of the list')
			return list(range(0, len(selected)))
			
		elif row >= len(selection) + len(self.tasks):
			# put selection in bottom of the list
			self.tasks += selection
			log.write('Task n°«'+','.join(str(x) for x in selected)+'» moved on bottom of the list')
			return list(range(len(self.tasks)-len(selected) , len(self.tasks)))
			
		else:
			# Put selection at specified index/row
			self.tasks = self.tasks[0:row]+selection+self.tasks[row:]
			log.write('Task n°«'+','.join(str(x) for x in selected)+'» moved on row '+str(row)+' of the list')
			return list(range(row, row + len(selected)))
	
	
	
	
	
	def batchEdit(self, log, preferences):
		'''batch edit task'''
		log.menuIn('Batch Editing')
		
		# get user selection
		select = self.batchSelect(log)
		
		# quit if null selection
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
1-  Copy
2-  Regroup And Move
3-  Remove
4-  Lock
5-  Unlock
6-  Enable «render all scene» option
6*- Disable «render all scene» option
7-  Enable resolution percentage overwriting
7*- Disable resolution percentage overwriting
9- Change Selection
0- Quit
''')
			
			if choice in ['q', 'quit', 'cancel', '0']:
				# quit batch task edition
				log.menuOut()
				log.menuOut()
				return change
				
			elif choice == '1':
				# copy selected tasks
				new, confirm = self.copyTasks(log, select, preferences)
				if confirm:
					select = new
					change = True
					log.menuOut()
					log.menuIn('Task n°'+','.join(str(x) for x in select))
				
			elif choice == '2':
				# move selected tasks inside the list
				
				confirm, select = self.move(log, select)
				change = (confirm or change)
				
			elif choice == '3':
				# delete selected tasks
				if self.remove(preferences, log, select):
					log.menuOut()
					log.menuOut()
					return True
				
			elif choice == '4':
				# lock selected tasks
				self.lock(select, log)
				change = True
				
			elif choice == '5':
				# unlock selected tasks
				self.unlock(select, log)
				change = True
				
			elif choice in [ '6', '6*', '7', '7*' ]:
				change = True
				unmodified, modified = [], []
				# edit all selected task
				for i in select:
					task = self.tasks[i]
					
					if task.log is None:
						# free to change settings
						if choice == '6':
							# Enable «render all scene» option
							task.scene = True
						elif choice == '6*':
							# Disable «render all scene» option
							task.scene = False
						elif choice == '7':
							# Enable resolution percentage overwriting
							task.percentOW = True
						elif choice == '7*':
							# Disable resolution percentage overwriting
							task.percentOW = False
						modified.append(i)
						
					else:
						unmodified.append(i)
				
				# log output variable part
				if choice == '6':
					txt = 'render all scenes'
				elif choice == '6*':
					txt = 'only render active scene'
				elif choice == '7':
					txt = 'use 100% resolution settings'
				elif choice == '7*':
					txt = 'use file resolution percentage'
				
				# log report
				if( len(modified)>0 ):
					log.write('Task n°«'+','.join(str(x) for x in modified)+'» have been set to '+txt+'.')
				if( len(unmodified)>0 ):
					log.write('Task n°«'+','.join(str(x) for x in unmodified)+'» are already started and can\'t be change.')
				
			elif choice == '9':
				# change selection
				log.menuOut()
				select = self.batchSelect(log, select)
				
				# if empty selection, quit batch edit
				if len(select) == 0:
					log.menuOut()
					return change
				
				log.menuIn('Task n°'+','.join(str(x) for x in select))
				
			else:
				log.error('Unvalid request',False)
	
	
	
	
	
	def lock(self, select, log):
		'''batch lock task'''
		# keep trace of modified and unmodified task
		modified = []
		unmodified = []
		
		for i in select:
			task = self.tasks[i]
			
			# lock selected tasks
			if task.status == 'started':
				task.status = 'pendinglock'
				modified.append(i)
				
			elif task.status == 'waiting':
				task.status = 'lock'
				modified.append(i)
				
			else:
				unmodified.append(i)
		
		# log modification
		if len(modified)>0:
			log.write('Task n°«'+','.join(str(x) for x in modified)+'» have been locked.')
		if len(unmodified)>0:
			log.write('Task n°«'+','.join(str(x) for x in unmodified)+'» were already lock or unlockable.')
	
	
	
	
	
	def unlock(self, select, log):
		'''batch unlock task'''
		# keep trace of modified and unmodified task
		modified = []
		unmodified = []
		
		for i in select:
			task = self.tasks[i]
			
			# unlock selected tasks
			if task.status == 'pendinglock':
				task.status = 'started'
				modified.append(i)
				
			elif task.status == 'lock':
				task.status = 'waiting'
				modified.append(i)
				
			else:
				unmodified.append(i)
		
		# log modification
		if len(modified)>0:
			log.write('Task n°«'+','.join(str(x) for x in modified)+'» have been unlocked.')
		if len(unmodified)>0:
			log.write('Task n°«'+','.join(str(x) for x in unmodified)+'» were already unlock.')
	
	
	
	
	
	def batchSelect(self, log, select = None):
		'''manual selection of multiple task'''
		log.menuIn('Multiple Task Selection')
		
		# init page, selection and mode
		if select is None:
			select = []
		page = 0
		mode = 'ADD'
		msg = 'What task to select [ADD mode] : '
		
		while True:
			log.print()
			print('\n\n        Multiple Selection :\n')
			self.print(page, select, True)
			
			# get user selection request
			choice = input(msg).strip().lower()
			
			if choice in ['quit', 'q', 'cancel']:
				# quit with current selection
				log.menuOut()
				return select
			
			if choice in ['h', 'help']:
				#display selection help
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
				
			elif choice  in ['u', '<']:# list page up
				if page > 0:
					page -= 1
				
			elif choice  in ['d', '>', '']:# list page down
				if page < math.floor((len(self.tasks)-1)/25):
					page += 1
				elif choice == '':
					page = 0
				
			elif choice  in ['a', 'add', '+']:# use additive selection mode
				mode = 'ADD'
				msg = 'What task to select [ADD mode] : '
				
			elif choice  in ['s', 'sub', '-']:# use substractive selection mode
				mode = 'SUB'
				msg = 'What task to unselect [SUB mode] : '
				
			elif choice  in ['switch', 'swt']:# use switching selection mode
				mode = 'SWT'
				msg = 'What task to switch selecting [SWT mode] : '
				
			elif choice == 'all':
				if mode == 'ADD':# select all task
					select = list(range(0, len(self.tasks)))
					
				elif mode == 'SUB':# unselect all task
					select = []
					
				else:
					for i in range(0, len(self.tasks)):
						if i in select:# unselect all selected task
							select.remove(i)
						else:# select all unselected task
							select.append(i)
				
			elif choice.count('-') == 1:# treat range selecting
				try:# try to get first and last task of the selection
					choice = choice.split('-')
					last = min(int(choice.pop().strip()), len(self.tasks)-1)
					first = max(int(choice.pop().strip()), 0)
				except (ValueError, IndexError):
					log.error('your request is unvalid', False)
					continue
				
				# get selection
				inter = list(range(first, last+1))
				
				if mode == 'ADD':
					# additive mode: add to selection all unselected task in the range
					for i in inter:
						if i not in select:
							select.append(i)
					select.sort()
					
				elif mode == 'SUB':
					# substractive mode: remove from selection all task in the range
					for i in inter:
						if i in select:
							select.remove(i)
					
				else:# switch mode
					for i in inter:
						if i in select: # remove from selection task of the range
							select.remove(i)
						else: # add to selection task of the range that wasn't previously selected
							select.append(i)
					select.sort()
				
			else:
				# get task by task choice
				try:
					choice = int(choice)
				except ValueError:
					log.error('your request ('+choice+') is unvalid', False)
					continue
				
				if mode == 'ADD' and choice not in select:# add to selection
					select.append(choice)
					select.sort()
					
				elif mode == 'SUB' and choice in select:# remove from selection
					select.remove(choice)
					
				elif mode == 'SWT':
					if choice in select:# unselect if selected
						select.remove(choice)
					else:# select if unselected
						select.append(choice)
						select.sort()
	
	
	
	
	
	def copyTasks(self, log, select, preferences):
		'''copy selected task'''
		log.menuIn('Batch Copy')
		log.menuIn('Position Choice')
		
		while True:
			log.print()
			# get user position choice
			choice = input('\n\n        Copy : Positon Choice :\n\nChoice : \n\n1- Immediately after original task\n2- At the end of list\n0- Cancel\n\nchoice : ').strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				#quit without copying
				log.menuOut()
				log.menuOut()
				return select, False
			
			if choice in ['1', '2']:# valid user choice
				break
			
			log.error('unvalid choice, accepted choice is 0 1 or 2', False)
			continue
		log.menuOut()
		
		# make a list of copy task
		index, copies = [], []
		select.sort()
		for i in select[:]:
			if os.path.exists(preferences.output.path+'source/'+self.tasks[i].name+'.blend'):
				copies.append(self.tasks[i].copy(self, preferences, False))
				index.append(i)
			else:
				log.error('Can\'t copy task n°'+str(i)+': can\'t find blender source file corresponding to the task!')
		
		# quit if no task have been copied
		if len(index) == 0:
			log.menuOut()
			return select, False
		
		if choice == '2':
			# get new selection index
			newSelect = list( range(\
						len(self.tasks) ,\
						len(self.tasks) + len(copies)
							))
			
			# put copy task at list end
			self.tasks += copies
			
			# log the copy
			log.write('Task n°«'+','.join(str(x) for x in select)+'» copied to row n°'+str(newSelect[0])+' to '+str(newSelect[-1])+'.')
			
			log.menuOut()
			return newSelect, True
			
		else:
			
			newSelect = []
			gap = 0
			for i in index:
				# new selection index
				newSelect.append(i+1+gap)
				gap += 1
				# put copy task at list, just after copied task
				self.tasks.insert(newSelect[-1], copies.pop(0))
			
			# log the copy
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
		self.checkAndArchive(preferences)
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
	
	
	
	
	
	def checkAndArchive(self, preferences):
		'''Archive task after ensuring all frame rendering was finshed'''
		limit = preferences.archiveLimit
		for task in self.tasks[:]:
			if ( task.log is not None and task.log.isComplete() )\
					or task.status == 'erased':# archive all finished task
				# move task from pending task list to archived task list
				self.tasks.remove(task)
				self.archive.append(task)
				
				# archive source file
				shutil.move(\
						preferences.output.path+'source/'+task.name+'.blend',\
						preferences.output.path+'render/'\
							+task.name+'/'+task.name+'.blend'\
							)
				
				# save the rendering log
				with open(preferences.output.path+'render/'+task.name+'/log','w') as logFile:
					logFile.write(task.log.saveOutput())
		
		while len(self.archive) > limit:# respect archive limit size
			self.archive.pop(0)
	
	
	
	
	
	
