#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage working path'''
import xml.etree.ElementTree as xmlMod
import os, re
from shutil import rmtree as rmdir
from usefullFunctions import indexPrintList, XML

class Output:
	'''class to manage working path'''
	
	
	def __init__(self, xml= None):
		'''initialize output path with default value or values extracted from an xml object'''
		if xml is None:
			if not os.path.exists('/home/'+os.getlogin()+'/.BlenderRenderManager/render'):
				os.mkdir('/home/'+os.getlogin()+'/.BlenderRenderManager/work')
			self.path = '/home/'+os.getlogin()+'/.BlenderRenderManager/work/'
		else:
			self.fromXml(xml)
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize output path with value extracted from an xml object'''
		self.path = xml.get('path')
	
	
	
	
	
	def toXml(self):
		'''export output path into xml syntaxed string'''
		return '<output path="'+XML.encode(self.path)+'" />\n'
	
	
	
	
	
	def menu(self, log):
		'''method to see and edit output path'''
		log.menuIn('Output')
		
		while True:
			log.print()
			print('\n')
			
			print('Work Path :\n'+self.path+'\n\n new path? (empty to keep current)')
			
			new = input().strip()
			
			if new in [ '', '0', 'q' ]:
				log.menuOut()
				return False
			elif self.set(new, log) :
				log.menuOut()
				return True
	
	
	
	
	
	def set(self, path, log):
		'''method to edit output path'''
		
		# remove ' and/or "
		if path[0] in ['\'', '"'] and path[-1] == path[0]:
			path  = path[1:len(path)-1]
		
		# check if it's absolute path
		if path[0] != '/':
			log.error('The path must be absolute (begin by «/»)!')
			return False
		
		# check path exist 
		if not os.path.exists(path):
			log.error('This path correspond to nothing!')
			return False
		
		# check path is a directory
		if not os.path.isdir(path):
			log.error('This path don\'t correspond to a directory!')
			return False
		
		# check path is writable
		if not os.access(path, os.W_OK):
			log.error('You don\'t have the permission to write in this directory!')
			return False
		
		if path[-1] != '/':
			path += '/'
		
		# apply path settings and confirm
		self.path = path
		log.write('Work path set to : '+self.path)
		return True
	
	
	
	
	
	
	
	
	
	
	
