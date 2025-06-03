import os
import json
import tkinter as tk
from dataclasses import make_dataclass, asdict, field

import tkinter as tk
from tkinter import ttk
import os


STATUS = "status"
SETTINGS = "settings"
PRICE_ZONES = "price zones"
MANAGEMENT = "Management"
RESTRICTIVE_MODE = "Restrictive Mode"
OPENING_MODE = "Opening Mode"
AGGRESIVE_MODE = 'Aggresive Mode'
VOLUME_MODE = 'Volume Mode'

# === Step 1: Central Config Schema ===
CONFIG_SCHEMA = [
    {"name": "Ticker",      "label": "Ticker",            "section": STATUS, "type": "string", "row": 0},
    {"name": "Status",      "label": "Status",            "section": STATUS, "type": "string", "row": 0, "default": "Pending", "readonly": True},
    {"name": "cur_inv",     "label": "Current Inventory", "section": STATUS, "type": "int",    "row": 0, "readonly": True},
    {"name": "unrealized",  "label": "Unreal",            "section": STATUS, "type": "float",  "row": 0},
    {"name": "realized",    "label": "Real",              "section": STATUS, "type": "float",  "row": 0},


    {"name": "d_enabled",     "label": "Default Mode",      "section": STATUS, "type": "bool",   "row": 1},
    {"name": "r_enabled",     "label": "Restrictive Mode", "section": STATUS, "type": "bool",   "row": 1},
    {"name": "a_enabled",     "label": "Aggresive Mode",      "section": STATUS, "type": "bool",   "row": 1},
    {"name": "o_enabled",    "label": "Opening Enabled",      "section": STATUS, "type": "bool",   "row": 1},

    {"name": "adj_Spread",  "label": "Adj Spread",        "section": STATUS, "type": "float",  "row": 2, "default": 0.01},
    {"name": "boardlot",    "label": "Board Lot",         "section": SETTINGS, "type": "int",    "row": 0},
    {"name": "ticksize",    "label": "Tick Size",         "section": SETTINGS, "type": "float",  "row": 0},
    {"name": "MAX_INV",     "label": "Max Inventory",     "section": SETTINGS, "type": "int",    "row": 0},
    {"name": "maxLoss",     "label": "Max Loss",          "section": SETTINGS, "type": "int",    "row": 0},
    {"name": "email_alert", "label": "Email Alert",       "section": SETTINGS, "type": "bool",   "row": 0},
    {"name": "defaultVenue","label": "Default Venue",     "section": SETTINGS, "type": "string", "row": 1, "options": ["T1", "T2", "T3"]},
    {"name": "bidmult",     "label": "Glb Bid Mult",      "section": SETTINGS, "type": "int",    "row": 1, "default": 1},
    {"name": "askmult",     "label": "Glb Ask Mult",      "section": SETTINGS, "type": "int",    "row": 1, "default": 1},

    {"name": "start_btn",   "label": "Start Strategy",    "section": MANAGEMENT, "type": "button", "row": 1, "command": "start_strategy"},
    {"name": "stop_btn",    "label": "Stop Strategy",     "section": MANAGEMENT, "type": "button", "row": 1, "command": "start_strategy"},
    {"name": "reserve_bidmult", "label": "Rsv Bid Mult",  "section": PRICE_ZONES, "type": "int", "row": 0, "default": 0},
    {"name": "reserve_askmult", "label": "Rsv Ask Mult",  "section": PRICE_ZONES, "type": "int", "row": 0, "default": 0},
    {"name": "buyzone1",    "label": "Buy Zone1",         "section": PRICE_ZONES, "type": "int", "row": 1, "default": 0},
    {"name": "buyzone2",    "label": "Buy Zone2",         "section": PRICE_ZONES, "type": "int", "row": 1, "default": 0},
    {"name": "buyzone3",    "label": "Buy Zone3",         "section": PRICE_ZONES, "type": "int", "row": 1, "default": 0},
    {"name": "sellzone1",   "label": "Sell Zone1",        "section": PRICE_ZONES, "type": "int", "row": 2, "default": 0},
    {"name": "sellzone2",   "label": "Sell Zone2",        "section": PRICE_ZONES, "type": "int", "row": 2, "default": 0},
    {"name": "sellzone3",   "label": "Sell Zone3",        "section": PRICE_ZONES, "type": "int", "row": 2, "default": 0},
    {"name": "loadData",    "label": "Load Data",         "section": PRICE_ZONES, "type": "button", "row": 3},


    {"name": "r_enabled",         "label": "Restrictive Enabled", "section": RESTRICTIVE_MODE, "type": "bool",   "row": 0},

    {"name": "r_nbbo",      "label": "Post on L1 ask",    "section": RESTRICTIVE_MODE, "type": "bool",   "row": 0},
    {"name": "r_bidmult",   "label": "Bid Mult",           "section": RESTRICTIVE_MODE, "type": "int",  "row": 0, "default": 1},
    {"name": "r_askmult",   "label": "Ask Mult",          "section": RESTRICTIVE_MODE, "type": "int",  "row": 0, "default": 1},
    # {"name": "PssVenue",    "label": "Passive Venue",     "section": RESTRICTIVE_MODE, "type": "string", "row": 2, "options": ["T1", "T2", "T3"]},
    # {"name": "AggVenue",    "label": "Aggressive Venue",  "section": RESTRICTIVE_MODE, "type": "string", "row": 2, "options": ["T1", "T2", "T3"]},
    # {"name": "OpnVenue",    "label": "Open Venue",        "section": RESTRICTIVE_MODE, "type": "string", "row": 2, "options": ["T1", "T2", "T3"]},



    {"name": "o_enabled",    "label": "Opening Enabled",      "section": OPENING_MODE, "type": "bool",   "row": 0},
    {"name": "o_bidmult",   "label": "Bid Mult",           "section": OPENING_MODE, "type": "int",  "row": 0, "default": 1},
    {"name": "o_askmult",   "label": "Ask Mult",          "section": OPENING_MODE, "type": "int",  "row": 0, "default": 1},


    {"name": "a_enabled",     "label": "Aggresive Enabled",      "section": AGGRESIVE_MODE, "type": "bool",   "row": 0},

    {"name": "a_action",    "label": "Aggresive Action",  "section": AGGRESIVE_MODE, "type": "string", "row": 0, "options": ["Buy", "Sell"],'default':'Buy'},
    {"name": "a_type",    "label": "Target Volume By",  "section": AGGRESIVE_MODE, "type": "string", "row": 0, "options": ["Size", "Percentage"],'default':'Size'},

    {"name": "a_bidmult",   "label": "Bid Mult",           "section": AGGRESIVE_MODE, "type": "int",  "row": 1, "default": 1},
    {"name": "a_askmult",   "label": "Ask Mult",          "section": AGGRESIVE_MODE, "type": "int",  "row": 1, "default": 1},


    {"name": "a_size",       "label": "Total Size",          "section": AGGRESIVE_MODE, "type": "int",  "row": 2, "default": 100},
    {"name": "a_percentage",   "label": "% Volume Target",          "section": AGGRESIVE_MODE, "type": "float",  "row": 2, "default": 0.05},
    {"name": "a_duration",   "label": "Total Duration(Min)",          "section": AGGRESIVE_MODE, "type": "int",  "row": 2, "default": 60},
    {"name": "a_Venue",    "label": "Aggressive Venue",  "section": AGGRESIVE_MODE, "type": "string", "row": 1, "options": ["T1", "T2", "T3"]},
    {"name": "v_hitalert",   "label": "Hit Notification",          "section": AGGRESIVE_MODE, "type": "bool",  "row": 0, "default": 1},




]


