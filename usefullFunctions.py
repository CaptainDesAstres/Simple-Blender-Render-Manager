#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
import time



def now(short = True):
	'''return current date in short or long form (HH:MM:SS or DD.MM.AAAA-HH:MM:SS)'''
	if short == True:
		return time.strftime('%H:%M:%S')
	else:
		return time.strftime('%d.%m.%Y-%H:%M:%S')



def columnLimit(value, limit, begin = True, sep = '|'):
	'''make fix sized text column'''
	if type(value) is not str:
		value = str(value)
	
	if begin is True:
		begin = limit# number of first caracter to display
	
	if len(value) > limit:
		return (value[0:begin-1]+'…'# first caracter\
				+value[len(value)-(limit-begin):]# last caracter\
				+sep) # column seperator
	else:
		return value +  (' '*(limit-len(value)))  +sep# add space to match needed size





def indexPrintList(l):
	'''Print a list and index'''
	
	for i, v in enumerate(l):
		print(str(i)+'- '+str(v))
	





class XML:
	''' a class containing usefull method for XML'''
	
	entities = {
				'\'':'&apos;',
				'"':'&quot;',
				'<':'&lt;',
				'>':'&gt;'
				}
	
	
	
	
	
	def encode(txt):
		'''replace XML entities by XML representation'''
		txt.replace('&', '&amp;')
		
		for entity, code in XML.entities.items():
			txt.replace(entity, code)
		
		return txt
	
	
	
	
	
	def decode(txt):
		'''XML representation by the original character'''
		for entity, code in XML.entities.items():
			txt.replace(code, entity)
		
		txt.replace('&amp;', '&')
		
		return txt





