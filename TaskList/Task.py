#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task settings'''
import xml.etree.ElementTree as xmlMod
import os
from usefullFunctions import *
from TaskList.FileInfo.FileInfo import *

class Task:
	'''class to manage task settings'''
	
	
	def __init__(self, path = None, scene = None, preset = None,\
					fileInfo = None, xml= None):
		'''initialize task object with default settings or saved settings'''
		if xml is None:
			self.defaultInit(path, scene, preset, fileInfo)
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self, path, scene, preset, fileInfo):
		'''initialize Task object with default settings'''
		self.path = path
		self.scene = scene
		self.preset = preset
		self.info = fileInfo
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize Task object with savedd settings'''
		self.path = xml.get('path')
		self.scene = xml.get('scene')
		self.preset = xml.get('preset')
		self.info = FileInfo(xml.find('fileInfo'))
	
	
	
	
	
	def toXml(self):
		'''export task settings into xml syntaxed string'''
		return '<task path="'+self.path+'" scene="'+self.scene+'" preset="'\
				+self.preset+'" >\n'\
				+self.info.toXml()\
				+'</task>\n'
		
	
	
	
	
	
	def menu(self, log, index, tasks, preferences):
		'''method to edit task settings'''
		log.menuIn('Task n°'+str(index))
		change = False
		
		while True:
			log.print()
			
			print('\n        Edit Task n°'+str(index)+' :')
			self.print()
			print('\n')
			print('''    Menu :
1- Change scene
2- Change preset
3- Edit preset
4- Active/desactive Renderlayer
5- Change list row
6- Erase task
0- Quit and save

''')
			
			
			choice= input('action : ').strip().lower()
			if choice in ['0', 'q', 'quit', 'cancel']:
				log.menuOut()# quit preferences menu
				return change
			elif choice == '1':
				scene = self.info.sceneChoice(log, allChoice = False)[0]
				if scene is not None:
					self.scene = scene
					log.write('Scene of task n°'+str(index)+' set to «'+self.scene+'»')
					change = True
			elif choice == '2':
				change = (self.presetChoice(log) or change)
			elif choice == '3':
				change = (preferences.presets.presets[self.preset].menu(log) or change)
			elif choice == '4':
				change = (self.info.scene[self.scene].renderlayerActivator(log) or change)
			elif choice == '5':
				change = (tasks.move(log, [index]) or change)
			elif choice == '6':
				change = (tasks.remove(log, [index]) or change)
			else:
				log.error('Unknow request!', False)
	
	
	
	
	
	def print(self):
		'''A method to print task information'''
		print('\n\nPath :          '+self.path)
		print('File Name :     '+self.path.split('/').pop())
		print('Scene :         '+self.scene)
		print('Preset :        '+self.preset+'\n')
		print('\033[4mActive Renderlayer :\033[0m')
		self.info.scenes[self.scene].printActiveRenderlayer()
		print('\n')
	
	
	
	
	
	def renamePreset(self, old, new):
		'''a method to rename used preset'''
		if self.preset == old:
			self.preset = new
	
	
	
	
	
	
	def erasePreset(self, preset):
		'''a method to stop using preset'''
		if self.preset == preset:
			self.preset = '[default]'
	
	
	
	
	
	def getRow(self):
		'''A method to get row to print task list'''
		name = self.path.split('/').pop()
		return columnLimit('  '+name, 25, 5)\
				+columnLimit('  '+self.scene, 25, 5)\
				+columnLimit('  '+self.preset, 25, 5)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
