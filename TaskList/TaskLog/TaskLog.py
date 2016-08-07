#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''task rendering log'''
from TaskList.TaskLog.SceneLog import *
from usefullFunctions import XML


class TaskLog:
	'''task rendering log'''
	
	
	def __init__(self, xml = None, task = None):
		'''load task log info'''
		if xml is None:
			self.defaultInit(task)
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self, task):
		'''generate log from task settings'''
		# get task file name
		self.name = task.path.split('/').pop().split('.')
		self.name.pop()
		self.name = '.'.join(self.name)
		
		
		self.scenes = []
		if task.scene :
			# load all scene info
			for scene in task.info.scenes.keys():
				self.scenes.append(\
								SceneLog(scene = scene, task = task)\
								)
			
		else:
			# load active scene info
			self.scenes.append(\
								SceneLog(scene = task.info.active,\
									task = task)\
								)
		
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize Task log object with saved log'''
		self.name = XML.decode(xml.get('name'))
		
		#load all scene info
		self.scenes = []
		for scene in xml.findall('scene'):
			self.scenes.append(\
					SceneLog(xml = scene)\
								)
	
	
	
	
	
	def toXml(self):
		'''export in xml'''
		#export task name
		xml = '<log name="'+XML.encode(self.name)+'" >\n'
		
		# export each scene
		for scene in self.scenes:
			xml += scene.toXml()
		
		xml += '</log >'
		return xml
	
	
	
	
	
	def menu(self, log, index):
		'''navigate inside rendering log'''
		log.menuIn('Rendering Log')
		
		while True:
			log.print()
			print('\n\n        Rendering Log of task n°'+str(index)+' :\n')
			self.print(True)
			
			# get user instructions
			choice = input('\n\nType scene index for details (q to quit) :').strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				# quit rendering log
				log.menuOut()
				return
			
			try:# try to get choose scene index
				choice = int(choice) - 1
			except:
				log.error('Integer value expected!', False)
				continue
			
			if choice >= 0 and choice < len(self.scenes):
				# display scene rendering log
				self.scenes[choice].menu(log)
			else:
				log.error('There is no scene with this index!', False)
			
	
	
	
	
	
	def print(self, index = False):
		'''Display task log info'''
		print(''+str(len(self.scenes))+' scene(s) in this task:')
		
		ended, total = 0, 0
		
		for i, scene in enumerate(self.scenes):
			# display each scene info
			if index:
				scene.runMenuPrint(i+1)
			else:
				scene.runMenuPrint()
			
			# compute total frame number and rendered frame number
			total += (scene.end - scene.start + 1)
			ended += len(scene.frames)
		
		# display task frame info resume
		print('\n\n                  '+str(ended)+'/'+str(total)\
							+'(remain '+str(total-ended)+' frame(s))')
	
	
	
	
	
	def isComplete(self):
		'''report if there is still unrendered frame'''
		for scene in self.scenes:
			if scene.remaining()>0:
				return False
		return True
	
	
	
	

