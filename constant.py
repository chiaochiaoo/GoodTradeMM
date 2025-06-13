#Spirits of the machine, accept my pleas, And walk amidst the gun, and fire it true.

from dataclasses import make_dataclass, asdict, field
import os
import json
#SYMBOL PARAMETERS
BID = "bid"
ASK = "ask"
RESISTENCE="resistence"
SUPPORT="support"
OPEN="open" 
HIGH="high"
LOW="low" 
CLOSE = "close"

# STATE

READY = "ready"
FILLING = "filling"
EXITING = "exiting"
FLAT = "flat"


SUMMARY = "summary"
SUMMARY_SYMBOL = "summary_symbol"


TIMESTAMP="timestamp"
TRADE_TIMESTAMP = "TRADE_timestamp"
PREMARKETHIGH="phigh"
PREMARKETLOW="plow"

#STATS
ATR ='ATR'
OHAVG='OHavg'
OHSTD = 'OHstd'
OLAVG = 'OLavg'
OLSTD ='OLstd'

#TP PARAMETER
AUTORANGE = "AR"
AUTOMANAGE = "AM"
RELOAD = "reload"
SELECTED = "selected"
ANCART_OVERRIDE = "ancartoverride"
USING_STOP = "Using_STOP"
FLATTENTIMER = "flattentimer"

ALGO_UIID = "algo_ui_id"
TIMER = "timer"
ACTRISK="actrisk"
ESTRISK="estrisk"
RISK_RATIO = "risk_ratio"
SIZE_IN = "size_in"

WR = "WR"
MR = "MR"
TR = "TR"

ALGO_MULTIPLIER = "Multiplier"

SYMBOL1_SHARE = "Symbol1_share"
SYMBOL2_SHARE = "Symbol2_share"

CURRENT_SHARE = "CURRENT_SHARE"
TARGET_SHARE = "TARGET_SHARE"
INPUT_TARGET_SHARE ="INTPU_SHARE"
RISK_PER_SHARE = "RISK_PER_SHARE"
AVERAGE_PRICE = "AVERAGE_PRICE"

AVERAGE_PRICE1 = "AP1"
AVERAGE_PRICE2 = "AP2"

LAST_AVERAGE_PRICE = "Last_average_price"
UNREAL = "UNREAL"
UNREAL_MIN = "UNREAL_MIN"
UNREAL_MAX = "UNREAL_MAX"
UNREAL_PSHR = "UNREAL_PSHR" 
REALIZED =  "REALIZED"
TOTAL_REALIZED = "TOTAL_REALIZED" 
STOP = "Stop"
STOP_LEVEL = "Stop_level"
SYMBOL = "Symbol"
MIND = "Msg"
RELOAD_TIMES = "Reloadtimes"

CUR_PROFIT_LEVEL = "Current_profit_level"

BREAKPRICE = "Breakprice"


CUSTOM = "custom"
PXT1 = "tpx1"
PXT2 = "tpx2"
PXT3 = "tpx3"
PXT4 = "tpx4"
PXT5 = "tpx5"
PXTF = "tpxF"


EMACOUNT = "EMAcount"
EMA8H="EMA8H"
EMA8L="EMA8L"
EMA8C="EMA8C"

EMA5H= "EMA5H"
EMA5L= "EMA5L"
EMA5C = "EMA5C"

EMA21H= "EMA21H"
EMA21L= "EMA21L"
EMA21C = "EMA21C"

TRIGGER_PRICE_1 = "Trigger_price_1"
TRIGGER_PRICE_2 = "Trigger_price_2"
TRIGGER_PRICE_3 = "Trigger_price_3"
TRIGGER_PRICE_4 = "Trigger_price_4"
TRIGGER_PRICE_5 = "Trigger_price_5"
TRIGGER_PRICE_6 = "Trigger_price_6"
TRIGGER_PRICE_7 = "Trigger_price_7"
TRIGGER_PRICE_8 = "Trigger_price_8"
TRIGGER_PRICE_9 = "Trigger_price_9"

