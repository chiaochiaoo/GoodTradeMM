from pannel import *
from constant import *
from Util_functions import *

import time
from SymbolMM import *

try:
	from ttkwidgets.frames import Tooltip
except ImportError:
	import pip
	pip.main(['install', 'ttkwidgets'])
	from ttkwidgets.frames import Tooltip

FIELDS_PER_ROW = 6 

TICKER_CONFIG_FILE = "configs/tickers.json"


CONNECTED = " CONNECTED"
DISCONNECTED = "DISCONNECTED"
DELAYED = "DELAYED"



def save_tickers(self):
	os.makedirs("configs", exist_ok=True)
	ticker_list = list(self.ticker_table_rows.keys())
	with open(TICKER_CONFIG_FILE, "w") as f:
		json.dump(ticker_list, f, indent=4)
	print(f"[Saved] {len(ticker_list)} tickers to {TICKER_CONFIG_FILE}")
def validate_float(new_value):
	if new_value == "":
		return True
	try:
		float(new_value)
		return True
	except ValueError:
		return False

def validate_int(new_value):
	if new_value == "":
		return True  # Allow empty (for deletion)
	return new_value.isdigit()

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
		self.status_text = cmd_text
		self.risk_timer = tk.DoubleVar(value=300)


		self.float_check = (root.register(validate_float), "%P")
		self.int_check =(root.register(validate_int), "%P")
		self.init_pannel()

	def init_pannel(self):

		self.system_pannel = ttk.LabelFrame(self.root,text="System")
		self.system_pannel.place(x=10,y=10,height=200,width=350)


		self.ticker_management_frame  = ttk.LabelFrame(self.root,text="Ticker Management") 
		self.ticker_management_frame .place(x=360,y=10,height=200,width=700)

		self.notification_pannel = ttk.LabelFrame(self.root,text="Notification") 
		self.notification_pannel.place(x=1090,y=10,height=900,width=400)

		self.notification_text = tk.Text(self.notification_pannel, height=10, width=50, state='disabled')
		self.notification_text.pack(anchor="nw", padx=0, pady=0, fill="both",expand=True)#


		# self.filter_pannel = ttk.LabelFrame(self.root,text="Algorithms Management") 
		# self.filter_pannel.place(x=360,y=200,height=60,width=1300)

		self.mm_pannel = ttk.LabelFrame(self.root,text="MarketMaking") 
		self.mm_pannel.place(x=10,y=210,height=870,width=1060)

		self.marketmaking_notebook = ttk.Notebook(self.mm_pannel)
		self.marketmaking_notebook.place(x=0,rely=0,relheight=1,relwidth=1)
		self.marketmaking_tabs={}

		self.init_ticker_management_table()
		self.init_system_pannel()
		self.load_saved_tickers()

	def show_notification(self, message: str, max_lines=500):
		self.notification_text.config(state='normal')
		self.notification_text.insert(tk.END, message + '\n')
		self.notification_text.see(tk.END)

		# Trim to keep only the last 500 lines
		lines = self.notification_text.get("1.0", tk.END).splitlines()
		if len(lines) > max_lines:
			self.notification_text.delete("1.0", f"{len(lines) - max_lines + 1}.0")

		self.notification_text.config(state='disabled')

	def show_notification(self, message: str, max_lines=500, color="black"):
	    self.notification_text.config(state='normal')

	    # Create or configure a tag with the desired color

	    if 'mode switch' in message:
	    	color='red'
	    if not self.notification_text.tag_names().__contains__(color):
	        self.notification_text.tag_config(color, foreground=color)

	    # Insert the message with the color tag
	    self.notification_text.insert(tk.END, message + '\n', color)
	    self.notification_text.see(tk.END)

	    # Trim to keep only the last 500 lines
	    lines = self.notification_text.get("1.0", tk.END).splitlines()
	    if len(lines) > max_lines:
	        self.notification_text.delete("1.0", f"{len(lines) - max_lines + 1}.0")

	    self.notification_text.config(state='disabled')

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

		self.file_last_update = tk.StringVar(value="Disconnected")

		self.algo_count_string = tk.StringVar(value="0")
		self.algo_timer_string = tk.StringVar(value="0")
		self.algo_timer_close_string = tk.StringVar(value="0")

		self.algo_count_string.set("Activated Algos:"+str(self.algo_count_number))


		row = 1
		self.system = ttk.Label(self.system_pannel, text="SYSTEM:")
		self.system.grid(sticky="w",column=1,row=row,padx=10)

		self.system_status = tk.Button(self.system_pannel, textvariable=self.status_text,activebackground='red',activeforeground='yellow')
		self.system_status.grid(sticky="w",column=2,row=row)
		self.system_status["background"] = "red"
		row +=1
		self.account = ttk.Label(self.system_pannel, text="Account ID:")
		self.account.grid(sticky="w",column=1,row=row,padx=10)
		
		self.account_status = ttk.Label(self.system_pannel, textvariable=self.user)
		self.account_status.grid(sticky="w",column=2,row=row)
		self.account_status["background"] = "red"



		row +=1
		self.al = ttk.Label(self.system_pannel, text="Position Count::")
		self.al.grid(sticky="w",column=1,row=row,padx=10)
		self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.position_count)
		self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)

		row +=1
		self.ol = ttk.Label(self.system_pannel, text="Orders Count::")
		self.ol.grid(sticky="w",column=1,row=row,padx=10)



		# row +=1

		# ttk.Label(self.system_pannel, text="Disaster mode:").grid(sticky="w",column=1,row=row,padx=10)

		# try:
		# 	ttk.Checkbutton(self.system_pannel, variable=self.manager.disaster_mode).grid(sticky="w",column=2,row=row)
		# except:
		# 	pass 


		row +=1
		ttk.Label(self.system_pannel, text="SVI Order Check:").grid(row=row, column=1,  sticky="w",padx=10)
		
		ttk.Checkbutton(self.system_pannel, variable=self.manager.SVI_cover_check).grid(row=row, column=2,sticky="w")


		row +=1
		ttk.Label(self.system_pannel, text="Ticker:").grid(row=row, column=1,  sticky="w",padx=10)

		self.ticker_var = tk.StringVar()
		ttk.Entry(self.system_pannel, textvariable=self.ticker_var, width=15).grid(row=row, column=2,sticky="w")

		ttk.Button(self.system_pannel, text="Load/Create", command=self.load_ticker_tab).grid(row=row, column=3)

		row +=1
		ttk.Button(self.system_pannel, text="Save All Tickers", command=self.save_tickers).grid(row=row, column=1)
		ttk.Button(self.system_pannel, text="Fetch All Database", command=self.manager.fetch_all_database).grid(row=row, column=2)

		row +=1

		ttk.Button(self.system_pannel, text="Start All Inactive", command=self.manager.start_all_inactive).grid(row=row, column=1)

		#ttk.Button(self.system_pannel, text="Start All Restrictive", command=self.manager.start_all_restrictive).grid(row=row, column=2)

		ttk.Button(self.system_pannel, text="Start All Default", command=self.manager.start_all_default).grid(row=row, column=2)

		#row +=1



		ttk.Button(self.system_pannel, text="Start All Opening", command=self.manager.start_all_opening).grid(row=row, column=3)

		#self.ticker_var.set('XIU.TO')
		#self.load_ticker_tab()


	def load_saved_tickers(self):
		if os.path.exists(TICKER_CONFIG_FILE):
			with open(TICKER_CONFIG_FILE, "r") as f:
				saved = json.load(f)
				for symbol in saved:
					self.ticker_var.set(symbol)
					self.load_ticker_tab()  # This should call your full load logic
			#print(f"[Loaded] {len(saved)} saved tickers from {TICKER_CONFIG_FILE}")
		else:
			print("[Info] No saved ticker file found.")



	def save_tickers(self):
		os.makedirs("configs", exist_ok=True)
		ticker_list = list(self.ticker_table_rows.keys())
		with open(TICKER_CONFIG_FILE, "w") as f:
			json.dump(ticker_list, f, indent=4)
		print(f"[Saved] {len(ticker_list)} tickers to {TICKER_CONFIG_FILE}")




	def set_user(self,user):

		self.user.set(user)

		if len(user)>0:
			self.account_status["background"] = "lightgreen"

	def on_mode_toggle(self, mm,changed_name):
		# Ensure only one mode checkbox is True
		for name in MODE_CHECKBOXES:
			if name != changed_name:
				var, _ = mm.vars.get(name, (None, None))
				if var:
					var.set(0)

	def get_sort_value(self, symbol, key):
		info = self.ticker_table_rows[symbol]

		#print(symbol,key)
		if key == "ticker":
			return symbol
		elif key in info:
			var = info[key]
			if hasattr(var, "get"):
				val = var.get()
				try:
					# Try convert to float if it's numeric
					return float(val)
				except (ValueError, TypeError):
					return val  # fallback to raw string
			return var
		else:
			return ""  # fallback if key not found
	def sort_ticker_table(self, key):
		ascending = self.sort_order.get(key, True)

		sortable = []
		for symbol in self.ticker_table_rows:
			val = self.get_sort_value(symbol, key)
			sortable.append((symbol, val))

		sortable.sort(key=lambda x: x[1], reverse=not ascending)
		self.sort_order[key] = not ascending

		for new_row, (symbol, _) in enumerate(sortable, start=1):
			row_info = self.ticker_table_rows[symbol]
			for col, widget in enumerate(row_info["widgets"]):
				widget.grid(row=new_row, column=col, padx=5, sticky="w")
			row_info["row"] = new_row




	def create_ticker_management_ui(self, symbol, mm):
		if symbol in self.ticker_table_rows:
			return  # Already exists

		row_idx = len(self.ticker_table_rows) + 1

		# Variables from mm instance
		status = mm.vars['Status'][0]
		inventory = mm.vars['cur_inv'][0]
		open_orders = mm.vars['openOrderCount'][0]
		notional = mm.vars['notionalAmount'][0]

		cur_trade = mm.vars['cur_traded'][0]
		cur_tradep= mm.vars['cur_tradedp'][0]

		svi_trade = mm.vars['svi_traded'][0]
		svi_tradep= mm.vars['svi_tradedp'][0]




		w =10

		# === Create and place widgets ===
		label = ttk.Label(self.ticker_table_frame, text=symbol, foreground="blue", cursor="hand2")
		label.grid(row=row_idx, column=0, padx=5, sticky="w")
		label.bind("<Button-1>", lambda e, sym=symbol: self.open_ticker_tab(sym))

		status_label = ttk.Label(self.ticker_table_frame, textvariable=status,width=w)
		status_label.grid(row=row_idx, column=1, padx=5, sticky="w")

		inv_label = ttk.Label(self.ticker_table_frame, textvariable=inventory,width=w)
		inv_label.grid(row=row_idx, column=2, padx=5, sticky="w")


		not_label = ttk.Label(self.ticker_table_frame, textvariable=notional,width=w)
		not_label.grid(row=row_idx, column=3, padx=5, sticky="w")

		orders_label = ttk.Label(self.ticker_table_frame, textvariable=open_orders,width=w)
		orders_label.grid(row=row_idx, column=4, padx=5, sticky="w")

		ct_label = ttk.Label(self.ticker_table_frame, textvariable=cur_trade,width=w)
		ct_label.grid(row=row_idx, column=5, padx=5, sticky="w")

		ctp_label = ttk.Label(self.ticker_table_frame, textvariable=cur_tradep,width=w)
		ctp_label.grid(row=row_idx, column=6, padx=5, sticky="w")

		svi_label = ttk.Label(self.ticker_table_frame, textvariable=svi_trade,width=w)
		svi_label.grid(row=row_idx, column=7, padx=5, sticky="w")

		svip_label = ttk.Label(self.ticker_table_frame, textvariable=svi_tradep,width=w)
		svip_label.grid(row=row_idx, column=8, padx=5, sticky="w")
		# Store all info + widgets for future sorting
		self.ticker_table_rows[symbol] = {
			"status": status,
			"inventory": inventory,
			'notional amount':notional,
			"orders": open_orders,
			'curt':cur_trade,
			'curtp':cur_tradep,
			'svit':svi_trade,
			'svitp':svi_tradep,
			"row": row_idx,
			"widgets": [label, status_label, inv_label, not_label,orders_label,ct_label,ctp_label,svi_label,svip_label]
		}

	# def init_ticker_management_table(self):
	# 	# === Scrollable canvas inside ticker_management_frame ===
	# 	canvas = tk.Canvas(self.ticker_management_frame, height=200)

	# 	scrollbar = ttk.Scrollbar(self.ticker_management_frame, orient="vertical", command=canvas.yview)
		
	# 	self.ticker_table_frame = ttk.Frame(canvas)
	# 	self.ticker_table_frame.bind(
	# 		"<Configure>",
	# 		lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
	# 	)

	# 	canvas.create_window((0, 0), window=self.ticker_table_frame, anchor="nw")
	# 	canvas.configure(yscrollcommand=scrollbar.set)

	# 	canvas.pack(side="left", fill="both", expand=True)
	# 	scrollbar.pack(side="right", fill="y")

	# 	# === Header row with sortable buttons ===
	# 	self.sort_order = {}  # Track current sort direction

	# 	headers = [("Ticker", "ticker"),
	# 			   ("Status", "status"),
	# 			   ("Inventory", "inventory"),
	# 			   ("Notional$","notional"),
	# 			   ("Open Orders", "Open Orders"),
	# 				("Current Trade", "orders"),
	# 				("Trade %", "orders"),
	# 				("SVI Trade", "orders"),
	# 				("SVI %", "orders"),									   				   ]

	# 	for col, (label, key) in enumerate(headers):
	# 		btn = ttk.Button(
	# 			self.ticker_table_frame,
	# 			text=label,width=12,
	# 			command=lambda k=key: self.sort_ticker_table(k)
	# 		)
	# 		btn.grid(row=0, column=col, padx=0, pady=2, sticky="w")
	# 		self.sort_order[key] = True

	# 	self.ticker_table_rows = {}  # symbol -> data/vars

	def init_ticker_management_table(self):
		# === Create container frame ===
		# self.ticker_management_frame = ttk.Frame(self.parent)  # or whatever your parent is
		# self.ticker_management_frame.pack(fill="both", expand=True)

		# === Fixed Header Frame ===
		header_frame = ttk.Frame(self.ticker_management_frame)
		header_frame.pack(fill="x")

		headers = [("Ticker", "ticker"),
				   ("Status", "status"),
				   ("Inventory", "inventory"),
				   ("Notional$", "notional"),
				   ("Open Orders", "Open Orders"),
				   ("Current Trade", "orders"),
				   ("Trade %", "orders"),
				   ("SVI Trade", "orders"),
				   ("SVI %", "orders")]

		self.sort_order = {}
		for col, (label, key) in enumerate(headers):
			btn = ttk.Button(
				header_frame,
				text=label,width=10,
				command=lambda k=key: self.sort_ticker_table(k)
			)
			btn.grid(row=0, column=col, padx=1, pady=2, sticky="w")
			self.sort_order[key] = True

		# === Scrollable Canvas ===
		canvas = tk.Canvas(self.ticker_management_frame, height=200)
		scrollbar = ttk.Scrollbar(self.ticker_management_frame, orient="vertical", command=canvas.yview)
		self.ticker_table_frame = ttk.Frame(canvas)

		self.ticker_table_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
		)

		canvas.create_window((0, 0), window=self.ticker_table_frame, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")

		self.ticker_table_rows = {}

	def open_ticker_tab(self, symbol):

		#print(self.marketmaking_tabs)
		if hasattr(self, 'marketmaking_tabs') and symbol in self.marketmaking_tabs:
			tab = self.marketmaking_tabs[symbol]
			self.marketmaking_notebook.select(tab)



	def delete_ticker(self, symbol):
		# 1. Remove widgets from Ticker Management table
		if symbol in self.ticker_table_rows:
			for widget in self.ticker_table_rows[symbol]["widgets"]:
				widget.destroy()
			del self.ticker_table_rows[symbol]

		# 2. Remove notebook tab
		if hasattr(self, 'marketmaking_tabs') and symbol in self.marketmaking_tabs:
			self.marketmaking_notebook.forget(self.marketmaking_tabs[symbol])
			del self.marketmaking_tabs[symbol]

		# 3. Remove mm instance from manager if tracked
		if hasattr(self.manager, "symbols") and symbol in self.manager.symbols:
			del self.manager.symbols[symbol]

		# 4. Save updated tickers
		self.save_tickers()

		print(f"[Deleted] {symbol} fully removed.")

	def load_ticker_tab(self, force=True):

		ticker = self.ticker_var.get().strip().upper()
		if not ticker:
			return

		mm = self.manager.load_ticker(ticker)

		if not mm:
			return 

		self.create_ticker_management_ui(ticker,mm)
		# Create new tab
		tab = ttk.Frame(self.marketmaking_notebook)
		self.marketmaking_notebook.add(tab, text=ticker)
		self.marketmaking_tabs[ticker] = tab
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
					cmd_func = mm.button_commands.get(cmd_name)
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
						widget = ttk.Entry(section_frame, textvariable=var, state="readonly", width=15)
					elif entry_type == "bool":
						if name in MODE_CHECKBOXES:
							widget = ttk.Checkbutton(section_frame, variable=var, command=lambda n=name: self.on_mode_toggle(mm,n))
						else:
							widget = ttk.Checkbutton(section_frame, variable=var)
					elif options:
						
						if 'Venue' in label:
							if ticker[-3:] in MARKET:
								options = MARKET[ticker[-3:]]


							if 'Reserve Venue' in label:
								options = MARKET['RESERVE']

							if var.get()=="":
								var.set(options[0])
							widget = ttk.Combobox(section_frame, textvariable=var, values=options, state="readonly", width=45)


						else:
							widget = ttk.Combobox(section_frame, textvariable=var, values=options, state="readonly", width=10)
						#mm.venues_options[name] = widget
					else:

						if entry_type=="float":
							widget = ttk.Entry(section_frame, textvariable=var, width=14,validate="key", validatecommand=self.float_check)
						elif entry_type=="int":
							widget = ttk.Entry(section_frame, textvariable=var, width=14,validate="key", validatecommand=self.int_check)
						else:
							widget = ttk.Entry(section_frame, textvariable=var, width=14)
					widget.grid(row=row, column=col * 2 + 1, sticky="w", padx=5, pady=5)
					row_tracker[row] = col + 1





		# Save Button at the bottom of the last section
		# ttk.Button(tab, text="Save", command=lambda: mm.save()).grid(
		# 	row=row_counter + 10, column=0, columnspan=FIELDS_PER_ROW * 2, pady=15, padx=10, sticky="w"
		# )

		# ttk.Button(
		# 	tab,
		# 	text="Delete Ticker",
		# 	command=lambda sym=ticker: self.delete_ticker(sym)
		# ).grid(
		# 	row=row_counter + 10, column=1,
		# 	columnspan=FIELDS_PER_ROW * 2, pady=15, padx=10, sticky="w"
		# )

class CollapsibleSection(ttk.Frame):
	def __init__(self, parent, title="", *args, **kwargs):
		super().__init__(parent, *args, **kwargs)

		self.showing = tk.BooleanVar(value=True)

		# Title row with toggle button
		self.toggle_button = ttk.Checkbutton(
			self, text=f"▼ {title}", variable=self.showing,
			command=self.toggle, style="Toolbutton"
		)
		self.toggle_button.grid(row=0, column=0, sticky="w", pady=(10, 0))

		# Container for child widgets
		self.content = ttk.Frame(self)
		self.content.grid(row=1, column=0, sticky="w")

	def toggle(self):
		if self.showing.get():
			self.toggle_button.configure(text=self.toggle_button.cget("text").replace("▶", "▼"))
			self.content.grid()
		else:
			self.toggle_button.configure(text=self.toggle_button.cget("text").replace("▼", "▶"))
			self.content.grid_remove()


MARKET={}


MARKET['.TO'] = ["AEQN ACTION AequitasLIT Limit Broker DAY",\
				 "AEQN ACTION AequitasNEO Limit Broker DAY",\
				 "ALPH ACTION ALPHA Limit Broker DAY",\
				 "CHIX ACTION SMART Limit Broker DAY",\
				 "LYNX ACTION LYNXSOR Limit Broker DAY",\
				 "OMGA ACTION OMEGASOR Limit Broker DAY",\
				 "TSX ACTION SweepSOR Limit Broker DAY",\
				 "XCSE ACTION CSESMRT Limit Broker DAY",\
				 "CX2 ACTION SMART Limit DAY",\
				 "CXD ACTION NasdaqCXD Limit DAY"]


MARKET['.VN'] = ["AEQN ACTION AequitasLIT Limit Broker DAY",\
				 "AEQN ACTION AequitasNEO Limit Broker DAY",\
				 "ALPH ACTION ALPHA Limit Broker DAY",\
				 "CHIX ACTION SMART Limit Broker DAY",\
				 "LYNX ACTION LYNXSOR Limit Broker DAY",\
				 "OMGA ACTION OMEGASOR Limit Broker DAY",\
				 "TSX ACTION SweepSOR Limit Broker DAY",\
				 "XCSE ACTION CSESMRT Limit Broker DAY",\
				 "CX2 ACTION SMART Limit DAY",\
				 "CXD ACTION NasdaqCXD Limit DAY"]


MARKET['.CN'] = ["AEQN ACTION AequitasLIT Limit Broker DAY",\
				 "AEQN ACTION AequitasNEO Limit Broker DAY",\
				 "CHIX ACTION SMART Limit Broker DAY",\
				 "LYNX ACTION LYNXSOR Limit Broker DAY",\
				 "OMGA ACTION OMEGASOR Limit Broker DAY",\
				 "CX2 ACTION SMART Limit DAY",\
				 "CSE ACTION CSE Limit Broker DAY",\
				 "CSE2 ACTION CSE2 Limit DAY",\
				 "CXD ACTION NasdaqCXD Limit DAY"]

MARKET['.CC'] = ["AEQN ACTION AequitasLIT Limit Broker DAY",\
				 "AEQN ACTION AequitasNEO Limit Broker DAY",\
				 "OMGA ACTION OMEGASOR Limit Broker DAY",\
				 "CXD ACTION NasdaqCXD Limit DAY",\
				 "CHIX ACTION SMART Limit Broker DAY"]


MARKET['RESERVE'] = ['AEQN Buy AequitasLIT Limit Broker DAY Reserve',
'AEQN Sell->Short AequitasLIT Limit Broker DAY Reserve']

if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager Market Making v1") 
	#root.geometry("1380x780")
	root.geometry("1520x1280")

	UI(root)


	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop() 