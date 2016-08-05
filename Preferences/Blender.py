#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage Blender application path'''
import os

class Blender:
	'''class dedicated to manage Blender path'''
	
	
	def __init__(self, xml= None):
		'''load or initialize Blender path'''
		if xml is None:
			self.path = 'blender'
		else:
			self.path = xml.get('path')
	
	
	
	
	
	def toXml(self):
		'''export Blender path into xml syntaxed string'''
		
		return '  <blender path="'+self.path+'" />\n'
	
	
	
	
	
	def menu(self, log):
		'''edit Blender path'''
		log.menuIn('Blender path')
		
		while True:
			# print log and current Blender path and get a new one
			log.print()
			new = input('\n            \033[4mBlender Path :\033[0m\n'\
					+self.path+'\n\n\nNew path? (empty to keep current)'
					).strip()
			
			# treat given path
			if new in [ '', 'q', '0' ]:
				log.menuOut() # quit preferences menu
				return False
			elif self.set(new, log):# check the path and save it
				log.menuOut() # return to preferences menu
				return True
	
	
	
	
	
	def set(self, path, log):
		'''confirm Blender path and save it'''
		if path=='blender':# auto accept «blender» default command
			self.path = 'blender'
			log.write('Blender path set to «blender».')
			return True
		
		# remove first and last quote mark or apostrophe
		if path[0] in ['\'', '"'] and path[-1] == path[0]:
			path  = path[1:len(path)-1]
		
		# ensure it's an absolute path
		if path[0] != '/':
			log.error('It must be an absolute path (begining by «/»)!')
			return False
		
		# ensure path exist 
		if not os.path.exists(path):
			log.error('This path correspond to nothing!')
			return False
		
		# ensure path is a file
		if not os.path.isfile(path):
			log.error('This path is not a file!')
			return False
		
		# ensure the file is executable
		if not os.access(path, os.X_OK):
			log.error('This file is not an executable (or you don\'t have the permission to execute it)!')
			return False
		
		# save as new blender path
		self.path = path
		log.write('Blender path set to «'+self.path+'».')
		return True
	
	
	
	
	
	
	
	
