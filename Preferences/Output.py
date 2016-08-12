#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage working path'''
import os
from shutil import move as movedir
from usefullFunctions import XML

class Output:
	'''class to manage working path'''
	
	
	def __init__(self, xml= None):
		'''load (or initialize default) output path preferences'''
		if xml is None:
			self.path = '/home/'+os.getlogin()+'/.BlenderRenderManager/work'
			if not os.path.exists(self.path):
				os.mkdir(self.path)
		else:
			self.fromXml(xml)
	
	
	
	
	
	def fromXml(self, xml):
		'''Load output path from xml'''
		self.path = XML.decode(xml.get('path'))
	
	
	
	
	
	def toXml(self):
		'''xml export'''
		return '<output path="'+XML.encode(self.path)+'" />\n'
	
	
	
	
	
	def menu(self, log):
		'''edit output path'''
		log.menuIn('Output Path')
		
		while True:
			log.print()
			new = input('\nWork Path :\n'+self.path\
							+'\n\n new path? (empty to keep current)'
						).strip()
			
			if new in [ '', '0', 'q' ]:# quit output path editing menu
				log.menuOut()
				return False
			elif self.set(new, log) :
				log.menuOut()
				return True
	
	
	
	
	
	def set(self, path, log):
		'''check and save new output path'''
		# remove first and last ' and/or "
		if path[0] in ['\'', '"'] and path[-1] == path[0]:
			path  = path[1:len(path)-1]
		
		# check if it's absolute path
		if path[0] != '/':
			log.error('It must be an absolute path!')
			return False
		
		# check path exist 
		if not os.path.exists(path):
			try:
				os.makedirs(path)
			except Exception as e:
				log.error('Unable to find or create a directory with this path!')
				return False
		
		# check path is a directory
		if not os.path.isdir(path):
			log.error('It must be a directory!')
			return False
		
		# check path is writable
		if not os.access(path, os.W_OK):
			log.error('You must have writing access permission!')
			return False
		
		if path[-1] != '/':
			path += '/'
		
		# apply path settings and confirm
		old = self.path
		self.path = path
		log.write('Working directory set to : '+self.path)
		
		# manage old path content
		confirm = input('move old working directory content into the new one (!!!overwriting risk!!!)? (empty or y = confirm)').strip()
		
		if confirm in [ '', 'y' ]:# content moved to the new path
			for f in os.listdir(old):
				movedir(old+f, path)
			log.write('«'+old+'» content have been moved into «'+self.path+'»')
			
		else:# content ignore
			log.write('«'+old+'» content haven\'t been moved!')
		
		if not os.path.exists(path+'source/'):
			os.mkdir(path+'source/')
		
		return True# confirm change
	
	
	
	
	
	
	
	
	
	
	
