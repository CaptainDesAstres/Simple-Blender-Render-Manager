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
	
	
	
	
	
	def setChoice(self, log):
		'''choose between render the active scene or all the scene and between respect file resolution percentage or overwrite it'''
		scenes = len(self.scenes)
		
		# can't add empty task file
		if scenes == 0:
			log.error('  no scene in this file… Abort')
			return None
		
		# count only scene with camera and scene without 100% resolution setting
		scenesOW, scenesWithCam = 0, 0
		for s in self.scenes:
			if s.camera:
				scenesWithCam+=1
			if s.percent != 100:
				sceneOW+= 1
		
		# display a error message if no scene have camera
		if scenesWithCam == 0:
			log.error('  The scene(s) of this file have no camera to render from! Abort!')
			return None
		
		# no need to choose if there is only one scene in the file
		if scenesWithCam == 1:
			log.write('  Only one scene to render in file.')
			return True
		
		# get user choice
		log.menuIn('Scene Choice')
		while True:
			if scenesWithCam == scenes:
				print('There is '+str(scenes)+' scenes in this file. Do you want to:')
			else:
				print('There is '+str(scenes)+' scenes in this file but only '+str(scenesWithCam)+' have a camera set. Scene without camera will be ignore. Do you want to:')
			choice = input('''	1- Render all scenes
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
				if self.scenes[self.active].camera:
					log.write('  Set to render task active scene only')
					return False
				else:
					Log.error('  Impossible to render the active scene: no camera set! Abort!')
					return None
			
			log.error('unvalid choice')
			
	
	
	
	
	
	
	
	
	
