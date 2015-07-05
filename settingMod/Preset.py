#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage preset'''
import xml.etree.ElementTree as xmlMod
from settingMod.Quality import *
from settingMod.BounceSet import *
from settingMod.Engine import *
from settingMod.Options import *
import os

class Preset:
	'''class to manage preset'''
	
	
	def __init__(self, xml= None):
		'''initialize preset with default value or values extracted from an xml object'''
		if xml is None:
			self.defaultInit()
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self):
		'''initialize preset with default value'''
		self.animation = -1
		self.quality = Quality()
		self.bounce = BounceSet()
		self.engine = Engine()
		self.options = Options()
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize preset with values extracted from an xml object'''
		self.animation = int(xml.get('animation'))
		self.quality = Quality(xml.find('quality'))
		self.bounce = BounceSet(xml.find('bounceSet'))
		self.engine = Engine(xml.find('engine'))
		self.options = Options(xml.find('options'))
	
	
	
	
	
	def toXml(self):
		'''export preset into xml syntaxed string'''
		txt = '<preset animation="'+str(self.animation)+'" >\n'
		
		txt += self.quality.toXml()
		
		txt += self.bounce.toXml()
		
		txt += self.engine.toXml()
		
		txt += self.options.toXml()
		
		txt += '</preset>\n'
		return txt
	
	
	
	
	
	def see(self, log, versions):
		'''menu to explore and edit preset settings'''
		change = False
		log.menuIn('Preset')
		
		while True:
			os.system('clear')
			log.print()
			
			self.print()
			
			print('''\n\n        Menu :
1- Edit Quality Settings
2- Edit Bounces Settings (Cycles)
3- Edit Rendering Options
4- Edit Animation Setting
9- Edit Engine Settings
0- Save and quit

''')
			
			choice = input('Action?').strip().lower()
			
			if choice in ['0', 'q', 'quit', 'cancel']:
				log.menuOut()
				return change
			elif choice == '1':
				change = (self.quality.see(log) or change)
			elif choice == '2':
				change = (self.bounce.see(log) or change)
			elif choice == '3':
				change = (self.options.see(log) or change)
			elif choice == '9':
				change = (self.engine.see(log, versions) or change)
			else:
				log.error('Unvalid menu choice', False)
		
	
	
	
	
	
	def print(self):
		'''a method to print preset'''
		self.quality.print()
		print('Animation : '+self.getAnimation())
		print()
		self.bounce.print()
		print()
		self.options.print()
		print()
		self.engine.print()
	
	
	
	
	
	
	
	
	
	
