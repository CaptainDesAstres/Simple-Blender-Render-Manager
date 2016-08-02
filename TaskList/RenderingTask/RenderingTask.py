'''A module to manage task rendering in blender'''
import bpy, sys, os, socket, time, threading
sys.path.append(os.path.abspath(sys.argv[4]+'/../../../..'))

def RenderingTask(task, preferences):
	task.running = True
	
	#scene = bpy.data.scenes[task.scene]
	#bpy.context.screen.scene = scene
	
	scene.render.use_stamp_time = True
	scene.render.use_stamp_date = True
	scene.render.use_stamp_render_time = True
	scene.render.use_stamp_frame = True
	scene.render.use_stamp_scene = True
	scene.render.use_stamp_camera = True
	scene.render.use_stamp_lens = True
	scene.render.use_stamp_filename = True
	scene.render.use_stamp_marker = True
	scene.render.use_stamp_sequencer_strip = True
	scene.render.use_stamp_note = True
	
	scene.render.use_file_extension = True
	scene.render.use_placeholder = True
	
	connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion.connect(('localhost', preferences.port))
	
	listen = threading.Thread(
				target = socketListener,
				args=(connexion, task) 
							)
	listen.start()
	
	try:
		run()
	except Exception as e:
		connexion.sendall( (task.uid+' debugMsg('+str(e)+') EOS').encode() )
	
	task.running = 'NOW'
	connexion.sendall( (task.uid+' VersionEnded EOS').encode() )
	
	listen.join()
	
	connexion.close()



def socketListener(soc, task):
	'''a method to manage signal send by the main process'''
	msg = ''
	soc.settimeout(0.5)
	while True:
		try:
			msg += soc.recv(1024).decode()
		except:
			pass # (socket timeout error)
		
		if task.running == 'NOW':
			break
		if msg[-4:] != ' EOS':
			continue
		else:
			messages = msg.split(' EOS')
			messages.pop()
			for m in messages:
				if m == task.uid+' stopAfterFrame()':
					task.running = 'until next frame'
				if m == task.uid+' stopAfterGroup()':
					task.running = 'until next group'
			msg = ''
	




def run(task, bpy, socket):
	'''Function to manage task rendering'''
		scene = bpy.context.screen.scene
		
		while scene.frame_current <= scene.frame_end \
					and task.running != 'until next frame':
			
			start = time.time()
			
			scene.render.filepath = task.log.getMainPath()\
									+logGroup.subpath\
									+(logGroup.naming.replace('####', str(scene.frame_current)))
			bpy.ops.render.render( write_still=True )
			
			endDate = datetime.datetime.today()
			computeTime = time.time() - start
			
			msg = task.uid+' ConfirmFrame('+logGroup.name\
					+','+str(scene.frame_current)+','+endDate.strftime('%d:%m:%Y:%H:%M:%S')\
					+','+str(computeTime)+') EOS'
			socket.sendall(msg.encode())
			
			scene.frame_current += 1




