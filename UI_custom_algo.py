import tkinter as tk                     
from tkinter import ttk 
import threading
import multiprocessing
import pandas as pd
import time
from datetime import datetime

import requests


#from pannel import *
#from modules.pannel import *

from tkinter import *
import json
import os 


ACTIVE = 0
RISK = 1
MULTIPLIER = 2
PASSIVE = 3
DESCRIPTION = 4
# from modules.TNV_OR import *
# from modules.TNV_Trend import *

class fake_NT():

	def __init__(self):

		self.nasdaq_trader_symbols_ranking=[]

def ts_to_min(ts):
	ts = int(ts)
	m = ts//60
	s = ts%60

	return str(m)+":"+str(s)

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data


class Custom_Algo():

	def __init__(self,root,TNV_scanner,http_out,Pipe=None):

		self.root = root 

		self.http_out = http_out

		self.tnv_scanner = TNV_scanner
		self.entries = []

		self.algo_activate = tk.BooleanVar(value=1)

		current_y = 0

		self.TNV_TAB = ttk.Notebook(self.root)
		self.TNV_TAB.place(x=0,rely=0.05,relheight=1,width=640)


		self.frames = {}
		self.algo_groups = []
		self.algos ={}
		self.load_algo_tabs()

		self.create_algo_tabs()
		self.create_each_algos()

		self.load_all()

		if Pipe!=None:
			self.pipe = Pipe 
			db = threading.Thread(target=self.receive_request,args=(),daemon=True)
			db.start()

	def receive_request(self):

		#self.util_request.send("HELLO!")
		while True:
			d = self.pipe.recv()
			try:
				if len(d)>0:

					if d[0]=="http":
						try:
							self.http_order(d[1])
						except Exception as e:
							print("Error updating HTTP:",e)
					else:
						print("unkown server package:",d)

			except Exception as e:
				print("Util receive unkown:",e,d)

	def load_algo_tabs(self):

		# load each algo, create tab for them
		# for each individual algo, create stuff

		dir_name = "custom_algos"
		directory = os.fsencode(dir_name)


		count = 0
		for file in os.listdir(directory):
			filename = os.fsdecode(file)

			strategy = filename[:-4]
			self.algo_groups.append(strategy)
			self.algos[strategy] = {}
			if filename.endswith(".txt"): 
				print(filename)
				a_file = open(dir_name+"/"+filename)
				lines = a_file.read().splitlines()
				for i in lines:
					self.algos[strategy][i] = [] 
					self.algos[strategy][i].append(tk.BooleanVar(value=0))
					self.algos[strategy][i].append(tk.IntVar(value=1))
					self.algos[strategy][i].append(tk.IntVar(value=1))
					self.algos[strategy][i].append(tk.BooleanVar(value=0))

	def create_algo_tabs(self):

		for i in self.algo_groups:
			self.frames[i] = tk.Canvas(self.TNV_TAB)
			self.TNV_TAB.add(self.frames[i], text =i)

	def create_each_algos(self):

		for i in self.algo_groups:
			ttk.Label(self.frames[i], text="").grid(sticky="w",column=0,row=0)
			row = 1
			col = 0
			for algo,item in self.algos[i].items():

				ttk.Label(self.frames[i], text=algo).grid(sticky="w",column=col,row=row)
				ttk.Checkbutton(self.frames[i], variable=item[ACTIVE]).grid(sticky="w",column=col+1,row=row)

				ttk.Label(self.frames[i], text="Risk:").grid(sticky="w",column=col+4,row=row)
				ttk.Entry(self.frames[i], textvariable=item[RISK]).grid(sticky="w",column=col+5,row=row)

				ttk.Label(self.frames[i], text="Multiplier:").grid(sticky="w",column=col+6,row=row)
				ttk.Entry(self.frames[i], textvariable=item[MULTIPLIER]).grid(sticky="w",column=col+7,row=row)


				ttk.Label(self.frames[i], text="Aggresive:").grid(sticky="w",column=col+2,row=row)
				ttk.Checkbutton(self.frames[i], variable=item[PASSIVE]).grid(sticky="w",column=col+3,row=row)


				row+=1

			#print("CUURR",i)
			t = i 
			ttk.Button(self.frames[i], text="Save Config",command= lambda: self.save_setting()).grid(sticky="w",column=col,row=row)
			ttk.Button(self.frames[i], text="Load Config",command= lambda: self.load_setting()).grid(sticky="w",column=col+2,row=row)

	def save_setting(self):
		d = {}

		tab =self.TNV_TAB.tab(self.TNV_TAB.select(),"text")
		for algo,item in self.algos[tab].items():
			d[algo]=[]
			for i in item:
				d[algo].append(i.get())
		#print("saving",tab)
		with open('custom_algos_config/'+tab+'_setting.json', 'w') as fp:
			json.dump(d, fp)

	def load_setting(self):
		
		tab =self.TNV_TAB.tab(self.TNV_TAB.select(),"text")
		with open('custom_algos_config/'+tab+'_setting.json', 'r') as myfile:
			data=myfile.read()

		# parse file
		d = json.loads(data)
		#print("loading",tab)

		for key,item in d.items():
			#print(self.algos[tab][key])
			try:
				self.algos[tab][key][ACTIVE].set(item[ACTIVE])
				self.algos[tab][key][PASSIVE].set(item[PASSIVE])
				self.algos[tab][key][RISK].set(item[RISK])
				self.algos[tab][key][MULTIPLIER].set(item[MULTIPLIER])
			except:
				pass

	def load_all(self):

		try:
			for tab in self.algo_groups:
				with open('custom_algos_config/'+tab+'_setting.json', 'r') as myfile:
					data=myfile.read()

				# parse file
				d = json.loads(data)
				#print("loading",tab)

				for key,item in d.items():
					#print(self.algos[tab][key])
					try:
						self.algos[tab][key][ACTIVE].set(item[ACTIVE])
						self.algos[tab][key][PASSIVE].set(item[PASSIVE])
						self.algos[tab][key][RISK].set(item[RISK])
						self.algos[tab][key][MULTIPLIER].set(item[MULTIPLIER])
					except:
						pass
		except:
			pass


	def order_complier(self,data,multiplier,risk,aggresive):


		basket = find_between(data,"Basket=",",") 
		symbol = find_between(data,"Order=*","*") 

		new_order = "Order=*"

		z = 0 
		for i in symbol.split(","):
			if z>=1:
				new_order+=","
			k = i.split(":")
			new_order+= k[0]
			new_order+= ":"+str(int(k[1])*multiplier)
			z+=1

		new_order+="*"

		data = "Basket="+basket+","+new_order

		risk__ = risk
		data += ","+"Risk="+str(risk__)+","

		if aggresive:
			data += "Aggresive=1"+","
		else:
			data += "Aggresive=0"+","
		return data


	def http_order(self,data):

		print("RECEVING:",data)

		if "Basket" in data:

			## PARSE IT AND RE PARSE IT. ? ADD RISK TO IT. 

			name = find_between(data, "Basket=", ",")
			confimed = False 


			for i in self.algo_groups:
				for algo,item in self.algos[i].items():
					print(algo,name,algo in name,item[ACTIVE].get())
					if algo in name and item[ACTIVE].get()==True:
						confimed=True
						data = self.order_complier(data,item[MULTIPLIER].get(),item[RISK].get(),item[PASSIVE].get())
						break

				if confimed:
					break

			if confimed:

				# risk = int(self.algo_risk.get())
				# data += ","+"Risk="+str(risk)+","
				msg = "http://localhost:4441/"	
				msg += data
				print("Sending:",msg)

				#requests.get(msg)

				self.request_post(msg)
				# reg1 = threading.Thread(target=request_post,args=(msg,), daemon=True)
				# reg1.start()

		else:
			print("Not activated")


	def request_post(self,body):

		#requests.get(body,timeout=2)
		self.http_out.send(body)


