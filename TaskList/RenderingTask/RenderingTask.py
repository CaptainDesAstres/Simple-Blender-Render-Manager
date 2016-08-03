'''A module to manage task rendering in blender'''
import bpy, sys, os, socket, time, threading
sys.path.append(os.path.abspath(sys.argv[4]+'/../../../..'))

def RenderingTask(task, preferences):
	task.running = True
	
	# create a socket to communicate with blender-render-manager
	connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion.connect(('localhost', preferences.port))
	listen = threading.Thread(
				target = socketListener,
				args=(connexion, task) 
							)
	listen.start()
	
	scenes = task.log.scenes
	for sceneLog in scenes:
		# select scene as active
		scene = bpy.data.scenes[sceneLog.name]
		bpy.context.screen.scene = scene
		
		# active all stamp info
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
		
		# active output option
		scene.render.use_file_extension = True
		scene.render.use_placeholder = True
		
		# render scene
		try:
			run(task, sceneLog, bpy, connexion, preferences )
		except Exception as e:
			connexion.sendall( (task.uid+' debugMsg('+str(e)+') EOS').encode() )
	
	# send end of rendering signal
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
	




def run(task, sceneLog, bpy, socket, preferences ):
	'''Function to manage task rendering'''
	# set output path
	scene = bpy.context.screen.scene
	scene.render.filepath = preferences.output.path+'render/'\
								+task.info.name+'/'\
								+scene.name+'/####'
	
	for scene.frame_current in range(scene.frame_start, scene.frame_end+1):
		
		if task.running != 'until next frame':
			break
		
		# check if frame have already been rendered
		if sceneLog.frameDone(scene.frame_current):
			continue
		
		start = time.time()
		
		# render the frame
		bpy.ops.render.render( write_still=True )
		
		endDate = datetime.datetime.today()
		computeTime = time.time() - start
		
		# report frame rendering to Blender Render Manager thread
		msg = task.uid+' ConfirmFrame('+logGroup.name\
				+','+str(scene.frame_current)+','+endDate.strftime('%d:%m:%Y:%H:%M:%S')\
				+','+str(computeTime)+') EOS'
		socket.sendall(msg.encode())
		




