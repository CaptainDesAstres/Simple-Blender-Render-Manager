'''Rendering task in blender'''
import bpy, sys, os, socket, time, datetime, threading
sys.path.append(os.path.abspath(sys.argv[4]+'/../../../..'))

def RenderingTask(task, preferences):
	# Create a socket to communicate with blender-render-manager
	connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion.connect(('localhost', preferences.port))
	# creat a listener
	listen = threading.Thread(
				target = socketListener,
				args=(connexion, task) 
							)
	listen.start()
	
	scenes = task.log.scenes # (contain only scene that must be render)
	for sceneLog in scenes:# render each scene
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
		
		# active output file option
		scene.render.use_file_extension = True
		scene.render.use_placeholder = True
		
		# render scene and report any error
		try:
			run(task, sceneLog, bpy, connexion, preferences )
		except Exception as e:
			connexion.sendall( (task.uid+' debugMsg('+str(e)+') EOS').encode() )
		
		# stop rendering after this scene if user request it
		if task.running == 'until next scene':
			break
	
	# report that the rendering is finish
	task.running = 'NOW'
	connexion.sendall( (task.uid+' TaskEnded EOS').encode() )
	
	listen.join()# stop the socket listener thread
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
				if m == task.uid+' stopAfterScene()':
					task.running = 'until next scene'
			msg = ''
	




def run(task, sceneLog, bpy, socket, preferences ):
	'''Function to manage task rendering'''
	# set output path
	scene = bpy.context.screen.scene
	path = preferences.output.path+'render/'\
								+task.log.name+'/'\
								+scene.name+'/'
	
	for scene.frame_current in range(scene.frame_start, scene.frame_end+1):
		
		if task.running == 'until next frame':
			break
		
		# check if frame have already been rendered
		if sceneLog.frameDone(scene.frame_current):
			continue
		
		scene.render.filepath = path+str(scene.frame_current).rjust(4,'0')
		
		start = time.time()
		
		# render the frame
		try:
			bpy.ops.render.render( write_still=True )
		except Exception as e:
			socket.sendall( (task.uid+' debugMsg('+str(e)+'[file «'+task.log.name\
						+'» scene «'+scene.name+'»  frame '\
						+str(scene.frame_current)+']) EOS').encode() )
			break
		
		
		endDate = datetime.datetime.today()
		computeTime = time.time() - start
		
		# report frame rendering to Blender Render Manager thread
		msg = task.uid+' ConfirmFrame('+scene.name\
				+','+str(scene.frame_current)+','+endDate.strftime('%d:%m:%Y:%H:%M:%S')\
				+','+str(computeTime)+') EOS'
		socket.sendall(msg.encode())
		




