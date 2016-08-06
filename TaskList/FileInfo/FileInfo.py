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
	
	
	
	
	
	def sceneChoice(self, log):
		'''choose between render the active scene or all the scene'''
		scenes = len(self.scenes)
		
		# can't add empty task file
		if scenes == 0:
			log.error('  no scene in this file… Abort')
			return None
		
		# no need to choose if there is only one scene in the file
		if scenes == 1:
			log.write('  Only one scene to render in file.')
			return True
		
		# get user choice
		log.menuIn('Scene Choice')
		while True:
			choice = input('there is '+str(scenes)+''' scenes in this file. Do you want to:
	1- Render all scenes
	2- Render active scene «'''+self.active+'''»
	0- Abort''').strip().lower()
			
			# quit and abort task adding
			if choice in [ '', 'q', '0' ]:
				log.menuOut()
				log.write('  Abort task adding')
				return None
			
			# quit and render all scene
			if choice == '1':
				log.menuOut()
				log.write('  Set to render all task scene')
				return True
			
			# quit and render only active scene
			if choice == '2':
				log.menuOut()
				log.write('  Set to render task active scene only')
				return False
			
			log.error('unvalid choice')
			
		
	
	
	
	
	
	
	
	
	