MODE_CHECKBOXES = [
    'd_enabled',
    "r_enabled",         # Restrictive Mode
    "o_enabled",          # Opening Mode
    "a_enabled",         # Aggressive Mode
]


# === Step 2: Dynamic TickerConfig Class ===
TYPE_MAP = {
    "string": str,
    "int": int,
    "float": float,
    "bool": bool,
    "button": None 
}

# Deduplicate names when creating dataclass fields
used_names = set()
fields_spec = []

for entry in CONFIG_SCHEMA:
    name = entry["name"]
    typ = entry["type"]

    if typ not in TYPE_MAP or TYPE_MAP[typ] is None:
        continue  # skip unsupported types like button

    if name in used_names:
        continue  # skip duplicates

    used_names.add(name)
    py_type = TYPE_MAP[typ]
    default_val = entry.get("default", py_type())
    fields_spec.append((name, py_type, field(default=default_val)))

TickerConfig = make_dataclass("TickerConfig", fields_spec)

def config_save(self, folder="configs"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{self.Ticker}.json")
    with open(path, "w") as f:
        json.dump(asdict(self), f, indent=4)
    print(f"[Saved] {path}")

@staticmethod
def config_load(ticker, folder="configs"):
    path = os.path.join(folder, f"{ticker}.json")
    with open(path, "r") as f:
        data = json.load(f)
    return TickerConfig(**data)
# Attach methods
TickerConfig.save = config_save
TickerConfig.load = config_load
FIELDS_PER_ROW= 6
# === Step 3: TickerMM Class with tkinter Variables ===

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

class TickerMM:
    def __init__(self, ticker: str, folder="configs", override=False, **override_values):
        self.vars = {}
        self.ticker = ticker

        # Load from JSON or override
        if override:
            self.data = {
                entry["name"]: override_values.get(
                    entry["name"],
                    entry.get("default", self.default_for(entry["type"]))
                )
                for entry in CONFIG_SCHEMA
            }
            self.data["Ticker"] = ticker
        else:
            self.data = TickerConfig.load(ticker, folder).__dict__

        # Create tk.Variable without a master
        for entry in CONFIG_SCHEMA:

            if entry["type"] == "button":
                continue  # Skip buttons
            name = entry["name"]
            typ = entry["type"]
            value = self.data.get(name, self.default_for(typ))

            if typ == "int" or typ =='bool':
                var = tk.IntVar(value=value)
            elif typ == "float":
                var = tk.DoubleVar(value=value)
            else:
                var = tk.StringVar(value=value)

            setattr(self, name, var)
            self.vars[name] = (var, typ)

    def default_for(self, typ):
        return 0 if typ == "int" else 0.0 if typ == "float" else ""

    def to_config(self):
        values = {}
        for name, (var, typ) in self.vars.items():
            try:
                value = var.get()
            except tk.TclError:
                # Fallback for empty entry fields
                if typ == "int":
                    value = 0
                elif typ == "float":
                    value = 0.0
                elif typ == "bool":
                    value = False
                else:
                    value = ""
            values[name] = value
        return TickerConfig(**values)
    def save(self, folder="configs"):
        config = self.to_config()
        config.save(folder=folder)

    def __repr__(self):
        lines = [f"<TickerMM: {self.ticker}>"]
        for entry in CONFIG_SCHEMA:
            name = entry["name"]
            label = entry["label"]
            value = self.vars[name][0].get()
            lines.append(f"  {label}: {value}")
        return "\n".join(lines)

# # # === Step 4: Quick Test ===
# if __name__ == "__main__":

#     tk.Tk()
#     mm = TickerMM("AAPL", override=True, boardlot=100, ticksize=0.01, MAX_INV=500)
#     print(mm)
#     mm.cur_inv.set(250)
#     mm.save()  # saves to configs/AAPL.json

#     # Reload from file
#     mm2 = TickerMM("AAPL")
#     print("Loaded from file:", mm2)

class TickerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ticker Config UI")
        self.geometry("1400x1000")
        self.mm = None  # TickerMM instance

        self.entries = {}  # { name: Entry widget }
        self.button_commands = {
            "start_strategy": self.start_strategy,
            "stop_strategy": self.stop_strategy,
            # Add more as needed
        }
        self.build_ui()


    def start_strategy(self):
        print(f"[{self.mm.ticker}] Strategy started")

    def stop_strategy(self):
        print(f"[{self.mm.ticker}] Strategy stopped")

    def build_ui(self):
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Row 0: Ticker Entry + Load Button
        ttk.Label(self.main_frame, text="Ticker:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.ticker_var = tk.StringVar()
        self.ticker_entry = ttk.Entry(self.main_frame, textvariable=self.ticker_var, width=20)
        self.ticker_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        load_button = ttk.Button(self.main_frame, text="Load / Create", command=self.load_ticker_tab)
        load_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        self.marketmaking_notebook = ttk.Notebook(self.main_frame)
        self.marketmaking_notebook.place(x=0,rely=0,relheight=1,relwidth=1)

        self.ticker_var.set('DEM')
        self.load_ticker_tab(False)

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
        if os.path.exists(f"configs/{ticker}.json") and not force:
            mm = TickerMM(ticker)
        else:
            mm = TickerMM(ticker, override=True)
            mm.save()

        self.mm = mm

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
        ttk.Button(tab, text="Save", command=lambda: self.mm.save()).grid(
            row=row_counter + 10, column=0, columnspan=FIELDS_PER_ROW * 2, pady=15, padx=10, sticky="w"
        )



if __name__ == "__main__":
    app = TickerUI()
    app.mainloop()