#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''Export blender file scene info in XML, parse like in FileInfo class export xml'''
import bpy, sys, os
sys.path.append(os.path.abspath(sys.argv[4]+'/../../..'))
from usefullFunctions import XML

print('<?xml version="1.0" encoding="UTF-8"?>')
# export active scene name
print('<fileInfo active="'+XML.encode(bpy.context.screen.scene.name)+'">')

for name in bpy.data.scenes.keys():
	scene = bpy.data.scenes[name]
	#export all scene name, starting and ending frame
	print('  <scene name="'+XML.encode(name)+'" start="'+str(scene.frame_start)\
			+'" end="'+str(scene.frame_end)+'" fps="'+str(scene.render.fps)\
			+'" camera="'+str(scene.camera is not None)+'" />')

print('</fileInfo>')
