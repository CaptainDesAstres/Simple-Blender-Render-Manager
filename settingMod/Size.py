#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage size settings representation'''
import xml.etree.ElementTree as xmlMod
import os, re

class Tiles:
	'''class to represent size settings'''
	
	
	def __init__(self, XYstr = None, xml= None):
		'''initialize size settings with default value or values extracted from an xml object'''
		if XYstr is not None:
			self.fromStr(XYstr)
		else:
			self.fromXml(xml)
	
	
	
	
	
	def fromStr(self, XYstr):
		'''initialize tiles sizes with default value'''
		XYstr = XYstr.split('x')
		self.X = int(XYstr[0].strip())
		self.Y = int(XYstr[1].strip())
	
	
	
	
	
	def check(XYstr):
		'''class method to check if a string well syntaxed to be used by Size.fromStr()'''
		return re.search(r'^\d{1,} *x *\d{1,}$',XYstr) is not None
		
	
	
	
	
	
	def fromXml(self, xml):
		'''initialize size with values extracted from an xml object'''
		self.X = int(xml.get('x'))
		self.Y = int(xml.get('y'))
	
	
	
	
	
	def toXmlAttr(self):
		'''export size into xml syntaxed attribute string'''
		return 'x="'+self.X+'" y="'+self.Y+'"'
	
	
	
	
	
	def toStr(self):
		'''A method to export settings in a simple string'''
		return str(self.X)+'x'+str(self.Y)
	
	
	
	
	
	def print(self):
		'''a method to display the size settings'''
		print(self.toStr(), sep='')
	
	
	
	
	
	
	
	
	
	
