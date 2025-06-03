from pannel import *
from constant import *
from Util_functions import *

import time
from TickerMM import *

try:
	from ttkwidgets.frames import Tooltip
except ImportError:
	import pip
	pip.main(['install', 'ttkwidgets'])
	from ttkwidgets.frames import Tooltip

FIELDS_PER_ROW = 6 


def trace_func(d):

	if d['lock'].get()==0:
		d['set_entry']["state"] = DISABLED
		d['set_button']["state"] = DISABLED
		#d['flat_button']["state"] = DISABLED
		
		d['set_current']["state"] = DISABLED
		d['set_max']["state"] = DISABLED
		d['passive_button']["state"] = DISABLED


	else:
		d['set_entry']["state"] = "normal"
		d['set_button']["state"] = "normal"
		#d['flat_button']["state"] = "normal"
		d['set_current']["state"] = "normal"
		d['set_max']["state"] = "normal"
		d['passive_button']["state"] = "normal"



def show_tooltip(event, widget,root,label,text):
	x, y, _, _ = widget.bbox("insert")
	x += widget.winfo_rootx() + 25
	y += widget.winfo_rooty() - 25
	
	root.geometry("+{}+{}".format(x, y))
	label.config(text=text)
	root.deiconify()

def hide_tooltip(event,root):
	root.withdraw()


