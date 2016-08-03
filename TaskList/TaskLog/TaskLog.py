#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task running log'''
import xml.etree.ElementTree as xmlMod
from usefullFunctions import XML


class TaskLog:
	'''class to manage task running log'''
	
	
	def __init__(self, xml = None, pref = None, task = None):
		'''initialize task log object'''
		if xml is None:
			self.defaultInit(pref, task)
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self, pref, task):
		'''initialize Task log object by generating from the task settings'''
		self.name = task
		self.backup = 0
		
		self.scenes = []
		if task.scene :
			for scene in task.info.scenes:
				self.scenes.append(\
								SceneLog(scene = scene.name, task = task, pref = pref)\
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
			self.scene.append(\
					SceneLog(xml = scene)\
								)
	
	
	
	
	
	def toXml(self):
		'''export task log into xml syntaxed string'''
		xml = '<log name="'+XML.encode(self.name)+'" backup="'+str(self.backup)\
				+'" status="'+self.status+'" >'
		
		for scene in self.scenes:
			xml += scene.toXml()
		
		xml = '</log >'
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
			
	
	
	
	
	
#	def print(self, index = False):
#		'''A method to print task log'''
#		print('The task have '+str(len(self.groups))+' group(s):')
#		ended, total = 0, 0
#		for i, group in enumerate(self.groups):
#			if index:
#				group.runMenuPrint(i+1)
#			else:
#				group.runMenuPrint()
#			
#			total += (group.end - group.start + 1)
#			ended += len(group.frames)
#		print('\n\n                  '+str(ended)+'/'+str(total)\
#							+'('+str(total-ended)+' remaining)')
	
	
	
	
	
#	def getMainPath(self):
#		'''return the task main path'''
#		if self.backup == 0:
#			return self.path
#		else:
#			return self.path+'previous rendering '+str(self.backup)+'/'
	
	
	
	
	
#	def isComplete(self):
#		'''check if there is still frame waiting to be rendered'''
#		for group in self.groups:
#			if group.remaining()>0:
#				return False
#		return True
	
	
	
	
	
#	def checkFrames(self):
#		'''check for each frame that have been claimed as rendered if there is really a file corresponding to it'''
#		path = self.getMainPath()
#		for group in self.groups:
#			group.checkFrames(path)
#		
#		return self.isComplete()
	
	
	
	