if __name__ == '__main__':

	from http_out import *
	from TNV_http import *

	ACTIVE = 0
	RISK = 1
	MULTIPLIER = 2
	PASSIVE = 3

	http_in, http_out = multiprocessing.Pipe()
	util_request, util_response = multiprocessing.Pipe()



	http = threading.Thread(target=httpserver,args=(util_response,),daemon=True)
	http.start()

	http2 = threading.Thread(target=http_driver,args=(http_out,),daemon=True)
	http2.start()


	root = tk.Tk() 
	root.title("GoodTrade Lite") 
	root.geometry("640x840")

	# print(ratio_compute(0.8))
	# print(ratio_compute(1.2))

	Custom_Algo(root,fake_NT(),http_in,util_request)

	root.mainloop()

	# print("h")
	# body="http://localhost:4441/Basket=PUFTB,Order=*QQQ.NQ:0*,Risk=1,Aggresive=0,"

	# r=requests.get(body,timeout=2)

	# print(r.status_code)


	# 		info = [rank,avgv,relv,roc5,roc10,roc15,score,sc,so]
	# 		self.nasdaq.append([])

# # # # df=df.sort_values(by="rank",ascending=False)

# print(df)
# i=0
# for item,row in df.iterrows():
# 	#print(item,row)
# 	df.loc[item,"rank"] =i
# 	i+=1 
# print(df)
# df.loc[df["rank"]==2,"rank5"]=5


# print(df.loc[df["status"]=='New'])
# print(df)


# df=df.sort_values(by=["rank","status"],ascending=False)

# print(df)

