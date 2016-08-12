'''Rendering task in blender'''
import bpy, sys, os, socket, time, datetime, threading
sys.path.append(os.path.abspath(sys.argv[4]+'/../../../..'))

def RenderingTask(task, preferences):
	'''rendering each scene of the task'''
	# Create a socket to communicate with blender-render-manager
	connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion.connect(('localhost', preferences.port))
	# create a listener
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
			run(task, sceneLog, connexion, preferences )
		except Exception as e:
			connexion.sendall( (task.uid+' debugMsg('+str(e)+') EOS').encode() )
		
		# stop rendering after this scene if user request it
		if task.status in ['until next scene', 'until next frame']:
			break
	
	# report that the rendering is finish
	task.status = 'FINISH'
	connexion.sendall( (task.uid+' TaskEnded EOS').encode() )
	
	listen.join()# stop the socket listener thread
	connexion.close()
	bpy.ops.wm.quit_blender()



def socketListener(soc, task):
	'''treat main process request'''
	msg = ''
	soc.settimeout(0.5)
	print('listener start')
	while True:
		try:# get socket messages
			msg += soc.recv(1024).decode()
		except:
			pass # (socket timeout error)
		
		if task.status == 'FINISH':
			break# the task is finihed, listener must be stoped
		
		if msg[-4:] != ' EOS':
			print('partial message«'+msg+'»')
			continue# loop until the message is complete
			
		else:
			print('complete message«'+msg+'»')
			messages = msg.split(' EOS')
			messages.pop()# pop empty last element
			
			for m in messages:
				if m == task.uid+' stopAfterFrame()':# stop after current frame request
					task.status = 'until next frame'
					
				if m == task.uid+' stopAfterScene()':# stop after current scene request
					task.status = 'until next scene'
			
			msg = ''# initialize for new message





def run(task, sceneLog, socket, preferences ):
	'''render current scene'''
	scene = bpy.context.screen.scene
	
	# get scene output path
	scPath = preferences.output.path+'render/'\
								+task.name+'/'\
								+scene.name+'/'
	
	for scene.frame_current in range(scene.frame_start, scene.frame_end+1):
		# respect «stop after previous frame» request
		if task.status == 'until next frame':
			break
		
		# determine frame rendering path and ensure the frame isn't already rendered
		scene.render.filepath = scPath + str(scene.frame_current).rjust(4,'0')
		frPath = scene.render.filepath+scene.render.file_extension
		if os.path.exists(frPath) or sceneLog.frameDone(scene.frame_current):
			continue
		
		start = time.time()
		
		# render the frame
		try:
			bpy.ops.render.render( write_still=True )
		except Exception as e:
			socket.sendall( (task.uid+' debugMsg('+str(e)+'[file «'+task.name\
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
		




