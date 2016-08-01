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
		'''method to see output path and access edition menu'''
		change = False
		log.menuIn('Output')
		
		while True:
			
			log.print()
			
			print('\n')
			self.print()
			
			print('''\n\n        \033[4mMenu :\033[0m
1- Edit path
2- Edit patterns
3- Switch overwrite mode
4- Change backup limit (only in «backup» overwriting mode)
0- Save And Quit

''')
			choice = input().strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				log.menuOut()
				return change
			elif choice == '1':
				# edit output path
				change = (self.editPath(log) or change)
			elif choice == '2':
				# edit output pattern
				change = (self.editPattern(log) or change)
			elif choice == '3':
				# switch overwriting mode
				change = (self.switchOverwrite(log) or change)
			elif choice == '4':
				# edit backup limit
				change = (self.editBackupLimit(log) or change)
			else:
				log.error('Unvalid menu index!', False)
	
	
	
	
	
	def editPath(self, log):
		'''method to manually edit output path'''
		log.menuIn('Edit Path')
		
		while True:
			
			log.print()
			
			#print current path and ask the new one
			print('\nCurrent output path : '+self.path)
			choice = input('\n\nwhat\'s the path to use ?(absolute path required, surround path by \' or " if it contains space)').strip()
			if choice == '':
				log.menuOut()
				return False
			
			
			# remove ' and/or "
			if choice[0] in ['\'', '"'] and choice[-1] == choice[0]:
				choice  = choice[1:len(choice)-1]
			
			# check it's absolute path
			if choice[0] != '/':
				log.error('The path must be absolute (begin by «/»)!')
				continue
			
			# check path exist 
			if not os.path.exists(choice):
				log.error('This path correspond to nothing!')
				continue
			
			# check path is a directory
			if not os.path.isdir(choice):
				log.error('This path don\'t correspond to a directory!')
				continue
			
			# check path is writable
			if not os.access(choice, os.W_OK):
				log.error('You don\'t have the permission to write in this directory!')
				continue
			
			if choice[-1] != '/':
				choice += '/'
			
			# apply path settings and confirm
			self.path = choice
			log.write('Output path set to : '+self.path)
			log.menuOut()
			return True
	
	
	
	
	
	
	
	
	
	
	
