#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage list of all know version of Blender in the system'''
import os

class Blender:
	'''class dedicated to manage Blender path'''
	
	
	def __init__(self, xml= None):
		'''initialize Blender path on loading'''
		if xml is None:
			self.path = 'blender'
		else:
			self.path = xml.get('path')
	
	
	
	
	
	def toXml(self):
		'''export Blender path into xml syntaxed string'''
		
		return '  <blender path="'+self.path+'" />\n'
	
	
	
	
	
	def menu(self, log):
		'''method to see and change Blender path'''
		log.menuIn('Blender path')
		
		while True:
			# print log and actual Blender path
			log.print()
			print('\n            \033[4mBlender Path :\033[0m\n'+self.path+'\n\n')
			
			# treat given path
			new = input('New path? (empty to keep current)').strip()
			if new in [ '', 'q', '0' ]:
				log.menuOut() # quit preferences menu
				return False
			elif self.set(new, log):
				# check the path and save it
				log.menuOut() # quit preferences menu
				return True
	
	
	
	
	
	def set(self, path, log):
		'''a method to check and set a Blender path'''
		if path=='blender':
			self.path = 'blender'
			log.write('Blender path set to «blender».')
			return True
		
		# remove quote mark and apostrophe in first and last character
		if path[0] in ['\'', '"'] and path[-1] == path[0]:
			path  = path[1:len(path)-1]
		
		# check that the path is absolute: begin by '/'
		if path[0] != '/':
			log.error('The path must be absolute (begin by «/»)!')
			return False
		
		# check path exist 
		if not os.path.exists(path):
			log.error('This path correspond to nothing!')
			return False
		
		# check path is a file
		if not os.path.isfile(path):
			log.error('This path is not a file!')
			return False
		
		# check path is executable
		if not os.access(path, os.X_OK):
			log.error('This file is not executable or you don\'t have the permission to do it!')
			return False
		
		self.path = path
		log.write('Blender path set to «'+self.path+'».')
		return True
	
	
	
	
	
	
	
	
