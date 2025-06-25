from datetime import datetime
import linecache
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

import traceback
import socket
import time
import requests
import json
import threading
from UI_MM import *
import xml.etree.ElementTree as ET

from psutil import process_iter
import psutil
import mysql.connector
from logging_module import *

from flask import Flask

# get_open_orders('QIAOSUN')
# while True:
# 	a=1

TEST_MODE = False 
class Manager:

	def __init__(self,root):

		self.root = root 
		self.system_status = tk.StringVar(value="")

		self.SVI_cover_check = tk.BooleanVar(value=True)

		self.symbols ={}
		
		self.ui = UI(root,self,self.system_status)


		#ui = self.ui

		set_ui(self.ui)


		self.user = ""
	
		self.positions ={}
		self.open_orders = {}


		self.lock = threading.Lock()

		### ONLY RUN; when Both System & User check works ###

		good = threading.Thread(target=self.position_update_loop, daemon=True)
		good.start()


		x = threading.Thread(target=self.Ppro_in, args=(4399,),daemon=True)
		x.start()

		self.app = Flask('GoodTrade')
		self._setup_routes()
		# x2 = threading.Thread(target=self.connectivity_check, daemon=True)
		# x2.start()

		try:
			self.conn = mysql.connector.connect(
				user="webuser",
				password="Domination77$$",
				host="10.29.10.143",
				database="summitdata",
				port=3306,
				auth_plugin='mysql_native_password'
			)
			self.cursor = self.conn.cursor()
			message(f'Database connected',NOTIFICATION)
		except Exception as e:
			message(f'Database cannot connect',NOTIFICATION)

		self.start_server()
		self.start_all_inactive()



		# Query to get columns
		# self.cursor.execute("SHOW COLUMNS FROM orderdata")

		# print("Columns in 'orderdata' table:")
		# for column in self.cursor.fetchall():
		# 	print(f"- {column[0]}")


		# 	# Query to get columns
		# self.cursor.execute("SHOW COLUMNS FROM canceldata")

		# print("Columns in 'orderdata' table:")
		# for column in self.cursor.fetchall():
		# 	print(f"- {column[0]}")
		query = """
		SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT, EXTRA
		FROM INFORMATION_SCHEMA.COLUMNS
		WHERE TABLE_SCHEMA = 'summitdata' AND TABLE_NAME = 'orderdata'
		"""
		self.cursor.execute(query)
		for row in self.cursor.fetchall():
			print(row)

		# self.insert_order('test','test','test',1,1)
		
		# self.insert_cancel(1,'test','test')

		#self.insert_order('symbol','side','order_number','price',shares,1,'test')

	def insert_order(
		self,
		symbol,                # e.g., "ACHR.NY"
		side,                  # e.g., "B" or "S"
		order_number,          # for tracking, stored in PapiID
		price,                 # float
		shares,                # int, optional (can be None)
		depth_level=0,         # default value if unknown
		messageX="OrderStatus"  # optional, for completeness
	):


		try:
			query = """
				INSERT INTO orderdata (
					MarketDate,
					ComputerTime,
					Message,
					Symbol,
					Trader,
					DepthLevel,
					Price,
					Side,
					PapiID,
					Size
				) VALUES (
					%s, %s, %s, %s, %s,
					%s, %s, %s, %s, %s
				)
			"""

			computer_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			self.cursor.execute(query, (
				computer_time,
				computer_time,
				messageX,
				symbol,
				self.user,
				depth_level,
				price,
				side,
				order_number,  # stored in PapiID
				shares
			))
			self.conn.commit()
			print('databse order submited')
		except Exception as e:
			message(f"database order submission error {e}",NOTIFICATION)

			
	def insert_cancel(self, order_number, symbol, reason):
		query = """
			INSERT INTO canceldata (order_number, symbol, reason)
			VALUES (%s, %s, %s)
		"""
		self.cursor.execute(query, (order_number, symbol, reason))
		self.conn.commit()


	def _setup_routes(self):
		@self.app.route('/symbol', methods=['GET'])
		def get_symbol():
			# You can customize this return as needed
			return f"{list(self.symbols.keys())}"

	def start_server(self):
		thread = threading.Thread(target=self._run_flask)
		thread.daemon = True  # allows program to exit even if thread is running
		thread.start()

	def _run_flask(self):
		self.app.run(port=8888, use_reloader=False)

	def get_svi_order_check(self):

		return self.SVI_cover_check.get()
		
	def get_inventory(self,symbol):


		if symbol in self.positions:
			return self.positions[symbol]

		else:
			return 0,0

	def get_open_order(self,symbol):

		if symbol in self.open_orders:
			return self.open_orders[symbol]
		else:
			return {}

	def start_all_inactive(self):

		for symbol in self.symbols.keys():
			self.symbols[symbol].start_pending()	

	def start_all_restrictive(self):

		for symbol in self.symbols.keys():
			self.symbols[symbol].start_restrictive()
	def start_all_default(self):

		for symbol in self.symbols.keys():
			self.symbols[symbol].start_default()

	def start_all_opening(self):

		for symbol in self.symbols.keys():
			self.symbols[symbol].start_opening()

	def set_connected(self):
		if self.system_status.get()!=CONNECTED:
			

			self.user = get_env()

			if self.user =='x':
				return 
			self.ui.set_user(self.user)
			message(f"Trader id: {self.user}",NOTIFICATION)

			
			req = "http://127.0.0.1:8080/SetOutput?region=1&feedtype=OSTAT&output="+ str(4399)+"&status=on"
			r = requests.post(req)


			message("PPRO Connected",NOTIFICATION)
		self.system_status.set(CONNECTED)
		self.ui.system_status["background"] = "lightgreen"

	def set_disconnected(self):

		if self.system_status.get()!=DISCONNECTED:
			message("Alert: Cannot Connect to PPRO",NOTIFICATION)
		self.system_status.set(DISCONNECTED)

		self.ui.system_status["background"] = "red"

	def get_connectivity(self):

		return self.system_status.get()==CONNECTED

	def position_update_loop(self):

		while True:

			try:
				self.root.after(0, lambda: None)
				break
			except RuntimeError:
				time.sleep(3)


		while True:
			try:
				self.set_connected()
				self.positions = get_current_positions(self.user)
				self.open_orders = get_open_orders(self.user)
				
			except Exception as e:
				self.set_disconnected()

			try:
				if self.get_connectivity():
					for symbol in self.symbols.keys():
						self.symbols[symbol].update_data()

						if symbol in self.open_orders:
							self.symbols[symbol].update_orderbook(self.open_orders[symbol])
						else:
							self.symbols[symbol].update_orderbook({})

						self.symbols[symbol].sysmbol_inspection()
			except:
				PrintException("Inspection error:")


			time.sleep(5)



	def load_ticker(self,ticker):
		
		if ticker in self.symbols:
			return 

		else:

			if os.path.exists(f"configs/{ticker}.json"):
				mm = SymbolMM(ticker,self)
			else:
				mm = SymbolMM(ticker,self)
				mm.save()

			self.symbols[ticker] = mm

			return self.symbols[ticker]

	def manager_loop(self):

		# fayila

		pass 
	
	def cancel_all_orders(self):
		pass

	def fetch_all_database(self):

		for symbol in self.symbols.keys():
			self.symbols[symbol].fetch_db_data()


	def Ppro_in(self,port):

		UDP_IP = "localhost"
		UDP_PORT = port

		force_close_port(port)

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((UDP_IP, UDP_PORT))
		# sock.settimeout(1.0)

		#sock.settimeout()
		work = False

		print('ppro in actived')



		while True:

			try:
				rec= False
				try:
					data, addr = sock.recvfrom(2048)
					rec = True
				except Exception as e:

					work = False

				if rec:
					stream_data = str(data)
					#print(stream_data)
					work=True
					type_ = find_between(stream_data, "Message=", ",")
					if type_ == "OrderStatus":
						self.decode_order(stream_data)


			except Exception as e:
				PrintException(e,"PPRO IN error")
		f.close()

	def decode_order(self,stream_data):
		if "OrderState" in stream_data:
			#log_print(stream_data)
			state = find_between(stream_data, "OrderState=", ",")
			if state =="Filled" or state =="Partially Filled":
				symbol = find_between(stream_data, "Symbol=", ",")
				side = find_between(stream_data, "Side=", ",")
				price = find_between(stream_data, "Price=", ",")
				share = int(find_between(stream_data, "Shares=", ","))
				ts=find_between(stream_data, "MarketDateTime=", ",")[9:-4]
				#add time
				# if side =="T" or side =="S": side ="Short"
				# if side =="B": side = "Long"

				# data ={}
				# data["symbol"]= symbol
				# data["side"]= side
				# data["price"]= float(price)
				# data["shares"]= int(share)
				# data["timestamp"]= timestamp_seconds(ts)
				# #pipe.send(["order confirm",data])


				if symbol in self.symbols:

					self.symbols[symbol].add_trade_volume(share)

			if state =="Rejected":
				symbol = find_between(stream_data, "Symbol=", ",")
				side = find_between(stream_data, "Side=", ",")
				info = find_between(stream_data, "InfoText=", ",")
				data ={}
				if side =="T" or side =="S": side ="Short"
				if side =="B": side = "Long"

				data["symbol"]= symbol
				data["side"]= side
				data["info"]=info

				#print(symbol,side)

				if symbol in self.symbols:

					self.symbols[symbol].rejection_received()





