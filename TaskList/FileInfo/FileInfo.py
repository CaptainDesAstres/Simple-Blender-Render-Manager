#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''manage blender file info'''
from TaskList.FileInfo.Scene import *
from usefullFunctions import XML

class FileInfo:
	'''contain blender file info'''
	
	def __init__(self, xml):
		'''load blender file info from xml'''
		# get active scene name
		self.active = XML.decode(xml.get('active'))
		
		# list all scene
		self.scenes = {}
		for scene in xml.findall('scene'):
			self.scenes[XML.decode(scene.get('name'))] = Scene(scene)
	
	
	
	
	
	def toXml(self):
		'''export blender file info in xml'''
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
			
		
	
	
	
	
	
	
	
	
	