class UI(pannel):
	def __init__(self,root,manager=None,cmd_text=None):

		self.root = root

		self.manager = manager
		self.command_text = cmd_text
		self.risk_timer = tk.DoubleVar(value=300)

		self.button_commands = {
			"start_strategy": self.start_strategy,
			"stop_strategy": self.stop_strategy,
			# Add more as needed
		}
		
		self.init_pannel()

	def start_strategy(self):
		print(f"[{self.mm.ticker}] Strategy started")

	def stop_strategy(self):
		print(f"[{self.mm.ticker}] Strategy stopped")

	def init_system_pannel(self):

		self.main_app_status = tk.StringVar()
		self.main_app_status.set("")

		self.user = tk.StringVar()
		self.user.set("DISCONNECTED")

		self.ppro_api_status = tk.StringVar()
		self.ppro_api_status.set("Disconnected")

		self.algo_count_number = tk.IntVar(value=0)
		self.active_algo_count_number = tk.IntVar(value=0)
		self.current_display_count = 0
		self.algo_number = 0

		self.position_count = tk.IntVar(value=0)
		self.position_number = 0

		self.user_email = tk.StringVar()
		self.user_email.set("")

		self.user_phone = tk.StringVar()
		self.user_phone.set("")

		self.system_status_text = tk.StringVar()
		self.system_status_text.set("ERROR")

		self.file_last_update = tk.StringVar(value="Disconnected")

		self.algo_count_string = tk.StringVar(value="0")
		self.algo_timer_string = tk.StringVar(value="0")
		self.algo_timer_close_string = tk.StringVar(value="0")

		self.algo_count_string.set("Activated Algos:"+str(self.algo_count_number))


		row = 1
		self.system = ttk.Label(self.system_pannel, text="SYSTEM:")
		self.system.grid(sticky="w",column=1,row=row,padx=10)

		self.system_status = tk.Button(self.system_pannel, textvariable=self.system_status_text,activebackground='red',activeforeground='yellow')
		self.system_status.grid(sticky="w",column=2,row=row)
		self.system_status["background"] = "red"
		row +=1
		self.account = ttk.Label(self.system_pannel, text="Account ID:")
		self.account.grid(sticky="w",column=1,row=row,padx=10)
		
		self.account_status = ttk.Label(self.system_pannel, textvariable=self.user)
		self.account_status.grid(sticky="w",column=2,row=row)
		self.account_status["background"] = "red"

		row +=1
		self.file_link_label = ttk.Label(self.system_pannel, text="File Linked:")
		self.file_link_label.grid(sticky="w",column=1,row=row,padx=10)
		self.file_link_status = ttk.Label(self.system_pannel,  textvariable=self.file_last_update)
		self.file_link_status["background"] = "red"
		self.file_link_status.grid(sticky="w",column=2,row=row,padx=10)

		row +=1
		self.ppro = ttk.Label(self.system_pannel, text="Ppro API:")
		self.ppro.grid(sticky="w",column=1,row=row,padx=10)
		self.ppro_api_status_label = ttk.Label(self.system_pannel, textvariable=self.ppro_api_status)
		self.ppro_api_status_label.grid(sticky="w",column=2,row=row)
		self.ppro_api_status_label["background"] = "red"

		row +=1
		self.al = ttk.Label(self.system_pannel, text="Total Algo Count::")
		self.al.grid(sticky="w",column=1,row=row,padx=10)
		self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.algo_count_number)
		self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)

		row +=1
		self.al = ttk.Label(self.system_pannel, text="Active Algo Count::")
		self.al.grid(sticky="w",column=1,row=row,padx=10)
		self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.active_algo_count_number)
		self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)

		row +=1
		self.al = ttk.Label(self.system_pannel, text="Position Count::")
		self.al.grid(sticky="w",column=1,row=row,padx=10)
		self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.position_count)
		self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)

		row +=1
		self.ol = ttk.Label(self.system_pannel, text="Orders Count::")
		self.ol.grid(sticky="w",column=1,row=row,padx=10)
		# self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.position_count)
		# self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)


		row +=1

		ttk.Label(self.system_pannel, text="Disaster mode:").grid(sticky="w",column=1,row=row,padx=10)

		try:
			ttk.Checkbutton(self.system_pannel, variable=self.manager.disaster_mode).grid(sticky="w",column=2,row=row)
		except:
			pass 



		row +=1
		ttk.Label(self.system_pannel, text="Ticker:").grid(row=row, column=1,  sticky="w",padx=10)
		self.ticker_var = tk.StringVar()
		ttk.Entry(self.system_pannel, textvariable=self.ticker_var, width=15).grid(row=row, column=2,sticky="w")

		ttk.Button(self.system_pannel, text="Load/Create", command=self.load_ticker_tab).grid(row=row, column=3)


		self.ticker_var.set('DEMO.TO')
		#self.load_ticker_tab()


	def on_mode_toggle(self, changed_name):
		# Ensure only one mode checkbox is True
		for name in MODE_CHECKBOXES:
			if name != changed_name:
				var, _ = self.mm.vars.get(name, (None, None))
				if var:
					var.set(0)

	def load_ticker_tab(self, force=True):

		ticker = self.ticker_var.get().strip()
		if not ticker:
			return

		# Load or create TickerMM
		# if os.path.exists(f"configs/{ticker}.json") and not force:
		# 	mm = TickerMM(ticker)
		# else:
		# 	mm = TickerMM(ticker, override=True)
		# 	mm.save()

		mm = self.manager.load_ticker(ticker)

		if not mm:
			return 

		# Create new tab
		tab = ttk.Frame(self.marketmaking_notebook)
		self.marketmaking_notebook.add(tab, text=ticker)

		# --- Step 1: Group schema entries by section ---
		sections = {}
		for entry in CONFIG_SCHEMA:
			sec = entry.get("section", "status")
			sections.setdefault(sec, []).append(entry)

		section_frames = {}
		row_counter = 0

		for sec_name, entries in sections.items():
			# Section title
			collapsible = CollapsibleSection(tab, title=sec_name.upper())
			collapsible.grid(row=row_counter, column=0, columnspan=FIELDS_PER_ROW * 2, sticky="w", padx=10)

			section_frame = collapsible.content  # actual frame for widgets
			section_frames[sec_name] = section_frame
			section_frames[sec_name] = section_frame

			row_counter += 2

			row_tracker = {}  # row -> current column count

			for entry in entries:
				name = entry["name"]
				label = entry["label"]
				if name == "Ticker":
					continue

				entry_type = entry["type"]
				readonly = entry.get("readonly", False)
				options = entry.get("options")
				var = mm.vars[name][0] if name in mm.vars else None

				row = entry.get("row", 0)
				col = row_tracker.get(row, 0)

				if entry_type == "button":
					# Button takes 1 cell directly
					cmd_name = entry.get("command")
					cmd_func = self.button_commands.get(cmd_name)
					widget = ttk.Button(section_frame, text=label, command=cmd_func)
					widget.grid(row=row, column=col, sticky="w", padx=5, pady=5)
					row_tracker[row] = col + 1
				else:
					# Label
					ttk.Label(section_frame, text=f"{label}:").grid(
						row=row, column=col * 2, sticky="e", padx=5, pady=5
					)
					# Widget
					if readonly:
						widget = ttk.Entry(section_frame, textvariable=var, state="readonly")
					elif entry_type == "bool":
						if name in MODE_CHECKBOXES:
							widget = ttk.Checkbutton(section_frame, variable=var, command=lambda n=name: self.on_mode_toggle(n))
						else:
							widget = ttk.Checkbutton(section_frame, variable=var)
					elif options:
						widget = ttk.Combobox(section_frame, textvariable=var, values=options, state="readonly", width=14)
					else:
						widget = ttk.Entry(section_frame, textvariable=var, width=14)

					widget.grid(row=row, column=col * 2 + 1, sticky="w", padx=5, pady=5)
					row_tracker[row] = col + 1

		# Save Button at the bottom of the last section
		ttk.Button(tab, text="Save", command=lambda: mm.save()).grid(
			row=row_counter + 10, column=0, columnspan=FIELDS_PER_ROW * 2, pady=15, padx=10, sticky="w"
		)

	def init_pannel(self):

		self.system_pannel = ttk.LabelFrame(self.root,text="System")
		self.system_pannel.place(x=10,y=10,height=250,width=350)


		self.performance_pannel = ttk.LabelFrame(self.root,text="Ticker Management") 
		self.performance_pannel.place(x=360,y=10,height=250,width=700)

		self.notification_pannel = ttk.LabelFrame(self.root,text="Notification") 
		self.notification_pannel.place(x=1070,y=10,height=250,width=290)

		# self.filter_pannel = ttk.LabelFrame(self.root,text="Algorithms Management") 
		# self.filter_pannel.place(x=360,y=200,height=60,width=1300)

		self.mm_pannel = ttk.LabelFrame(self.root,text="MarketMaking") 
		self.mm_pannel.place(x=10,y=270,height=950,width=1350)

		self.marketmaking_notebook = ttk.Notebook(self.mm_pannel)
		self.marketmaking_notebook.place(x=0,rely=0,relheight=1,relwidth=1)

		self.init_system_pannel()


if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager Market Making v1") 
	#root.geometry("1380x780")
	root.geometry("1520x1280")

	UI(root)


	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop() 