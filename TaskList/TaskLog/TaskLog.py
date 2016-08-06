#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task running log'''
import xml.etree.ElementTree as xmlMod
from TaskList.TaskLog.SceneLog import *
from usefullFunctions import XML


class TaskLog:
	'''class to manage task running log'''
	
	
	def __init__(self, xml = None, pref = None, task = None):
		'''load task log info'''
		if xml is None:
			self.defaultInit(pref, task)
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self, pref, task):
		'''generate log from task settings'''
		self.name = task.path.split('/').pop().split('.')
		self.name.pop()
		self.name = '.'.join(self.name)
		self.backup = 0
		
		self.scenes = []
		if task.scene :
			for scene in task.info.scenes.keys():
				self.scenes.append(\
								SceneLog(scene = scene, task = task, pref = pref)\
								)
		else:
			self.scenes.append(\
								SceneLog(scene = task.info.active,\
									task = task, pref = pref)\
								)
		
		self.status = 'ready'
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize Task log object with saved log'''
		self.name = XML.decode(xml.get('name'))
		self.backup = int(xml.get('backup'))
		self.status = XML.decode(xml.get('status'))
		self.scenes = []
		for scene in xml.findall('scene'):
			self.scenes.append(\
					SceneLog(xml = scene)\
								)
	
	
	
	
	
	def toXml(self):
		'''export task log into xml syntaxed string'''
		xml = '<log name="'+XML.encode(self.name)+'" backup="'+str(self.backup)\
				+'" status="'+self.status+'" >\n'
		
		for scene in self.scenes:
			xml += scene.toXml()
		
		xml += '</log >'
		return xml
	
	
	
	
	
	def menu(self, log, index):
		'''a method to display and browse into task rendering log'''
		log.menuIn('Rendering Log')
		while True:
			log.print()
			print('\n\n        Rendering Log of task n°'+str(index)+' :\n')
			
			self.print(True)
			
			choice = input('\n\ntype the index of a scene to see more or q to quit :').strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				log.menuOut()
				return
			
			try:
				choice = int(choice)-1
			except:
				log.error('Integer value expected!', False)
				continue
			
			if choice >= 0 and choice < len(self.scenes):
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
		'''check if there is still frame waiting to be rendered'''
		for scene in self.scenes:
			if scene.remaining()>0:
				return False
		return True
	
	
	
	

