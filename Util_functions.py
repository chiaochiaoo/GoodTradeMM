from datetime import datetime

import linecache
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.pyplot as plt
import traceback
import socket
import time
import json
def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data


def convert(df):
	
	algos = df.ALGO.unique()
	dates = df.DATE.unique()
	treal = pd.DataFrame(index=dates)
	trisk = pd.DataFrame(index=dates)
	for algo in algos:
		#print(algo)
		a = []
		b = []
		for date in dates:
			a.append(sum(df.loc[(df["DATE"]==date)&(df["ALGO"]==algo)]["REALIZED"].tolist()))
			b.append(sum(df.loc[(df["DATE"]==date)&(df["ALGO"]==algo)]["RISK"].tolist()))
		treal[algo] = a#r.loc[r.ALGO==algo].groupby(['DATE']).sum()["REALIZED"].tolist()
		trisk[algo] = b
	return treal,trisk


def graphweekly():


	now = datetime.now()
	monday = now - timedelta(days = now.weekday())
	file = monday.strftime("%Y_%m_%d")+".csv"

	r = pd.read_csv("../../algo_records/"+file)



	algos = r.ALGO.unique()


	fig, axs = plt.subplots(3,2,figsize=(20,15))
	#fig.suptitle('Vertically stacked subplots')

	r.groupby(['DATE']).sum().plot(ax=axs[0,0],kind='bar')

	axs[0,0].axhline(0,linestyle="--")
	axs[0,0].xaxis.set_tick_params(rotation=1)      
	axs[0,0].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[0,0].set_title("Total by date")

	tr,trk = convert(r)

	tr.plot(ax=axs[1,0],kind='bar')
	axs[1,0].axhline(0,linestyle="--")
	axs[1,0].xaxis.set_tick_params(rotation=1)      
	axs[1,0].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[1,0].set_title("Total Realized by algo by date")


	trk.plot(ax=axs[2,0],kind='bar')
	axs[2,0].axhline(0,linestyle="--")
	axs[2,0].xaxis.set_tick_params(rotation=1)      
	axs[2,0].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[2,0].set_title("Total Risk by algo by date")


	r.groupby(['ALGO'])["RISK"].sum().plot(ax=axs[0,1],kind='bar')
	axs[0,1].axhline(0,linestyle="--")
	axs[0,1].xaxis.set_tick_params(rotation=1)      
	axs[0,1].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[0,1].set_title("Total Risk by Algo")

	r.groupby(['ALGO'])["REALIZED"].sum().plot(ax=axs[1,1],kind='bar')
	axs[1,1].axhline(0,linestyle="--")
	axs[1,1].xaxis.set_tick_params(rotation=1)      
	axs[1,1].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[1,1].set_title("Total Realized by Algo")

	r.groupby(['SYMBOL'])["REALIZED"].sum().sort_values(ascending=False)[:10].plot(ax=axs[2,1],kind='bar')
	axs[2,1].axhline(0,linestyle="--")
	axs[2,1].xaxis.set_tick_params(rotation=1)      
	axs[2,1].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[2,1].set_title("Total Realized by Symbol")

	plt.tight_layout()
	plt.show()
	
def PrintException(info,additional="ERROR"):
	# exc_type, exc_obj, tb = sys.exc_info()
	# f = tb.tb_frame
	# lineno = tb.tb_lineno
	# filename = f.f_code.co_filename
	# linecache.checkcache(filename)
	# line = linecache.getline(filename, lineno, f.f_globals)
	# log_print (info+'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	log_print(additional,info,exc_type, fname, exc_tb.tb_lineno,traceback.format_exc())

def log_print(*args):
	"""My custom log_print() function."""
	# Adding new arguments to the log_print function signature 
	# is probably a bad idea.
	# Instead consider testing if custom argument keywords
	# are present in kwargs

	#send this via a pipe to another processor 

	try:
		listToStr = ' '.join([str(elem) for elem in args])

		if len(listToStr)>5:
			time_ = datetime.now().strftime("%H:%M:%S : ")
			with open("../../algo_logs/"+datetime.now().strftime("%Y-%m-%d")+".txt", "a+") as file:
				file.write("\n"+time_+listToStr)
			print(time_,*args)
	except Exception as e:
		print(*args,e,"failed to write")



def hexcolor_green_to_red(level):

	if level>0:
		code = int(510*(level))
		#print(code,"_")
		if code >255:
			first_part = code-255
			return "#FF"+hex_to_string(255-first_part)+"00"
		else:
			return "#FF"+"FF"+hex_to_string(255-code)

	else:
		code = int(255*(abs(level)))
		first_part = 255-code

		return "#"+hex_to_string(first_part)+"FF"+hex_to_string(first_part)

def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0


def hex_to_string(int):
	a = hex(int)[-2:]
	a = a.replace("x","0")

	return a

#1-5 is good 
def hexcolor_red(level):
	code = int(510*(level))
	if code >255:
		first_part = code-255
		return "#FF"+hex_to_string(255-first_part)+"00"
	else:
		return "#FF"+"FF"+hex_to_string(255-code)

		
