#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage list of all know version of Blender in the system'''
import xml.etree.ElementTree as xmlMod
import re, os
from usefullFunctions import XML

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
	
	
	
	
	
	def menu(self, log, preferences):
		'''method to see and change Blender path'''
		log.menuIn('Blender path')
		
		
		# print log and actual Blender path
		
		log.print()
		
		
		print('\n            \033[4mBlender Path :\033[0m\n')
		print(self.path)
		
		print('''new path? (empty to keep actual)''')
		
		
		# treat given path
		new = input('menu?').strip().lower()
		if new == '':
			log.menuOut() # quit preferences menu
			return False
		else:
			# check the path and save it
			log.menuOut() # quit preferences menu
			return self.set(new, log)
	
	
	
	
	
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
		if not os.path.isfile(choice):
			log.error('This path is not a file!')
			return False
		
		# check path is executable
		if not os.access(choice, os.X_OK):
			log.error('This file is not executable or you don\'t have the permission to do it!')
			return False
		
		self.path = path
		log.write('Blender path set to «'+self.path+'».')
		return True
	
	
	
	
	
	
	
	
