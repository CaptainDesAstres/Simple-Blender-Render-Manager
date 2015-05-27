import bpy

print('<?xml version="1.0" encoding="UTF-8"?>')
print('<preferences>')
for name in bpy.data.scenes.keys():
	scene = bpy.data.scenes[name]
	print('\t<scene name="'+name+'">')
	print('\t\t<resolution x="'+str(scene.render.resolution_x)+'" y="'+str(scene.render.resolution_y)+'" proportion="'+str(scene.render.resolution_percentage)+'" />')
	print('\t</scene>')
print('</preferences>')