def algo_manager_voxcom(pipe):

	#tries to establish commuc


	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		#PORT = 65491       # The port used by the server

		try:
			log_print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					with open('../commlink.json') as json_file:
						port_file = json.load(json_file)

					if datetime.now().strftime("%m%d") not in port_file:
						time.sleep(1)
					else:
						PORT = port_file[datetime.now().strftime("%m%d")]
						s.connect((HOST, PORT))
						connected = True

					s.setblocking(0)
				except Exception as e:
					pipe.send(["msg","Disconnected"])
					log_print("Cannot connected. Try again in 2 seconds.",e)
					time.sleep(2)

			connection = True
			pipe.send(["msg","Connected"])
			k = None

			count = 0
			while connection:

				#from the socket
				ready = select.select([s], [], [], 0)
				
				if ready[0]:
					data = []
					while True:
						try:
							part = s.recv(2048)
						except:
							connection = False
							break
						#if not part: break
						data.append(part)
						if len(part) < 2048:
							#try to assemble it, if successful.jump. else, get more. 
							try:
								k = pickle.loads(b"".join(data))
								break
							except:
								pass
					#k is the confirmation from client. send it back to pipe.
					if k!=None:
						placed = []

						pipe.send(["pkg",k[1:]])
						for i in k[1:]:
							log_print("placed:",i[1])
							placed.append(i[1])
						#log_print("placed:",k[1][1])
						
						s.send(pickle.dumps(["Algo placed",placed]))

				# if pipe.poll(0):
				# 	data = pipe.recv()
				# 	if data == "Termination":
				# 		s.send(pickle.dumps(["Termination"]))
				# 		print("Terminate!")

				# 	part = s.recv(2048)
				# except:
				# 	connection = False
				# 	break
				# #if not part: break
				# data.append(part)
				# if len(part) < 2048:
				# 	#try to assemble it, if successful.jump. else, get more. 
				# 	try:
				# 		k = pickle.loads(b"".join(data))
				# 		break
				# 	except:
				# 		pass

				count+=1
				print(count)
			log_print("Main disconnected")
			pipe.send(["msg","Main disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			log_print(e)


def algo_manager_voxcom2(pipe):

	#tries to establish commuc
	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		PORT = 65491       # The port used by the server

		try:
			log_print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					s.connect((HOST, PORT))
					s.send(pickle.dumps(["Connection","Connected"]))
					connected = True
				except:
					pipe.send(["msg","Disconnected"])
					log_print("Cannot connected. Try again in 3 seconds.")
					time.sleep(3)

			connection = True

			pipe.send(["msg","Connected"])

			while connection:

				data = []
				k = None
				while True:
					try:
						part = s.recv(2048)
					except:
						connection = False
						break
					#if not part: break
					data.append(part)
					if len(part) < 2048:
						#try to assemble it, if successful.jump. else, get more. 
						try:
							k = pickle.loads(b"".join(data))
							break
						except Exception as e:
							log_print(e)
				#s.sendall(pickle.dumps(["ids"]))
				if k!=None:
					pipe.send(["pkg",k])
					#log_print("placed:",k[1][1])
					s.send(pickle.dumps(["Algo placed",k[1][1]]))
			log_print("Main disconnected")
			pipe.send(["msg","Disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			log_print(e)


def algo_manager_voxcom3(pipe):

	#tries to establish commuc


	while True:

		HOST = 'localhost'  # The server's hostname or IP address
		#PORT = 65491       # The port used by the server

		try:
			log_print("Trying to connect to the main application")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connected = False

			while not connected:
				try:
					with open('../commlink.json') as json_file:
						port_file = json.load(json_file)

					if datetime.now().strftime("%m%d") not in port_file:
						time.sleep(1)
					else:
						PORT = port_file[datetime.now().strftime("%m%d")]
						s.connect((HOST, PORT))
						connected = True

					s.setblocking(1)
				except Exception as e:
					pipe.send(["msg","Disconnected"])
					#log_print("Cannot connected. Try again in 2 seconds.",e)
					time.sleep(120)

			connection = True
			pipe.send(["msg","Connected"])
			k = None

			count = 0
			while connection:

				#from the socket
				data = []
				while True:
					try:
						part = s.recv(2048)
					except:
						connection = False
						break
					#if not part: break
					data.append(part)
					if len(part) < 2048:
						#try to assemble it, if successful.jump. else, get more. 
						try:
							k = pickle.loads(b"".join(data))
							break
						except:
							pass
				#k is the confirmation from client. send it back to pipe.
				if k!=None:
					if k!=['checking']:
						placed = []

						pipe.send(["pkg",k[1:]])
						for i in k[1:]:
							log_print("placed:",i[1])
							placed.append(i[1])
						#log_print("placed:",k[1][1])
						
						s.send(pickle.dumps(["Algo placed",placed]))

				# if pipe.poll(0):
				# 	data = pipe.recv()
				# 	if data == "Termination":
				# 		s.send(pickle.dumps(["Termination"]))
				# 		print("Terminate!")

				# 	part = s.recv(2048)
				# except:
				# 	connection = False
				# 	break
				# #if not part: break
				# data.append(part)
				# if len(part) < 2048:
				# 	#try to assemble it, if successful.jump. else, get more. 
				# 	try:
				# 		k = pickle.loads(b"".join(data))
				# 		break
				# 	except:
				# 		pass

				count+=1
				#print("algo place counts",count)
			log_print("Main disconnected")
			pipe.send(["msg","Main disconnected"])
		except Exception as e:
			pipe.send(["msg",e])
			log_print(e)


def logging(pipe):

	f = open(datetime.now().strftime("%d/%m")+".txt", "w")
	while True:
		string = pipe.recv()
		time_ = datetime.now().strftime("%H:%M:%S")
		log_print(string)
		f.write(time_+" :"+string)
	f.close()

#COLOR CODING TEST
# if __name__ == '__main__':

# 	import tkinter as tk
# 	root = tk.Tk() 

# 	for i in range(0,13):

# 		tk.Label(text="",background=hexcolor_red(i/10),width=10).grid(column=i,row=1)

# 	root.mainloop()


