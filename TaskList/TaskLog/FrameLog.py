#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''Frame rendering log'''
import datetime
from usefullFunctions import *


class FrameLog:
	'''frame rendering log'''
	
	
	def __init__(self, xml = None, 
					frame = None,
					date = None,
					computingTime = None):
		'''load frame info'''
		
		if xml is None:
			self.defaultInit(frame, date, computingTime)
		else:
			self.fromXml(xml)
	
	
	
	
	
	def defaultInit(self, frame, date, computingTime):
		'''load frame info'''
		self.frame = frame # frame number
		self.date = date # rendering date
		self.computingTime = computingTime # rendering time
	
	
	
	
	
	def fromXml(self, xml):
		'''load frame info from xml'''
		self.frame = int(xml.get('frame'))
		self.date = datetime.datetime.fromtimestamp(float(xml.get('date')))
		self.computingTime = float(xml.get('computingTime'))
	
	
	
	
	
	def toXml(self):
		'''export in xml'''
		return '<frame frame="'+str(self.frame)\
				+'" date="'+str(int(self.date.timestamp()))\
				+'" computingTime="'+str(self.computingTime)+'" />'
		
	
	
	
	
	
	def print(self):
		'''Display task frame rendering log'''
		print(self.saveOutput())
	
	
	
	
	
	def saveOutput(self):
		'''Output to save in final rendering log file'''
		return ('\n ╚═ '+columnLimit((str(self.frame)), 9, sep = '')\
			 +self.date.strftime('%d/%m/%Y at %H:%M')\
			 +'            '+str(round(self.computingTime, 2)) )
	
	
	
	
	
