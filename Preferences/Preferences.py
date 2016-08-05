#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage preferences of Blender-Render-Manager'''
from save import *
from Preferences.Blender import *
from Preferences.Output import *

class Preferences:
	'''class to manage Blender-Render-Manager preferences'''
	
	
	def __init__(self, xml= None):
		'''load preferences object from XML or initialize default one'''
		if xml is None:
			self.defaultInit()
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self):
		'''initialize default preferences object'''
		
		self.blender = Blender() # blender application path
		self.output = Output() # working directory path
		self.port = 55814 # socket port to communicate with blender thread
		self.archiveLimit = 1000 # max number of task to keep in archive list
		self.logLimit = 100 # max number of session log file to keep
	
	
	
	
	
	def fromXml(self, xml):
		'''Load preferences from xml'''
		
		self.blender = Blender( xml.find('blender') )
		self.output = Output( xml.find('output') )
		self.port = int(xml.get('port'))
		self.archiveLimit = int(xml.get('archive'))
		self.logLimit = int(xml.get('log'))
	
	
	
	
	
	def toXml(self, preset = True, head = True):
		'''export preferences settings into xml syntaxed string'''
		xml = ''
		
		if head:
			xml += '<?xml version="1.0" encoding="UTF-8"?>\n'
		
		xml += '<preferences archive="'+str(self.archiveLimit)\
				+'" log="'+str(self.logLimit)+'" port="'+str(self.port)+'">\n'
		
		if preset:
			# export blender path
			xml += self.blender.toXml()
		
		# export output path
		xml+= self.output.toXml()
		
		xml += '</preferences>\n'
		
		return xml
	
	
	
	
	
	def menu(self, log, tasks):
		'''access function to set preferences'''
		log.menuIn('Preferences')
		change = False
		
		while True:
			log.print()
			self.print()
			
			choice = input('''\n    \033[4mPreferences Menu :\033[0m
1- Edit Blender Path
2- Edit Work Path
3- Edit Log Limit
4- Edit Archive Size Limit
5- Edit Socket Port
0- Save and quit

menu choice?''').strip().lower()
			
			#treat available actions
			if choice in ['0', 'q', 'quit', 'cancel']:# quit preferences menu
				log.menuOut()
				return
				
			elif choice == '1':# edit blender application path
				change = self.blender.menu(log)
				
			elif choice == '2':# edit working directory path
				change = self.output.menu(log)
				
			elif choice in ['3', '4']:# edit log or archive limit
				change = self.editLimit(log, choice == '3' )
				
			elif choice == '5':# edit socket port for blender thread communication
				change = self.editPort(log)
				
			else:
				log.error('Unknow request!', False)
			
			if change:# save when preferences have been changed
				change = False
				savePreferences(self)
				log.write('New preferences saved')
	
	
	
	
	
	def print(self):
		'''display preference settings'''
		print('Blender Path : '+self.blender.path,\
				'Work Path : '+self.output.path,\
				'Socket Port : '+str(self.port),\
				'Session Log Limit : '+str(self.logLimit),\
				'Archive Limit : '+str(self.archiveLimit),\
				sep='\n'
			)
	
	
	
	
	
	def editPort(self, log):
		'''A method to change the net port to communicate with blender instance'''
		log.menuIn('Edit Net Port')
		while True:
			log.print()
			
			choice = input('''

        Edit Net Port :

Current port :'''+str(self.port)+'''

Type the wanted port between 1024 and 65535 or q to quit or h for help :''').strip().lower()
			
			if choice in ['q', 'quit', 'cancel']:
				log.menuOut()
				return False
			
			if choice in ['h', 'help']:
				log.menuIn('Help')
				log.print()
				input('''

        Help :
When Blender Render Manager is running blender to render a picture, it communicate with Blender via a web socket to stay informed of the status. This setting is the port that the script use for the socket. be sure to use a port who is not used by another process.

enter to continue
''')
				log.menuOut()
				continue
			
			try:
				choice = int(choice)
			except ValueError:
				log.error('integer value expected!',False)
				continue
			
			if choice < 1024 or choice > 65535:
				log.error('the port value must be between 1024 and 65535!',False)
				continue
			
			self.port = choice
			log.write('the socket port is set to '+str(self.port))
			log.menuOut()
			return True
			
			
			
	
	
	
	
	
	def editLimit(self, log, logLim):
		'''edit log or archive limite'''
		if logLim:
			log.menuIn('Edit Log Limit')
			current = self.logLimit
		else:
			log.menuIn('Edit Archive Max Size')
			current = self.archiveLimit
		
		while True:
			log.print()
			
			choice = input('\n\nCurrent limit : '+str(current)+'\n\nNew limit (0 for unlimited, q to quit) : ').strip().lower()
			
			if choice in ['q', 'quit', 'cancel']:
				log.menuOut()
				return False
			
			try:
				choice = int(choice)
			except ValueError:
				log.error('Integer value expected!',False)
				continue
			
			if choice >= 0:
				if logLim:
					self.logLimit = choice
					log.write('Log limit set to '+str(self.logLimit))
				else:
					self.archiveLimit = choice
					log.write('Max archive size set to '+str(self.archiveLimit))
				log.menuOut()
				return True
			else:
				log.error('Expect a positive value!')
	
	
	
	
	
	
	
	
