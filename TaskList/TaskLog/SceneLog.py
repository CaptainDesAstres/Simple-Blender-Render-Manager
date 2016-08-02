#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task scene  log'''
import xml.etree.ElementTree as xmlMod
from TaskList.TaskLog.FrameLog import *
from usefullFunctions import XML


class SceneLog:
	'''class to manage task scene log'''
	
	def __init__(self, xml = None, scene = None, task = None, pref):
		'''initialize scene log object'''
		if xml is None:
			self.defaultInit(scene, task, pref)
		else:
			self.fromXml(xml)
	
	
	
	
	
	
	def defaultInit(self, scene, task, pref):
		'''initialize Scene log'''
		self.name = scene
		
		fileName = task.path.split('/').pop().split('.')
		fileName.pop()
		fileName = fileName.join('.')
		self.path = pref.output.path+'render/'+fileName+'/'+scene+'/'
		
		self.start = task.info.scene[scene].start
		self.end = task.info.scene[scene].end
		self.frames = []
		self.status = 'ready to start'
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize Scene log object with saved log'''
		self.name = XML.decode(xml.get('name'))
		self.path = XML.decode(xml.get('path'))
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
				+'" path="'+XML.encode(self.path)\
				+'" start="'+str(self.start)\
				+'" end="'+str(self.end)\
				+'" status="'+self.status+'" >\n'
		
		for f in self.frames:
			xml += f.toXml()
		
		xml += '</scene>\n'
		return xml
	
	
	
	
	
	def menu(self):
		'''see detail of the Scene rendering'''
		
	
	
	
	
	
	def print(self):
		'''A method to print Scene log'''
	
	
	
	
	
	def runMenuPrint(self):
		'''display rendering progress during run mode '''
	
	
	
	
	
	def average(self):
		'''return frame average rendering time'''
	
	
	
	
	
	def remaining(self):
		'''return the count of frames that don't have been rendered yet'''
	
	
	
	
	
	def confirmFrame(self):
		'''add frame rendering log confirmation to the scene'''
	
	
	
	
	
	def checkFrames(self):
		'''check for each frame that have been claimed as rendered if there is really a file corresponding to it'''
	
	
	
	
	
	
	
	