#CURRENT_FIB_LEVEL = "Current Fib Level"
FIBCURRENT_MAX = "Fib Current Max"
FIBLEVEL1 = "Fib level 1"
FIBLEVEL2 = "Fib level 2"
FIBLEVEL3 = "Fib level 3"
FIBLEVEL4 = "Fib level 4"
EXIT = "Exit price"
ENTRY = "Entry price"

STATUS = "Status"
POSITION="Position"
MANASTRAT = "ManaStart"
ENSTRAT = "EntryStrat"
ENTYPE = "Entrytype"
ENTRYPLAN = "EntryPlan"
MANAGEMENTPLAN = "ManagementPlan"
TRADING_PLAN ="TradingPlan"
RISKTIMER = "Risktimer"

EXPECTED_MOMENTUM = "expected_momentum"
#TRIGGER PARA
SYMBOL_DATA = "symbol_data"
TP_DATA = "TP_DATA" 

#Algo STATUS
DONE = "Done"
PENDING = "Pending"
DEPLOYED = "DEPLOYED"
MATURING = "Maturing"
RUNNING = "Running"
REJECTED = "Rejected"
CANCELED= "Canceled"

#orders sies
LONG  = "Long"
SHORT = "Short"


#Entry Type
INSTANT=      'Instant'
INCREMENTAL = 'Incrmntl'
INCREMENTAL2 = 'NewIncremtl'

#Entry Plan
FADEUP = "Fadeup"
FADEDOWN = "Fadedown"
BREAISH =   "  Bearish"
BULLISH =   "  Bullish"
BREAKUP =   " BreakUp"
BREAKDOWN = " BreakDn"
BREAKANY =  "BreakAny"
DIPBUY = "Dipbuy"
RIPSELL = "Ripsell"
FADEANY = "FadeAny"
BREAKFIRST = "BreakFirst"
FREECONTROL = "FreeControl"


####

MARKETMAKING = "MarketMaking"
PAIRONETOTWO = "PairOneToTwo"


#MANA Plan
NONE =          "NONE"
THREE_TARGETS = "Three tgts "
SMARTTRAIL =  "SmartTrail"
ANCARTMETHOD =  "AC METHOD"
ONETOTWORISKREWARD = "1:2 Exprmntl"
ONETOTWOWIDE = "1:2 Wide"
HOLDTILCLOSE = "HTC"

FULLMANUAL = "FullManual"
SEMIMANUAL = "SemiManual"


MARKETACTION = "MarketAction"

MARKETLONG = "MarketLong"
MARKETSHORT = "MarketShort"

INSTANTLONG = "Instant Long"
INSTANTSHORT = "Instant Short"
TARGETLONG = "Target Long"
TARGETSHORT = "Target Short"


HOLDXSECOND = "HoldXSecond"
FIBONO = "FibAdjstd"
FIBO = "Fib only"
EMASTRAT =  "EMA strategy"
SCALPATRON = "Scalpatron"
TRENDRIDER = "TrendRider"

ONETOTWORISKREWARDOLD = "1:2 RiskReward"

EM_STRATEGY = "Exp.Mtm"
##### ORDER TYPE ####

BUY = "Buy"
SELL = "Sell"
FLATTEN = "Flatten"


PASSIVELONG = "PASSIVELONG"
PASSIVESHORT = "PASSIVESHORT"


PASSIVEBUY = "Passivebuy"
PASSIVESELL = "Passivesell"


PASSIVEBUY_L = "Passivebuy_L"
PASSIVESELL_L = "Passivesell_L"


IOCBUY = "IoCBuy"
IOCSELL = "IoCSell"

LIMITBUY = "Litmit Buy" 
LIMITSELL = "Limit Sell"

