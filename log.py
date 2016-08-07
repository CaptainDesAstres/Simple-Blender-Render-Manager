#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''module to manage script log'''
import os

class Log:
	'''a class to manage all script output except menuing. must be print to each new page.'''
	
	def __init__(self, start, init):
		'''initialize session log (object and file)'''
		self.log = init # log text content
		
		self.logFile = open(os.getcwd()+'/log/session '+start+'.log','w')
		self.logFile.write(self.log)
		
		self.write('Log file created.\n')
		
		self.menu = []
		self.runMenu = None
	
	
	
	
	def __del__(self):
		'''close the log file when the object is deleted'''
		self.logFile.close()
		del(self.log)
		del(self.logFile)
	
	
	
	
	def __str__(self):
		'''return all log in a string form'''
		return self.log
	
	
	
	
	def print(self, menu = True):
		'''print the log'''
		os.system('clear')# clear terminal output
		print(self.log)# print log content
		if menu :
			self.printMenu()# print current menu location
	
	
	
	
	def write(self, txt, sep = '\n'):
		'''add lines to the log text and the log file'''
		self.logFile.write(txt+sep)
		self.log += txt+sep
	
	
	
	
	def error(self, err, log = True):
		'''Display and log error message'''
		# write error message in red
		err = '\033[31mError : '+err+'\033[0m\n'
		self.menuIn('Error Message')
		self.print()
		
		# wait user confirmation
		input('\n\n'+err+'Press enter to continue')
		self.menuOut()
		
		# repport error in log
		if log:
			self.log += err
	
	
	
	
	def __iadd__(self,txt):
		'''overload '+=' operator toredirect it to write() method'''
		self.write(txt);
		return self
	
	
	
	
	def menuIn(self, menu):
		'''add a menu'''
		self.menu.append(menu)
	
	
	
	
	def menuOut(self):
		'''quit a menu'''
		return self.menu.pop()
	
	
	
	
	def printMenu(self):
		'''print three to the current menu position'''
		bar = '=========================='
		print(bar)
		
		if len(self.menu) == 0 :# undefine position!
			print('⁻⁼=####MENU ERROR####=⁼⁻\n'+bar)
			
		else:
			prefix = ''
			for i,m in enumerate(self.menu):# print each menu
				if i!= 0:
					i -= 1
					prefix = '╚═ '
				print(('  '*i)+prefix+m+' :')
		
		print(bar)
	
	
	
	
	
	def runPrint(self):
		'''display run remaining message'''
		if self.runMenu is not None:
			print(self.runMenu)



