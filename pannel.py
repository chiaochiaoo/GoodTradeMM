import tkinter as tk 
from tkinter import ttk 
class pannel:

	def __init__(self,frame):

		self.tickers = []
		self.label_count = 0
		self.ticker_count = 0
		self.tickers_labels = {}
		self.tickers_tracers = {}

		self.tm = ttk.LabelFrame(frame) 
		self.tm.place(x=0, y=40, relheight=0.85, relwidth=1)

		self.canvas = tk.Canvas(self.tm)
		self.canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll2 = tk.Scrollbar(self.tm)
		self.scroll2.config(orient=tk.VERTICAL, command=self.canvas.yview)
		self.scroll2.pack(side=tk.RIGHT,fill="y")

		self.canvas.configure(yscrollcommand=self.scroll2.set)
		
		self.frame = tk.Frame(self.canvas)
		self.frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.canvas.create_window(0, 0, window=self.frame, anchor=tk.NW)


	def rebind(self,canvas,frame):
		canvas.update_idletasks()
		canvas.config(scrollregion=frame.bbox()) 
		
	def label_default_configure(self,label):

		label.configure(activebackground="#f9f9f9")
		label.configure(activeforeground="black")

		label.configure(background="#d9d9d9")
		label.configure(disabledforeground="#a3a3a3")
		label.configure(relief="ridge")
		label.configure(foreground="#000000")
		label.configure(highlightbackground="#d9d9d9")
		label.configure(highlightcolor="black")

	def status_change_color(self,text,label):

		try:

			if text.get() == "Connecting":
				label["background"] = "#ECF57C"
			elif text.get() == "Unfound":
				label["background"] = "red"
			elif text.get() == "Connected":
				label["background"] = "#97FEA8"
			elif text.get() == "Lagged":
				label["background"] = "#ECF57C"
			else:
				label["background"] = "red"

		except Exception as e:

			print("destroyed labels")



	def labels_creator(self,frame):
		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(frame, text=self.labels[i],width=self.width[i])#command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)


def timestamp(s):

	p = s.split(":")
	try:
		x = int(p[0])*60+int(p[1])
		return x
	except Exception as e:
		print(e)
		return 0


def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print(e)
		return 0

#print(timestamp_seconds("13:23:46"))

"""
		try:
			label.configure(activebackground="#f9f9f9")
		except:
			pass
		try:
			label.configure(background="#d9d9d9")
		except:
			pass
		try:
			label.configure(disabledforeground="#a3a3a3")
		except:
			pass
		try:
			label.configure(relief="ridge")
		except:
			pass
		try:
			label.configure(foreground="#000000")
		except:
			pass
		try:
			label.configure(highlightbackground="#d9d9d9")
		except:
			pass
		try:
			label.configure(highlightcolor="black")
		except:
			pass
"""