CANCEL = "Cancel"
CANCELALL = "CancelAll"
REGISTER = "Register"
DEREGISTER = "Deregister"
STOPBUY = "StopBuy"
STOPSELL= "StopSell"

BREAKUPBUY = "Breakupbuy"
BREAKDOWNSELL = "Breakdownsell"
ADD ="add"
MINUS="minus"


##COLOR

GREEN = "#97FEA8"
DEFAULT = "#d9d9d9"
LIGHTYELLOW = "#fef0b8"
YELLOW =  "#ECF57C"
VERYLIGHTGREEN = "#ecf8e1"
LIGHTGREEN = "#97FEA8"
STRONGGREEN = "#3DFC68"
STRONGRED = "#FC433D"
DEEPGREEN = "#059a12"


STATUS = "status"
SETTINGS = "Default Mode"
PRICE_ZONES = "Default Mode"
MANAGEMENT = "Management"
COMMANDS = "COMMANDS"
INACTIVE = "Inactive"
DEFAULT_MODE = "Default Mode"
RESTRICTIVE_MODE = "Restrictive Mode"
OPENING_MODE = "Opening Mode"
AGGRESIVE_MODE = 'Aggresive Mode'

VENUES = "Venues"
# === Step 1: Central Config Schema ===
CONFIG_SCHEMA = [
    {"name": "Ticker",      "label": "Ticker",            "section": STATUS, "type": "string", "row": 0},
    {"name": "Status",      "label": "Status",            "section": STATUS, "type": "string", "row": 0, "default": INACTIVE, "readonly": True},
    {"name": "bid",  "label": "Bid",            "section": STATUS, "type": "float",  "row": 0, "readonly": True},
    {"name": "ask",   "label": "Ask",            "section": STATUS, "type": "float",  "row": 0,"readonly":True},

    {"name": "cur_inv",     "label": "Current Inventory", "section": STATUS, "type": "int",    "row": 0, "readonly": True},
    {"name": "unrealized",  "label": "Unreal",            "section": STATUS, "type": "float",  "row": 0, "readonly": True},


    {"name": "cur_traded",   "label": "Current Trade", "section": STATUS, "type": "int",    "row": 1,'default':0, "readonly": True},
    {"name": "cur_tradedp",   "label": "Current Trade %", "section": STATUS, "type": "float",    "row": 1, 'default':0,"readonly": True},
    {"name": "svi_traded",     "label": "SVI trade", "section": STATUS, "type": "int",    "row": 1, 'default':0,"readonly": True},

    {"name": "svi_tradedp",     "label": "SVI trade %", "section": STATUS, "type": "float",    "row": 1,'default':0, "readonly": True},


    {"name": "openOrderCount",    "label": "Open Order Count","section": STATUS, "type": "int",  "row": 2,"readonly":True},
    {"name": "notionalAmount",    "label": "Notional Amount","section": STATUS, "type": "float",  "row": 2,"readonly":True},
    {"name": "RealizedPnLShutdown",  "label": "RPnLShutdown",            "section": STATUS, "type": "float",  "row": 2, "readonly": True},
    {"name": "FavourableBuyingConditions",  "label": "FavBuyingConds",   "section": STATUS, "type": "float",  "row": 2, "readonly": True},





    {"name": "d_Venue","label": "Default Venue",     "section": VENUES, "type": "string", "row": 0, "options": ["T1", "T2", "T3"]},
    {"name": "a_Venue",    "label": "Aggressive Venue",  "section": VENUES, "type": "string", "row": 0, "options": ["T1", "T2", "T3"]},
    # {"name": "d_enabled",     "label": "Default Mode",      "section": STATUS, "type": "bool",   "row": 1,"readonly":True},
    # {"name": "r_enabled",     "label": "Restrictive Mode", "section": STATUS, "type": "bool",   "row": 1,"readonly":True},
    # {"name": "a_enabled",     "label": "Aggresive Mode",      "section": STATUS, "type": "bool",   "row": 1,"readonly":True},
    # {"name": "o_enabled",    "label": "Opening Enabled",      "section": STATUS, "type": "bool",   "row": 1,"readonly":True},

    {"name": "start_pending",   "label": "Pause Algo",    "section": COMMANDS, "type": "button", "row": 0, "command": "start_pending"},
    {"name": "cancel_orders",   "label": "Cancel Orders",    "section": COMMANDS, "type": "button", "row": 0, "command": "cancel_orders"},
    {"name": "fetch_data",   "label": "Fetch Database",    "section": COMMANDS, "type": "button", "row": 0, "command": "fetch_data"},

    {"name": "start_default",   "label": "Start Default",    "section": SETTINGS, "type": "button", "row": 7, "command": "start_default"},

    #{"name": "start_test",   "label": "Start Test",    "section": SETTINGS, "type": "button", "row": 7, "command": "start_test"},


    {"name": "d_starttime", "label": "StartTime",  "section": SETTINGS, "type": "int", "row": 1, "default": 575},
    {"name": "d_stoptime", "label": "StopTime",  "section": SETTINGS, "type": "int", "row": 1, "default": 955},
    {"name": "boardlot",    "label": "Board Lot",         "section": SETTINGS, "type": "int",    "row": 1,"default": 100,"readonly": True},
    {"name": "ticksize",    "label": "Tick Size",         "section": SETTINGS, "type": "float",  "row": 1,"default": 0.01,"readonly": True},
    {"name": "MaxInventorySize",     "label": "Max Inventory",   "section": SETTINGS, "type": "int",    "row": 1,"default": 1000,},
    {"name": "MaxAllowedUPnL",     "label": "Max Loss",          "section": SETTINGS, "type": "int",    "row": 1,"default": 1000,},
    # {"name": "email_alert", "label": "Email Alert",       "section": SETTINGS, "type": "bool",   "row": 0},

    {"name": "bidmult",     "label": "Glb Bid Mult",      "section": SETTINGS, "type": "int",    "row": 2, "default": 1},
    {"name": "askmult",     "label": "Glb Ask Mult",      "section": SETTINGS, "type": "int",    "row": 2, "default": 1},


    {"name": "AdjustedSpread",  "label": "Adj Spread",        "section": SETTINGS, "type": "float",  "row": 2, "default": 0.01},
    {"name": "reserve_bidmult", "label": "Rsv Bid Mult",  "section": SETTINGS, "type": "int", "row": 2, "default": 2},
    {"name": "reserve_askmult", "label": "Rsv Ask Mult",  "section": SETTINGS, "type": "int", "row": 2, "default": 2},
    {"name": "BuyZone1",    "label": "Buy Zone1",         "section": SETTINGS, "type": "float", "row": 3, "default": 0},
    {"name": "BuyZone2",    "label": "Buy Zone2",         "section": SETTINGS, "type": "float", "row": 3, "default": 0},
    {"name": "BuyZone3",    "label": "Buy Zone3",         "section": SETTINGS, "type": "float", "row": 3, "default": 0},
    {"name": "SellZone1",   "label": "Sell Zone1",        "section": SETTINGS, "type": "float", "row": 4, "default": 0},
    {"name": "SellZone2",   "label": "Sell Zone2",        "section": SETTINGS, "type": "float", "row": 4, "default": 0},
    {"name": "SellZone3",   "label": "Sell Zone3",        "section": SETTINGS, "type": "float", "row": 4, "default": 0},

    # {"name": "d_enabled",   "label": "Default Mode Enabled", "section": SETTINGS, "type": "bool",   "row": 0,"readonly":True},
    # {"name": "loadData",    "label": "Load Data",         "section": SETTINGS, "type": "button", "row": 3},
    # {"name": "r_enabled",         "label": "Restrictive Enabled", "section": RESTRICTIVE_MODE, "type": "bool",   "row": 0,"readonly":True},

    {"name": "start_restrictive",   "label": "Start Restrictive",    "section": RESTRICTIVE_MODE, "type": "button", "row": 0, "command": "start_restrictive"},
    {"name": "r_starttime", "label": "StartTime",  "section": RESTRICTIVE_MODE, "type": "int", "row": 0, "default": 575},
    {"name": "r_stoptime", "label": "StopTime",  "section": RESTRICTIVE_MODE, "type": "int", "row": 0, "default": 955},
    {"name": "r_nbbo",      "label": "Post on L1 ask",    "section": RESTRICTIVE_MODE, "type": "bool",   "row": 0},
    {"name": "r_bidmult",   "label": "Bid Mult",           "section": RESTRICTIVE_MODE, "type": "int",  "row": 0, "default": 1},
    {"name": "r_askmult",   "label": "Ask Mult",          "section": RESTRICTIVE_MODE, "type": "int",  "row": 0, "default": 1},



    # {"name": "PssVenue",    "label": "Passive Venue",     "section": RESTRICTIVE_MODE, "type": "string", "row": 2, "options": ["T1", "T2", "T3"]},
    # {"name": "AggVenue",    "label": "Aggressive Venue",  "section": RESTRICTIVE_MODE, "type": "string", "row": 2, "options": ["T1", "T2", "T3"]},
    # {"name": "OpnVenue",    "label": "Open Venue",        "section": RESTRICTIVE_MODE, "type": "string", "row": 2, "options": ["T1", "T2", "T3"]},



    # {"name": "o_enabled",    "label": "Opening Enabled",      "section": OPENING_MODE, "type": "bool",   "row": 0,"readonly":True},
    {"name": "start_opening",   "label": "Start Opening",    "section": OPENING_MODE, "type": "button", "row": 0, "command": "start_opening"},
    {"name": "o_starttime", "label": "StartTime",  "section": OPENING_MODE, "type": "int", "row": 0, "default": 565},
    {"name": "o_bidmult",   "label": "Bid Mult",           "section": OPENING_MODE, "type": "int",  "row": 0, "default": 1},
    {"name": "o_askmult",   "label": "Ask Mult",          "section": OPENING_MODE, "type": "int",  "row": 0, "default": 1},


    # {"name": "a_enabled",     "label": "Aggresive Enabled",      "section": AGGRESIVE_MODE, "type": "bool",   "row": 0},


    {"name": "a_bidmult",   "label": "Bid Mult",           "section": AGGRESIVE_MODE, "type": "int",  "row": 0, "default": 1},
    {"name": "a_askmult",   "label": "Ask Mult",          "section": AGGRESIVE_MODE, "type": "int",  "row": 0, "default": 1},



    {"name": "a_action",    "label": "Aggresive Action",  "section": AGGRESIVE_MODE, "type": "string", "row": 0, "options": ["Buy", "Sell"],'default':'Buy'},
    {"name": "a_size",       "label": "Total Size",          "section": AGGRESIVE_MODE, "type": "int",  "row": 0, "default": 100},


    {"name": "a_percentage",   "label": "% Volume Target",          "section": AGGRESIVE_MODE, "type": "float",  "row": 1, "default": 0.05},
    {"name": "a_duration",   "label": "Total Duration(Min)",          "section": AGGRESIVE_MODE, "type": "int",  "row": 1, "default": 60},
    {"name": "a_type",    "label": "Target Volume By",  "section": AGGRESIVE_MODE, "type": "string", "row": 1, "options": ["Size", "Percentage"],'default':'Size'},

    {"name": "v_hitalert",   "label": "Hit Notification",          "section": AGGRESIVE_MODE, "type": "bool",  "row": 1, "default": 1},

    {"name": "start_aggresive",   "label": "Start Aggresive",    "section": AGGRESIVE_MODE, "type": "button", "row": 2, "command": "start_aggresive"},

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
    "bool": int,
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
    if typ=='bool':default_val = False
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