def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data


def get_env():
	try:
		p="http://127.0.0.1:8080/GetEnvironment?"
		r= requests.get(p)

		if r.status_code==200:
			user = find_between(r.text, "User=", " ")[1:-1]
			return user 
		else:
			return "x"
	except Exception as e:
		return "x"

def get_current_positions(user):

	try:
		d = {}
		p="http://127.0.0.1:8080/GetOpenPositions?user="+user
		r= requests.get(p)
		symbol=""
		share=""
		for i in r.text.splitlines():
			if "Position Symbol" in i:

				symbol = find_between(i, "Symbol=", " ")[1:-1]

				price =  float(find_between(i, "AveragePrice=", " ")[1:-1])
				share = int(find_between(i, "Volume=", " ")[1:-1])

				
				d[symbol] = (price,share) 
		#log_print("Ppro_in:, get positions:",d)
		return d
	except Exception as e:
		#PrintException(e)
		return None


def get_open_orders(user):
	url = f'http://127.0.0.1:8080/GetOpenOrders?user={user}'
	response = requests.get(url)

	# Parse XML
	root = ET.fromstring(response.text)
	orders = root.find("Content").find("Orders")

	dic ={}

	for order in orders.findall("Order"):
		order_id = order.get("id")
		# state = order.get("state")
		# description = order.get("description")
		open_shares = int(order.get("openSize"))
		side = order.get('side')


		symbol = order.get("symbol") if order.get("symbol") else "UNKNOWN"
		price = float(order.get("price") if order.get("price") else "0.0")


		if side!="B":
			price*=-1

		if abs(price)>=0.5:
			price = round(price,2)
		else:
			price = round(price,3)

		if symbol not in dic:
			dic[symbol] = {}

		dic[symbol][price] = order_id

		#print(f"ID: {order_id}, Symbol: {symbol}, OpenShares: {open_shares} {side}, Price: {price}")
	#print(dic)		

	return dic
def force_close_port(port, process_name=None):
	"""Terminate a process that is bound to a port.
	
	The process name can be set (eg. python), which will
	ignore any other process that doesn't start with it.
	"""
	for proc in psutil.process_iter():
		for conn in proc.connections():
			if conn.laddr[1] == port:
				#Don't close if it belongs to SYSTEM
				#On windows using .username() results in AccessDenied
				#TODO: Needs testing on other operating systems
				try:
					proc.username()
				except psutil.AccessDenied:
					pass
				else:
					if process_name is None or proc.name().startswith(process_name):
						try:
							proc.kill()
						except (psutil.NoSuchProcess, psutil.AccessDenied):
							pass 



if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager Market Making v1") 
	#root.geometry("1380x780")
	root.geometry("1520x1080")

	

	manager=Manager(root)


	message("System Initialized",NOTIFICATION)
	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop() 