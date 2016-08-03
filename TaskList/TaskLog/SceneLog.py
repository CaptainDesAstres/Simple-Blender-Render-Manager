#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task scene  log'''
import xml.etree.ElementTree as xmlMod
from TaskList.TaskLog.FrameLog import *
from usefullFunctions import XML


class SceneLog:
	'''class to manage task scene log'''
	
	pageSize = 15
	
	def __init__(self, xml = None, scene = None, task = None, pref = None):
		'''initialize scene log object'''
		if xml is None:
			self.defaultInit(scene, task, pref)
		else:
			self.fromXml(xml)
	
	
	
	
	
	
	def defaultInit(self, scene, task, pref):
		'''initialize Scene log'''
		self.name = scene
		self.start = task.info.scene[scene].start
		self.end = task.info.scene[scene].end
		self.frames = []
		self.status = 'ready to start'
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize Scene log object with saved log'''
		self.name = XML.decode(xml.get('name'))
		self.start = int(xml.get('start'))
		self.end = int(xml.get('end'))
		self.status = xml.get('status')
		
		self.frames = []
		for node in xml.findall('frame'):
			self.frames.append(\
					FrameLog( xml = node )\
					)
	
	
	
	
	
	def toXml(self):
		'''export scene log into xml syntaxed string'''
		xml = '<scene name="'+XML.encode(self.name)\
				+'" start="'+str(self.start)\
				+'" end="'+str(self.end)\
				+'" status="'+self.status+'" >\n'
		
		for f in self.frames:
			xml += f.toXml()
		
		xml += '</scene>\n'
		return xml
	
	
	
	
	
	def menu(self, log ):
		'''see detail of the Scene rendering'''
		log.menuIn('«'+self.name+'» scene details')
		
		page = 0
		count = len(self.frames)
		pageMax = round(count/self.pageSize)
		if count - pageMax * self.pageSize <=0:
			pageMax -= 1
		
		while True:
			log.print()
			
			print('\n\n        «'+self.name+'» group details :\n')
			self.print(page)
			
			choice = input('\n\nh for help').strip().lower()
			
			if choice in ['cancel', 'q', 'quit']:
				log.menuOut()
				return
			elif choice in ['h', 'help']:
				log.menuIn('Help')
				input('''
+ and -          scroll to see more frame
u and d          same
up and down      same
t and b          scroll to Top or Bottom of frame list
a frame number   scroll to see the frame of this number
q                quit group log
press enter to continu''')
				log.menuOut()
				
			elif choice in ['', '+', 'down', 'd']:
				page += 1 
				if page > pageMax:
					if choice != '':
						page = pageMax
					else:
						page = 0
				
			elif choice in ['-', 'up', 'u']:
				page -= 1 
				if page < 0:
					page = 0
				
			elif choice in ['t', 'top']:
				page = 0
				
			elif choice in ['b', 'bottom']:
				page = pageMax
				
			else:
				try:
					choice = int(choice)
				except:
					log.error('Unvalid action «'+choice+'» !', False)
					continue
				
				choice -= self.start
				if choice < 0 :
					choice = 0
				elif choice > count:
					choice = count
				page = int(choice / self.pageSize)
	
	
	
	
	
	def print(self, page = 0):
		'''A method to print Scene log'''
		total = self.end - self.start + 1
		remain = total - len(self.frames)
		
		print('Status          : '+self.status)
		
		print('\nRendered / total (remaining) : '+str(len(self.frames))+' / '\
				+str(total)+'     ( remain '+str(remain)+' frames )')
		print('Average rendering time : '+str(self.average())+' sec')
		
		if len(self.frames) > 0:
			print('Extract ('+str(page*self.pageSize+1)+' to '\
				+str((page+1)*self.pageSize)+' of '+str(len(self.frames))+') : ')
			print('Frame n°     rendering Date                 rendering time in seconds')
			for fr in self.frames[page*self.pageSize:(page+1)*self.pageSize]:
				fr.print()
		else:
			print('\n        No rendered frame')
	
	
	
	
	
	def runMenuPrint(self, index = None):
		'''display rendering progress during run mode '''
		total = self.end - self.start + 1
		
		if index is not None:
			index = str(index)+'-  '
		else:
			index = '╚═ '
		
		print(index+'«'+self.name+'» scene : '+str(len(self.frames))+'/'+str(total)\
					+' frames, '+str(total - len(self.frames))\
					+' remaining frames,\n     Average time by frame : '\
					+str(self.average())\
					)
	
	
	
	
	
	def average(self):
		'''return frame average rendering time'''
		if len(self.frames)>0:
			count = 0
			time = 0
			for f in self.frames:
				count += 1
				time += f.computingTime
			average = time / count
			return average
		else:
			return 0.0
	
	
	
	
	
	def remaining(self):
		'''return the count of frames that don't have been rendered yet'''
		return (self.end - self.start + 1 - len(self.frames) )
	
	
	
	
	
	def confirmFrame(self, frame, date, computingTime):
		'''add frame rendering log confirmation to the scene'''
		self.frames.append(
							FrameLog(
									frame = frame,
									date = date,
									computingTime = computingTime
									) 
							)
	
	
	
	
	
	
	
	
