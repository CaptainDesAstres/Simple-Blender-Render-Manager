#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage Quality settings'''
import xml.etree.ElementTree as xmlMod
from usefullFunctions import *
from Preferences.PresetList.Preset.OSA import *
from Preferences.PresetList.Preset.ValueType.Size import *
import os

class Quality:
	'''class to manage Quality settings'''
	
	
	def __init__(self, xml= None):
		'''initialize Quality settings with default value or values extracted from an xml object'''
		if xml is None:
			self.defaultInit()
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self):
		'''initialize Quality settings with default value'''
		self.pourcent = 100
		self.size = Size('1920x1080')
		self.samples = 1500
		self.simplify = None
		self.format = 'OPEN_EXR_MULTILAYER'
		self.OSA = OSA()
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize Quality settings with values extracted from an xml object'''
		node = xml.find('resolution')
		self.pourcent = int(node.get('pourcent'))
		self.size = Size(xml = node)
		self.samples = int(xml.find('samples').get('value'))
		if xml.find('simplify') is not None:
			self.simplify = int(xml.find('simplify').get('value'))
		else:
			self.simplify = None
		self.format = xml.find('format').get('value')
		self.OSA = OSA(xml.find('OSA'))
		
	
	
	
	
	
	def toXml(self):
		'''export Quality settings into xml syntaxed string'''
		txt = '<quality>\n'
		txt += '  <resolution pourcent="'+str(self.pourcent)+'" '+self.size.toXmlAttr()+' />\n'
		txt += '  <samples value="'+str(self.samples)+'" />\n'
		
		if self.simplify is not None:
			txt += '  <simplify value="'+str(self.simplify)+'" />\n'
		
		txt += '  <format value="'+self.format+'" />\n'
		
		txt += self.OSA.toXml()
		
		txt += '</quality>\n'
		return txt
	
	
	
	
	
	def menu(self, log):
		'''menu to explore and edit Quality settings settings'''
		change = False
		log.menuIn('Quality')
		
		while True:
			
			log.print()
			
			self.print()
			
			print('''\n\n        Menu :
1- Edit Resolution Size
2- Edit Pourcent Setting
3- Edit Cycles Samples
4- Edit Simplify Setting
5- Edit Format
6- Edit OSA settings (for Blender Render only)
0- Quit

''')
			
			choice = input('Action?').strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				log.menuOut()
				return change
			elif choice == '1':
				change = (self.size.edit(log, 'Resolution Size') or change)
			elif choice in ['2', '3']:
				change = (self.edit(log, int(choice)) or change)
			elif choice == '4':
				change = (self.editSimplify(log) or change)
			elif choice == '5':
				change = (self.editFormat(log) or change)
			elif choice == '6':
				change = (self.OSA.menu(log) or change)
			else:
				log.error('Unvalid menu choice', False)
		
	
	
	
	
	
	def print(self):
		'''a method to print preset'''
		print('Resolution :            '+self.size.toStr()+'@'+str(self.pourcent))
		print('Cycles Samples :        '+str(self.samples))
		print('Simplify :              '+self.getSimplify())
		print('Format :                '+self.format)
		self.OSA.print()
	
	
	
	
	
	def getSimplify(self):
		'''A method to get simplify setting'''
		if self.simplify is None:
			return 'Disabled'
		else:
			return str(self.simplify)+' subdiv'
	
	
	
	
	def edit(self, log, choice):
		'''A method to edit pourcent setting'''
		if choice == 2:
			log.menuIn('Edit Resolution Pourcent')
		else:
			log.menuIn('Edit Cycles Samples')
		
		while True:
			
			log.print()
			
			# print current setting and get new one
			if choice == 2:
				print('\n\n        Edit Pourcent :\nCurrent Pourcent : '+str(self.pourcent)+'\n')
				new = input('New pourcent setting?').strip().lower()
			else:
				print('\n\n        Edit Cycles Samples :\nCurrent Sammples : '+str(self.samples)+'\n')
				new = input('New Samples setting?').strip().lower()
			
			# exit menu
			if new in ['', 'q', 'quit', 'cancel']:
				log.menuOut()
				return False
			
			#check new setting
			try:
				new = int(new)
			except ValueError:
				log.error('New setting must be an integer.')
				continue
			
			if new < 0:
				log.error('New setting must be a positive integer.')
				continue
			
			# apply new setting and exit
			if choice == 2:
				self.pourcent = new
				log.write('Resolution pourcent setting is set to : '\
							+str(self.pourcent)+'%')
			else:
				self.samples = new
				log.write('Cycles samples set to : '+str(self.samples)+'%')
			log.menuOut()
			return True
		
	
	
	
	
	
	def editSimplify(self, log):
		'''A method to Edit Simplify settings'''
		log.menuIn('Edit Simplify settings')
		
		while True:
			
			log.print()
			
			# print current setting and get new one
			print('\n\n        Edit Simplify Settings :\nCurrent settings : '+self.getSimplify()+'\n')
			choice = input('New setting?').strip().lower()
			
			# exit menu
			if choice in ['', 'q', 'quit', 'cancel']:
				log.menuOut()
				return False
			
			#check new setting
			try:
				choice = int(choice)
			except ValueError:
				log.error('New setting must be an integer.')
				continue
			
			if choice < 0:
				log.error('New setting must be a positive integer.')
				continue
			
			if choice < 11:
				self.simplify = choice
			else:
				self.simplify = None
			log.write('Simplify set to : '+self.getSimplify())
			log.menuOut()
			return True
		
	
	
	
	
	
	def editFormat(self, log):
		'''A method to edit format settings'''
		formats = [
					'PNG', 
					'JPEG', 
					'OPEN_EXR', 
					'OPEN_EXR_MULTILAYER'
					]
		log.menuIn('Choose Output Format')
		
		while True:
			
			log.print()
			
			print('\n\n        Edit Output Format :\n\nCurrent format : '+self.format)
			
			indexPrintList(formats)
			
			choice = input('new format?').strip()
			
			if choice.lower() in ['', 'q', 'quit', 'cancel']:
				log.menuOut()
				return False
			
			try:
				choice = int(choice)
			except ValueError:
				log.error('An integer is expected!')
				continue
			
			if choice < 0 or choice >= len(formats):
				log.error('Out of choice range!')
				continue
			
			self.format = formats[choice]
			log.write('Output format is set to : '+self.format)
			log.menuOut()
			return True
	
	
	
	
	
	def apply(self, scene):
		'''apply settings to a blender scene object'''
		scene.render.resolution_percentage = self.pourcent
		scene.render.resolution_x = self.size.X
		scene.render.resolution_y = self.size.Y
		
		scene.cycles.use_square_samples = False
		scene.cycles.samples = self.samples
		
		if self.simplify is None:
			scene.render.use_simplify = False
		else:
			scene.render.use_simplify = True
			scene.render.simplify_subdivision_render
		
		scene.render.image_settings.file_format = self.format
		
		self.OSA.apply(scene)
	
	
	
	
	
	def getExtension(self):
		'''return file extension'''
		if self.format == 'PNG':
			return '.png'
		if self.format == 'JPEG':
			return '.jpg'
		return '.exr'
	
	
	
	
	
	
	
