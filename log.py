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
		'''return string log'''
		return self.log
	
	
	
	
	def print(self, menu = True):
		'''print the log'''
		os.system('clear')
		print(self.log)
		if menu :
			self.printMenu()
	
	
	
	
	def write(self, txt, sep = '\n'):
		'''add lines to the log'''
		self.logFile.write(txt+sep)
		self.log += txt+sep
	
	
	
	
	def error(self, err, log = True):
		'''Display a error message and add it to the log'''
		err = '\033[31mError : '+err+'\033[0m\n'
		
		self.menuIn('Error Message')
		self.print()
		print('\n\n'+err+'Press enter to continue')
		input()
		self.menuOut()
		if log:
			self.write(err, '')
	
	
	
	
	def __iadd__(self,txt):
		'''redirect '+=' operator to the write() method'''
		self.write(txt);
		return self
	
	
	
	
	def menuIn(self, menu):
		'''add a menu'''
		self.menu.append(menu)
	
	
	
	
	def menuOut(self):
		'''quit a menu'''
		return self.menu.pop()
	
	
	
	
	def printMenu(self):
		'''print three structure to current menu position'''
		bar = '=========================='
		print(bar)
		if len(self.menu) == 0 :
			print('⁻⁼=####MENU ERROR####=⁼⁻\n'+bar)
		else:
			for i,m in enumerate(self.menu):
				if i == 0:
					prefix = ''
				else:
					i -= 1
					prefix = '╚═ '
				print(('  '*i)+prefix+m+' :')
			print(bar)
	
	
	
	
	
	def runPrint(self):
		'''print the current menu'''
		if self.runMenu is not None:
			print(self.runMenu)



