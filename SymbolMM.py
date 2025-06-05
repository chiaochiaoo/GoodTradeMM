import os
import json
import tkinter as tk
import requests 
from dataclasses import make_dataclass, asdict, field
from Util_functions import *

import tkinter as tk
from tkinter import ttk
import os
from constant import *
from datetime import datetime

import mysql.connector
def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return data


# http://localhost:8080/CancelOrder?type=ordernumber&ordernumber=QIAOSUN_00000007M17D25C100000


def fetch_data(symbol):

    try:
        MYSQL_USER = "webuser"
        MYSQL_PASSWORD = "Domination77$$"
        MYSQL_DATABASE = "summitdata"
        PORT = 3306

        # Connect to the MySQL server
        connection = mysql.connector.connect(
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            host="10.29.10.143",
            database=MYSQL_DATABASE,
            port=PORT,
            auth_plugin='mysql_native_password'
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # Create a cursor object
            cursor = connection.cursor()

            # List of symbols for the mmdata query
            #mmdata_symbols = ['ELEM.CN', 'LEXT.CN', 'ESPN.VN', 'BATX.CN', 'CRTL.CN', 'ANT.CN']
            
            #query = "SELECT * FROM algoinfo WHERE Symbol = %s;"
            query = f"SELECT * FROM algoinfo WHERE Symbol = '{symbol}';"
            cursor.execute(query)
            rows = cursor.fetchall()
            column_names = [i[0] for i in cursor.description]

            results = [dict(zip(column_names, row)) for row in rows]

            # print(column_names)
            # print(results[0])
            return results[0]
            # Print JSON with Decimal safely handled
            #print(json.dumps(results, indent=4, cls=DecimalEncoder))

        cursor.close()
        connection.close()
    except Exception as e:

        print(e)
        return {}


# d =fetch_data('CRTL.CN')



# today = datetime.today().date()



# Calculate the difference
# days_remaining = (d['DayOfSharesUnrestricted'] - today).days
# print(days_remaining)




BUY = "Buy"
SELL ="Sell->Short"

TEST_MODE = True 

class SymbolMM:
    def __init__(self, symbol: str,manager, folder="configs", override=False, **override_values):

        self.vars = {}
        self.symbol = symbol
        self.manager = manager

        self.data_init(symbol,folder,override,override_values)

        self.button_commands = {
            "start_default": self.start_default,
            "start_restrictive": self.start_restrictive,
            "start_opening":self.start_opening,
            "start_aggresive":self.start_aggresive,
            'start_test':self.start_test,
            'start_pending':self.start_pending,
            'cancel_orders':self.cancel_orders,
            'fetch_data':self.fetch_db_data,
            # Add more as needed
        }

        self.mode =INACTIVE

        self.rejection = 0

        self.bid =0
        self.ask =0

        self.bid_change = False
        self.ask_change = False 


        self.order_book = {}
        self.open_order_number = 0

        self.pc=0

        self.l1_ts =0

        self.inv =0
        self.average_price=0

        self.unreal =0

        self.board_setting = False 


        self.nbids={}
        self.nasks={}

        self.rbids ={}
        self.rasks ={}

        for i in range(5):
            self.nbids[i]=0
            self.nasks[i]=0

            self.rbids[i]=0
            self.rasks[i]=0

        self.venues_options ={}
        self.set_up_venue()

    def fetch_db_data(self):

        select = ['RealizedPnLShutdown','FavourableBuyingConditions','MaxInventorySize','MaxAllowedUPnL','BuyZone1','BuyZone2','BuyZone3','SellZone1','SellZone2','SellZone3','AdjustedSpread']
        d = fetch_data(self.symbol)

        for j,i in d.items():
            if j in select:
                try:
                    self.set_variable(j,i)
                except:
                    print("problem:",j,i)

        # 'RealizedPnLShutdown'  '1'
        # 'FavourableBuyingConditions' '1'


        # 'MaxInventorySize' 'MAX_INV'
        # 'MaxAllowedUPnL' 'maxLoss'


        # 'BuyZone1':'bz1'
        # 'BuyZone2' 'bz2'
        # 'BuyZone3' 'bz3'
        # 'SellZone1' 'sz1'
        # 'SellZone2' 'sz2'
        # 'SellZone3' 'sz3'

        # # 'DayOfSharesUnrestricted' 'cur_inv'
        # 'AdjustedSpread' 'adj_Spread'



    def rejection_received(self):

        self.rejection+=1 

        print(self.symbol,self.rejection)
        if self.rejection>2:
            self.start_pending()
    def set_up_venue(self):
        pass

    def start_pending(self):

        self.mode = INACTIVE
        self.vars['Status'][0].set(self.mode)

    def start_default(self):
        self.mode = DEFAULT_MODE 
        self.vars['Status'][0].set(self.mode)

    def start_test(self):
        self.mode = 'TEST' 

        self.vars['Status'][0].set(self.mode)

        # NBBO

        action =BUY
        price = self.nbids[0] 
        order = self.vars['d_Venue'][0].get()
        board_lot =self.vars['boardlot'][0].get()

        self.post_cmd(order,price,board_lot,action)


    def start_restrictive(self):
        self.mode = RESTRICTIVE_MODE 
        self.vars['Status'][0].set(self.mode)

        # 1 level behind nbbo.
        ### STEP 1 , CHECK WHATS THERE ###

        ### STEP 2 , CHECK WHO SHOULD BE CANCELD ###

        ### STEP 3. CHECK WHO SHOULD BE THERE ###


    def start_opening(self):
        self.mode = OPENING_MODE 
        self.vars['Status'][0].set(self.mode)


    def start_aggresive(self):
        self.mode = AGGRESIVE_MODE 
        self.vars['Status'][0].set(self.mode)


    def sysmbol_inspection(self):

        if self.mode == RESTRICTIVE_MODE:
            
            self.inspection_restrictive()

        elif self.mode == INACTIVE:


            self.insepection_inactive()

    def insepection_inactive(self):
        self.cancel_orders()

        
    def inspection_restrictive(self):

        ## get should.
        vals = [self.nbids[1],self.nbids[2],self.nasks[1]*-1,self.nasks[2]*-1]
        a1enable = self.get_variable('r_nbbo')

        if a1enable:
            vals.append(self.nasks[0]*-1)

        cancel_list = []

        for price in self.order_book.keys():
            if price not in vals:
                cancel_list.append(price)
        ## cancel that.

        send_list = []
        for price in vals:
            if price not in self.order_book.keys():
                send_list.append(price)

        ## send that .
        #print('cancel:',cancel_list,"  send:",send_list)


        if len(cancel_list)>0:
            print(cancel_list)
        if len(send_list)>0:
            print(send_list)

        for i in cancel_list:
            self.cancel_order(self.order_book[i])


        order = self.vars['d_Venue'][0].get()
        board_lot =self.vars['boardlot'][0].get()

        for price in send_list:

            if price>0:
                action = BUY 
            else:
                action =SELL

            price = abs(price)
            self.post_cmd(order,price,board_lot,action)


    def cancel_orders(self):
        cancel_list = []

        for price in self.order_book.keys():
            cancel_list.append(price)

        for i in cancel_list:
            self.cancel_order(self.order_book[i])


    def cancel_order(self,ordername):

        req = f'http://127.0.0.1:8080/CancelOrder?type=ordernumber&ordernumber={ordername}'
        
        r = requests.post(req)

        print(ordername)


    def post_cmd(self,order,price,share,action):

        order = order.replace("ACTION",action)

        if TEST_MODE:
            order = order.replace("Broker ","")
        req = f'http://127.0.0.1:8080/ExecuteOrder?symbol={str(self.symbol)}&limitprice={str(price)}&ordername={order}&shares={str(share)}'
        
        print(order,req)
        r = requests.post(req)


    def update_orderbook(self,new_order):
        #refresh.
        self.order_book = new_order

        self.open_order_number = len(self.order_book)
        self.set_variable('openOrderCount',self.open_order_number)



    def get_l1(self):

        try:
            postbody = "http://127.0.0.1:8080/GetLv1?symbol=" + self.symbol 

            r= requests.get(postbody)

            stream_data = r.text

            bid = float(find_between(stream_data, "BidPrice=\"", "\""))
            ask = float(find_between(stream_data, "AskPrice=\"", "\""))
            pc = float(find_between(stream_data, "ClosePrice=\"", "\""))
            ts = find_between(stream_data, "MarketTime=\"", "\"")

            if self.bid!=bid:
                self.bid_change = True 
            else:
                self.bid_change = False 

            if self.ask!=ask:
                self.ask_change = True 
            else:
                self.ask_change = False 

            self.bid = bid
            self.ask = ask

            self.nbids[0]=bid
            self.nasks[0]=ask


            increment =  self.vars['AdjustedSpread'][0].get()

            if increment>self.ask-self.bid:
                increment = self.ask-self.bid

            if ask>=0.51:
                self.rbids[0]=round(ask-increment,2)
            else:
                self.rbids[0]=round(ask-increment,3)

            if bid>=0.51:
                self.rasks[0]=round(bid+increment,2)
            else:
                self.rasks[0]=round(bid+increment,3)


            self.pc = pc
            self.l1_ts =ts


            if self.inv>0:
                self.unreal = round(((self.bid-self.average_price)*self.inv),2)
            else:
                self.unreal = round(((self.average_price-self.ask)*abs(self.inv)),2)


            self.vars['bid'][0].set(self.bid)
            self.vars['ask'][0].set(self.ask)
            self.vars['unrealized'][0].set(self.unreal)

            if self.bid>0 and self.board_setting==False:
                self.check_boardlot()

            self.get_nbbo_depth()

        except Exception as e:
            print(e)
            pass

    def check_boardlot(self):

        board_lot =  self.vars['boardlot'][0].get()
        tick_size =  self.vars['ticksize'][0].get()


        if self.pc>1 and board_lot<=100:
            board_lot =100
        elif self.pc>=0.1 and board_lot<=500:
            board_lot =500
        else:
            board_lot =1000

        if self.bid>=0.5:
            tick_size = 0.01 
        else:
            tick_size = 0.005

        self.vars['boardlot'][0].set(board_lot)
        self.vars['ticksize'][0].set(tick_size)

        self.board_setting= True 

    def get_nbbo_depth(self):


        for i in range(1,5):

            bid = self.nbids[i-1]
            ask = self.nasks[i-1]

            if bid<0.5:
                b_increment = 0.005
                b_round_ = 3
            else:
                b_increment = 0.01 
                b_round_ = 2           

            if ask<0.5:
                a_increment = 0.005
                a_round_ = 3
            else:
                a_increment = 0.01 
                a_round_ = 2     

            self.nbids[i] = round(bid-b_increment,b_round_)

            if ask==0:
                self.nasks[i] = 0
            else:
                self.nasks[i] = round(ask+a_increment,a_round_)

            bid = self.rbids[i-1]
            ask = self.rasks[i-1]

            if bid<0.5:
                b_increment = 0.005
                b_round_ = 3
            else:
                b_increment = 0.01 
                b_round_ = 2           

            if ask<0.5:
                a_increment = 0.005
                a_round_ = 3
            else:
                a_increment = 0.01 
                a_round_ = 2     

            self.rbids[i] = round(bid-b_increment,b_round_)


            if ask==0:
                self.rasks[i] = 0
            else:
                self.rasks[i] = round(ask+a_increment,a_round_)

        #print("NBUY:",self.nbids,'\n',"NSELL:",self.nasks,'\n',"RBUY:",self.rbids,'\n',"RSELL:",self.rasks,"\n")

    def set_variable(self,var,val):
        self.vars[var][0].set(val)

    def get_variable(self,var):

        return self.vars[var][0].get()

    def update_data(self):        

        self.average_price,self.inv = self.manager.get_inventory(self.symbol)

        self.vars['cur_inv'][0].set(self.inv)

        self.set_variable('cur_inv',self.inv)

        self.get_l1()

        self.update_notional()

        #print(self.bid,self.ask)

    def update_notional(self):

        self.notional = int(abs(self.average_price*self.inv))

        self.set_variable('notionalAmount',self.notional)

    ### DATA SECTION 
    def default_for(self, typ):
        return {
            "int": 0,
            "float": 0.0,
            "bool": False,
            "string": "",
        }.get(typ, "")

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
        print("saving:::")
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

    def data_init(self,symbol,folder,override,override_values):

        try:
            if not override:
                self.data = TickerConfig.load(symbol, folder).__dict__
                print(f"[Loaded] {symbol} config from JSON")
            else:
                self.data = {}
        except Exception as e:
            print(f"[Load Fail] Using fallback defaults: {e}")
            self.data = {}

        self.data["Ticker"] = symbol  # Always overwrite with current symbol

        # === Step 2: Merge default & override values ===
        for entry in CONFIG_SCHEMA:
            name = entry["name"]
            typ = entry["type"]
            default_val = entry.get("default", self.default_for(typ))

            # Priority: override > loaded config > default
            if name in override_values:
                self.data[name] = override_values[name]
            elif name not in self.data:
                self.data[name] = default_val

        # === Step 3: Create tkinter Variables ===
        for entry in CONFIG_SCHEMA:
            name = entry["name"]
            typ = entry["type"]
            if typ == "button":
                continue  # Skip buttons

            value = self.data.get(name, self.default_for(typ))

            if typ == "int":
                value = 0 if value in ("", None) else int(value)
                var = tk.IntVar(value=value)
            elif typ == "float":
                value = 0.0 if value in ("", None) else float(value)
                var = tk.DoubleVar(value=value)
            elif typ == "bool":
                value = 0 if value in ("", None, False, "0", "false") else 1
                var = tk.BooleanVar(value=value)
            else:  # string
                value = "" if value is None else str(value)
                var = tk.StringVar(value=value)

            setattr(self, name, var)
            self.vars[name] = (var, typ)


