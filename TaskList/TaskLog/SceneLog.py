#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage task scene  log'''
import xml.etree.ElementTree as xmlMod
from usefullFunctions import XML


class SceneLog:
	'''class to manage task scene log'''
	
	def __init__(self, xml = None, scene = None, task = None):
		'''initialize scene log object'''
		if xml is None:
			self.defaultInit(scene, task)
		else:
			self.fromXml(xml)
	
	
	
	
	
	
	def defaultInit(self, scene, task):
		'''initialize Scene log'''
		self.name
		self.path
		self.start
		self.end
		self.frames
		self.status
	
	
	
	
	
	def fromXml(self):
		'''initialize Scene log object with saved log'''
		self.name
		self.path
		self.start
		self.end
		self.frames
		self.status
	
	
	
	
	
	def toXml(self):
		'''export scene log into xml syntaxed string'''
	
	
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
	
	
	
	
	
	
	
	
