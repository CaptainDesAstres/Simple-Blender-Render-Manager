#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''manage blender file scene info'''
from usefullFunctions import XML

class Scene:
	'''contain blender file scene info'''
	
	def __init__(self, xml):
		'''load scene info'''
		self.name = XML.decode(xml.get('name'))
		self.start = int(xml.get('start'))
		self.end = int(xml.get('end'))
		self.fps = int(xml.get('fps'))
		self.camera = bool(xml.get('camera'))
		self.percent = int(xml.get('pencent'))
	
	
	
	
	
	def toXml(self):
		'''export blender scene info in xml'''
		return '    <scene name="'+XML.encode(self.name)+'" start="'+str(self.start)\
			+'" end="'+str(self.end)+'" fps="'+str(self.fps)\
			+'" camera="'+str(self.camera)+'" percent="'+str(self.percent)+'"/>\n'
	
	
	
	
	
	
