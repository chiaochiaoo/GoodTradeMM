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
import json
from UI_MM import *





class Manager:

	def __init__(self,root):

		self.root = root 
		self.cmd_text = tk.StringVar(value="Status:")
		self.ui = UI(root,self,self.cmd_text)

		self.symbols = {}

	def load_ticker(self,ticker):
		
		if ticker in self.symbols:
			return 

		else:

			if os.path.exists(f"configs/{ticker}.json"):
				mm = TickerMM(ticker)
			else:
				mm = TickerMM(ticker)
				mm.save()


			self.symbols[ticker] = mm

			return self.symbols[ticker]

	def manager_loop(self):

		# fayila

		pass 
		
if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager Market Making v1") 
	#root.geometry("1380x780")
	root.geometry("1520x1280")

	
	manager=Manager(root)


	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop() 