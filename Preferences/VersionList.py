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
			self.path = xml.find('blender').get('path')
	
	
	
	
	
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
			return self.set(new)
	
	
	
	
	
	def set(self, path):
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
	
	
	
	
	
	def addAuto(self, log):
		'''a method to automatically add to the list numerous Blender version that is located in the same directory'''
		log.menuIn('Automatically Add Versions')
		
		while True:
			# print log 
			
			log.print()
			print('\n\nAll Blender version directory must be directly in a same directory. Script will not recursivly search for blender version')
			
			# get new version path
			choice= input('\nPath of the main directory?').strip()
			
			if choice == '':# quit
				log.menuOut()
				return False
			
			# remove quote mark and apostrophe in first and last character
			if choice[0] in ['\'', '"'] and choice[-1] == choice[0]:
				choice  = choice[1:len(choice)-1]
			
			# check that the path is absolute: begin by '/'
			if choice[0] != '/':
				log.error('The path must be absolute (begin by «/»)!')
				continue
			
			# check path exist 
			if not os.path.exists(choice):
				log.error('This path correspond to nothing!')
				continue
			
			# check path is a file
			if not os.path.isdir(choice):
				log.error('This path is not a directory!')
				continue
			
			path = choice
			if path[-1] != '/':
				path += '/'
			subdirectories = os.listdir(path)
			for sub in subdirectories:
				
				# check if ther is a blender version in this directory
				versionPath = path+sub+'/blender'
				if os.path.isdir(path+sub)\
						and os.path.exists(versionPath)\
						and os.path.isfile(versionPath)\
						and os.access(versionPath, os.X_OK):
					
					# get Blender version
					version = os.popen('"'+versionPath+'" -b -P "'+os.path.realpath(__file__+'/..')+'/getter/getBlenderVersion.py" ').read()
					version = re.search(r'<\?xml(.|\n)*</root>',version).group(0)
					version = xmlMod.fromstring(version).find('version').get('version')
					
					# generate an alias
					alias = 'Blender ('+version+')'
					if alias in self.list.keys():
						i = 0
						while alias+'('+str(i)+')' in self.list.keys():
							i+=1
						alias = alias+'('+str(i)+')'
					
					# add to the list
					self.list[alias] = versionPath
					log.write('('+alias+' : '+versionPath+') Blender version added to list')
			
			log.menuOut()
			return True
			
	
	
	
	
	
	def rename(self, log, preferences):
		'''display a menu to rename version in the list'''
		log.menuIn('Rename Version')
		
		# choose version
		oldAlias = self.choose(log)
		if oldAlias is None:
			return False
		
		while True:
			
			log.print()
			
			print('\n\n        \033[4mRename version :\033[0m')
			print(oldAlias+'\n    '+self.list[oldAlias])
			
			choice = input('\nNew name :').strip()
			
			if choice == '':
				log.menuOut()
				return False
			
			if choice in self.list.keys():
				log.error('This alias name is already use by another version.')
				continue
			
			self.list[choice] = self.list[oldAlias]
			self.list.pop(oldAlias)
			if self.default == oldAlias:
				self.default = choice
			
			preferences.presets.renameBlenderVersion( oldAlias, choice)
			
			log.write(oldAlias+' version rename in '+choice+'.')
			log.menuOut()
			return True
	
	
	
	
	
	def choose(self, log, std = False, default = False):
		'''display a menu to choose a version to working on'''
		log.menuIn('Choose Version')
		
		while True:
			
			log.print()
			
			print('\n\n')
			keys = self.print(True, std, default)
			choice = input('\nIndex of the version that you want to use :').strip()
			
			if choice == '':
				log.menuOut()
				return None
			
			try:
				choice = int(choice)
			except ValueError:
				log.error('Unvalid version choice : must be an irteger or an empty string')
				continue
			
			if choice >= 0 and choice < len(keys):
				log.menuOut()
				return keys[choice]
			else:
				log.error('Unvalid version choice : bad index.')
				continue
	
	
	
	
	
	def remove(self, log, preferences):
		'''A method to manually remove version from the list'''
		log.menuIn('Remove Version')
		
		# choose version
		alias = self.choose(log)
		if alias is None:
			log.menuOut()
			return False
		
		
		log.print()
		
		print('\n\n        \033[4mRemove version :\033[0m')
		print(alias+'\n    '+self.list[alias])
		
		
		if self.default == alias:
			print('\n\033[31mthis is actually the default version. if you erase it, default version will be set to de blender standard command.\033[0m')
		versionUsed = preferences.presets.useBlenderVersion(alias)
		if versionUsed:
			print('\n\033[31mThis version is actually used by some preset. If you erase it, the preset will automatically be changed to use default version.\033[0m')
		choice = input('\nDo you realy want to erase this version (y)?').strip().lower()
		
		
		
		if choice in ['y', 'yes']:
			self.list.pop(alias)
			if self.default == alias:
				self.default = 'Standard Blender'
			if versionUsed:
				preferences.presets.eraseBlenderVersion(alias)
			log.write('Remove "'+alias+'" version.')
			log.menuOut()
			return True
		log.menuOut()
		return False
	
	
	
	
	
	
	def chooseDefault(self, log):
		'''A method to choose the default version to use'''
		log.menuIn('Choose Default Version')
		
		# choose version
		alias = self.choose(log, True)
		
		if alias is None:
			log.menuOut()
			return False
		
		self.default = alias
		log.write('Default version set to "'+self.default+'" version.')
		log.menuOut()
		return True
	
	
	
	
	
	def getDefaultPath(self):
		'''a method to get the path of the default version'''
		return self.getVersionPath(self.default)
	
	
	
	
	
	def getVersionPath(self, versionName):
		'''a method to get the path of a version'''
		if versionName == '[default]':
			versionName = self.default
		path = self.list[versionName]
		if path != 'blender':
			path = '"'+path+'"'
		return path
		
	
	
	
	
	
	
	
