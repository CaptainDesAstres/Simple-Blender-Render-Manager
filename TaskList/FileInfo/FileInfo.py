#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage blender file info'''
import xml.etree.ElementTree as xmlMod
from TaskList.FileInfo.Scene import *
from usefullFunctions import XML
import os

class FileInfo:
	'''class to manage blender file info'''
	
	
	def __init__(self, xml):
		'''initialize blender file info with default settings or saved settings'''
		self.fromXml(xml)
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize blender file info with savedd settings'''
		self.active = XML.decode(xml.get('active'))
		self.scenes = {}
		for scene in xml.findall('scene'):
			self.scenes[scene.get('name')] = Scene(scene)
	
	
	
	
	
	def toXml(self):
		'''export blender file info into xml syntaxed string'''
		xml = '  <fileInfo active="'+XML.encode(self.active)+'">\n'
		
		for scene in self.scenes.values():
			xml += scene.toXml()
		
		xml += '  </fileInfo>\n'
		return xml
	
	
	
	
	
	def sceneChoice(self, log, allChoice = True):
		'''a methode to choose the scene mode'''
		scenes = list(self.scenes.keys())
		scenes.sort(key = str.lower)
		
		if len(scenes) == 0:
			log.error('  no scene in this file… Abort')
			return None
		
		if len(scenes) == 1:
			log.write('  Only one scene in file. All scene will be rendered.')
			return True
		
		log.menuIn('Scene Choice')
		while True:
			choice = input('there is '+str(len(scenes))+''' scenes in this file. Do you want to:
	1- Render all scenes
	2- Render active scene «'''+self.active+'''»
	0- Abort''').strip().lower()
			
			if choice in [ '', 'q', '0' ]:
				log.menuOut()
				log.write('  Abort task adding')
				return None
			elif choice == '1':
				log.menuOut()
				log.write('  Set to render all task scene')
				return True
			elif choice == '2':
				log.menuOut()
				log.write('  Set to render task active scene only')
				return False
			else:
				log.error('unvalid choice')
			
		
	
	
	
	
	
	
	
	
	
