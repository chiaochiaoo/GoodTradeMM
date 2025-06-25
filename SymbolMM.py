import os
import json
import tkinter as tk
import requests 
from dataclasses import make_dataclass, asdict, field
from Util_functions import *
import time
import tkinter as tk
from tkinter import ttk
import os
from constant import *
from datetime import datetime

import mysql.connector

from logging_module import *



TEST_MODE = False 


ALGO ="Algo Manger"
def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return data


def fetch_data(symbol):

    try:
        print('trying to fetch',symbol)
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

            print("Successful on ",symbol)
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

# AEQN Buy AequitasLIT Limit Broker DAY Reserve
# AEQN Sell->Short AequitasLIT Limit Broker DAY Reserve


BUY = "Buy"
SELL ="Sell->Short"


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
            'save':self.save,
            'delete':self.delete,
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

        self.spread =0
        self.adj_spread =0

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

        self.opening = []
        self.set_up_venue()


        self.buyzone1=0
        self.buyzone2=0
        self.buyzone3=0
        self.sellzone1=0
        self.sellzone2=0
        self.sellzone3=0

        self.cur_trade = 0
        self.cur_tradep = 0
        self.total_trade =0
        self.svi_trade = 0
        self.svi_tradep =0 

        self.board_lot = 100
        self.tick_size = 0.01



        self.inspection_count=0
        self.time_at_bid=0
        self.time_at_ask=0
        self.time_best_bid=0
        self.time_best_ask=0

        self.volume_update_ts = 0


        self.sell_percentage = 0
        self.ask_sell_percentage = 0
        self.buy_percentage = 0
        self.bid_buy_percentage =0

        
        self.reserve_orders = []

        self.today =  datetime.now().strftime("%Y-%m-%d")

        self.vars['Status'][0].trace_add("write", self.update_status)


    # def save(self):
    #     pass 

    def check_today(self):

        today = datetime.now().strftime("%Y-%m-%d")



        now = datetime.now()
        ts = now.hour*60 + now.minute


        if ts>=570 and ts<=960:
            self.inspection_count+=1

        if today!=self.today:
            message(f'New Day detected {today}',NOTIFICATION)
            self.inspection_count=0
            self.time_at_bid=0
            self.time_at_ask=0
            self.time_best_bid=0
            self.time_best_ask=0

        if ts%2==0 and ts!=self.volume_update_ts:

            self.volume_update_ts = ts

            self.manager.insert_volume_status(self.symbol,self.buy_percentage,self.bid_buy_percentage,self.sell_percentage,self.ask_sell_percentage,self.cur_trade)
            message(f'submimit {self.symbol,self.buy_percentage,self.bid_buy_percentage,self.sell_percentage,self.ask_sell_percentage,self.cur_trade} to databse',LOG)

    def delete(self):
        self.manager.ui.delete_ticker(self.symbol)
    def clear_reserve_orders(self):
        self.reserve_orders = []


    def fetch_db_data(self):

        try:
            select = ['RealizedPnLShutdown','FavourableBuyingConditions','MaxInventorySize','MaxAllowedUPnL','BuyZone1','BuyZone2','BuyZone3','SellZone1','SellZone2','SellZone3','AdjustedSpread']
            d = fetch_data(self.symbol)

            for j,i in d.items():
                if j in select:
                    try:
                        self.set_variable(j,i)
                    except:
                        print("problem:",j,i)

            self.update_var_data()
        except:
            PrintException("Fetch data from databse error")

    def update_var_data(self):

        self.buyzone1 =self.get_variable('BuyZone1')
        self.buyzone2 =self.get_variable('BuyZone2')
        self.buyzone3 =self.get_variable('BuyZone3')
        self.sellzone1 =self.get_variable('SellZone1')
        self.sellzone2 =self.get_variable('SellZone2')
        self.sellzone3 =self.get_variable('SellZone3')


    def rejection_received(self):

        self.rejection+=1 

        message(f'{ALGO} {self.symbol} received rejection. current count: {self.rejection}',CRITICAL)

        #message(f'')
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


    def start_restrictive(self):

        self.mode = RESTRICTIVE_MODE 
        self.vars['Status'][0].set(self.mode)


    def start_opening(self):


        o_starttime = self.get_variable('o_starttime')

        now = datetime.now()
        ts = now.hour*60 + now.minute

        if ts>o_starttime and ts<(o_starttime+6):

            self.mode = OPENING_MODE 
            self.vars['Status'][0].set(self.mode)


    def start_aggresive(self):
        self.mode = AGGRESIVE_MODE 
        self.vars['Status'][0].set(self.mode)



        self.init_aggresive_mode()


    def update_status(self,*args):
        message(f'{self.symbol} mode switch:{self.mode}.',NOTIFICATION)

    def start_test(self):
        self.mode = 'TEST' 

        self.vars['Status'][0].set(self.mode)

        # NBBO

        action =BUY
        price = self.nbids[0] 
        order = self.vars['d_Venue'][0].get()
        board_lot =self.vars['boardlot'][0].get()

        self.post_cmd(order,price,board_lot,action)

    def inventory_check(self,vals):
        ###
        inv =self.get_variable('cur_inv')

        result = {}
        total = 0

        #vals = dict(sorted(vals.items()))
        vals = dict(sorted(vals.items(), reverse=True))
        for key, value in vals.items():
            if key < 0:
                if total + value <= inv:
                    result[key] = value
                    total += value
            else:
                result[key] = value

        #print("inv check:",vals,result)
        result2={}

        for key,value in result.items():
            if value!=0:
                result2[key] = value
        return result2


    def update_volume_profile(self):


        # self.cur_trade = 0
        # self.cur_tradep = 0
        # self.total_trade =0
        # self.svi_trade = 0
        # self.svi_tradep =0 

        try:
            resp = requests.get("http://127.0.0.1:8000/traded_volume", params={"symbol": self.symbol})
            self.svi_trade = resp.json()['volume']

            
        except:
            message('svi server cannot reach.',NOTIFICATION)


        if self.total_trade!=0:
            self.svi_tradep = round(self.svi_trade/self.total_trade,2)
            self.cur_tradep = round(self.cur_trade/self.total_trade,2)

        #print(self.symbol,self.cur_trade,self.cur_tradep,self.cur_trade/self.total_trade,self.total_trade)

        #print(self.symbol,self.cur_trade,self.cur_tradep,self.svi_trade,self.svi_tradep,self.total_trade)

        self.set_variable('cur_traded',self.cur_trade)
        self.set_variable('cur_tradedp',self.cur_tradep)
        self.set_variable('svi_traded',self.svi_trade)
        self.set_variable('svi_tradedp',self.svi_tradep)



    def check_restrictive_condition(self):

        try:
            inv = int(self.get_variable('cur_inv'))
            max_inv = int(self.get_variable('MaxInventorySize'))

            u = int(self.get_variable('unrealized'))


            upnl = abs(self.get_variable('MaxAllowedUPnL'))*-1

            shutdown = int(self.get_variable('RealizedPnLShutdown'))

            ### 3 MODES CATEGORY. INACTIVE, RES, ELSE. 

            # r_starttime = self.get_variable('r_starttime')
            # r_stoptime = self.get_variable('r_stoptime')


            d_starttime= self.get_variable('d_starttime')
            d_stoptime = self.get_variable('d_stoptime')

            o_starttime = self.get_variable('o_starttime')

        except:
            message(f"{self.symbol} variables are not correctly set up ",NOTIFICATION)

        now = datetime.now()
        ts = now.hour*60 + now.minute

        if ts>560:

            self.update_volume_profile()


            # if ts==o_starttime:
            #     self.start_opening()


            if self.mode==RESTRICTIVE_MODE:
                #print("cehcking:", u>upnl,inv<int(max_inv*0.8),shutdown)
                if u>upnl and inv<int(max_inv*0.8) and shutdown!=1 and ts>d_starttime and ts<d_stoptime:
                    message(f'{self.symbol} inventory under max limit. switch to DEFAULT_MODE.',NOTIFICATION)
     
                    self.start_default()

                if inv==0 and max_inv ==0:
                    message(f'{self.symbol} no position & no intend inventory. switch to INACTIVE.',NOTIFICATION)
                    self.start_pending()

                if ts<d_starttime or ts>d_stoptime:
                    message(f'{self.symbol} out of RESTRICTIVE_MODE time block. switch to INACTIVE.',NOTIFICATION)
                    self.start_pending()


            if self.mode==DEFAULT_MODE:
                if shutdown!=0:
                    message(f'{self.symbol} realize shutdown activated. switch to RESTRICTIVE_MODE.',NOTIFICATION)
                    self.start_restrictive()

                if self.bid>self.buyzone3 :


                    if  inv>=max_inv:
                        message(f'{self.symbol} inventory reach max. switch to RESTRICTIVE_MODE.',NOTIFICATION)

                        if not shutdown:
                            self.set_variable('r_nbbo',1)
                        self.start_restrictive()

                    if u<=upnl:
                        message(f'{self.symbol} unreal PNL reach limit. switch to RESTRICTIVE_MODE.',NOTIFICATION)

                        if not shutdown:
                            self.set_variable('r_nbbo',1)
                        self.start_restrictive()

                if ts<d_starttime or ts>d_stoptime:
                    message(f'{self.symbol} out of DEFAULT time block. switch to INACTIVE.',NOTIFICATION)
                    self.start_pending()




    def sysmbol_inspection(self):

        self.check_restrictive_condition()
        self.clear_reserve_orders()

        self.check_today()

        try:
            self.update_var_data()
        except :
            pass




        try: 
            if self.mode == RESTRICTIVE_MODE:
                
                self.inspection_restrictive()

            elif self.mode == INACTIVE:

                self.insepection_inactive()

            elif self.mode == DEFAULT_MODE:

                self.inspection_default()

            elif self.mode == OPENING_MODE:

                self.inspection_opening()

            elif self.mode == AGGRESIVE_MODE:

                self.inspection_aggresive()
        except Exception as e:
            PrintException("Inspetion error")


    def init_aggresive_mode(self):

        ##
        mode = self.get_variable('a_type')

        if mode =='Size':
            size = self.get_variable('a_size')
        elif mode=='Percentage':
            size = int(self.get_variable('a_percentage')*self.total_trade*0.01)

        board_lot =self.vars['boardlot'][0].get()
        mult = self.vars['a_mult'][0].get()

        size -= size%(board_lot*mult)

        duration = int(self.get_variable('a_duration'))

        self.target_size = size

        self.set_variable('a_target_size',self.target_size)


        self.aggresive_action = self.get_variable('a_action')


        R,M,B = self.target_size,duration,board_lot*mult

        lst = [0 for i in range(M)]

        h=len(lst)//2

        v= R
        while v!=0: 
            for i in range(h):

                lst[i] +=B
                v-=B

                if v==0:
                    break
                lst[i+h] +=B
                v-=B

                if v==0:
                    break
                #print(i,i+h)


        now = datetime.now()
        ts = now.hour*60 + now.minute
        tss = [ts+i+1 for i in range(M)]

        agg = {}
        for i in range(len(tss)):

            agg[tss[i]] = lst[i]

        self.aggresive_order_book = agg
        self.aggresive_order_placement = []
        message(f'{self.symbol} aggresive order book updated {agg}')


    def inspection_aggresive(self):

        now = datetime.now()
        ts = now.hour*60 + now.minute

        if ts in self.aggresive_order_book:

            if ts not in self.aggresive_order_placement:

                self.aggresive_order_placement.append(ts)


                order = self.vars['a_Venue'][0].get()

                if self.aggresive_action=='Buy':

                    price = self.rasks[0]
                    ACTION = BUY
                elif self.aggresive_action  =='Sell':
                    price = self.rbids[0]
                    ACTION = SELL

                if self.aggresive_order_book[ts]!=0:
                    self.post_cmd(order,price,self.aggresive_order_book[ts],ACTION)

        if ts> list(self.aggresive_order_book.keys())[-1]:
            message(f'{self.symbol} aggresive mode finish')
            self.start_pending()

    def insepection_inactive(self):
        self.cancel_orders()


    def svi_order_check(self,price):

        try:
            resp = requests.post("http://127.0.0.1:8000/order_exists", json={
                "symbol": self.symbol,
                "side": 'B',
                "price": price
            })
            exist = resp.json()['exists']
            if exist:
                return True 
                message(f'{self.symbol} order: {price} {share} {action} order already exist, skipping.',LOG)
        except:
                message(f'{self.symbol} SVI order server unreachable',LOG)
                return False 
        return False 

    def update_order_book(self,vals):

        #print(vals)
        cancel_list = []

        ## for the order already there' and not in order book. 
        for price in self.order_book.keys():
            if price not in vals.keys():
                cancel_list.append(price)

        ## for the order already there' and in svi. 


        for price in self.order_book.keys():
            if price>0 and price>self.buyzone3:
                if self.svi_order_check(price)==True:

                    message(f'{self.symbol} SVI trader present at : {price}',LOG)
                    cancel_list.append(price)

        cancel_list=list(set(cancel_list))


        abs_keys_set = {abs(key) for key in self.order_book.keys()}


        send_list = []
        for price in vals.keys():
            if abs(price) not in abs_keys_set and abs(price) not in send_list:
                send_list.append(price)

        for i in cancel_list:
            self.cancel_order(self.order_book[i])

        #if len(cancel_list)>0:
            

        order = self.vars['d_Venue'][0].get()

        print(self.symbol,vals)
        message(f'{self.symbol} order check, should have : {list(vals.keys())}',LOG)
        message(f'{self.symbol} order check, already posted : {list(self.order_book.keys())}',LOG)
        message(f'{self.symbol} order set : {abs_keys_set}',LOG)
        if len(cancel_list)>0:
            message(f'{self.symbol} order check, canceling {cancel_list}',LOG)
            time.sleep(0.5)
        if len(send_list)>0:
            message(f'{self.symbol} order check, sending: {send_list}',LOG)


        for price in send_list:

            if price in self.reserve_orders and TEST_MODE==False:
                order = self.vars['r_Venue'][0].get()
            else:
                order = self.vars['d_Venue'][0].get()
            if price>0:
                action = BUY 
            else:
                action =SELL

            overlap = False 
            if action == BUY and self.manager.get_svi_order_check()==True:
                overlap  = self.svi_order_check(price)

                if overlap:
                     message(f'{self.symbol} SVI trader present at : {price} skippin',LOG)

            if not overlap:
                self.post_cmd(order, abs(price),vals[price],action)


    def inspection_default(self):
        vals = [self.nbids[0],self.nbids[1],self.nbids[2],self.nasks[0]*-1,self.nasks[1]*-1,self.nasks[2]*-1]
        sellzone1 = self.get_variable('SellZone1')

        #print("Default Check:",self.spread>=self.adj_spread,self.bid <= sellzone1)
        if self.spread>=self.adj_spread and self.ask < sellzone1:
            vals = [self.rbids[0],self.rbids[1],self.rbids[2],self.nasks[0]*-1,self.nasks[1]*-1,self.nasks[2]*-1]

        elif self.spread>=self.adj_spread and self.ask >= sellzone1:
            vals = [self.nbids[0],self.nbids[1],self.nbids[2],self.rasks[0]*-1,self.rasks[1]*-1,self.rasks[2]*-1]



        global_bid_mult = self.get_variable('bidmult')
        global_ask_mult =  self.get_variable('askmult')


        
        reserve_bidmult = self.get_variable('reserve_bidmult')
        reserve_askmult =  self.get_variable('reserve_askmult')



        board_lot =self.vars['boardlot'][0].get()

        orders = {}

        for val in vals:
            if val>0:
                if val<=self.buyzone3:
                    orders[val] = board_lot*reserve_bidmult
                    message(f'{self.symbol} buy zone 3 orders: {val} and size {board_lot*reserve_bidmult}',LOG)

                    self.reserve_orders.append(val)
                else:
                    orders[val] = board_lot*global_bid_mult
            else:


                if abs(val)>=self.sellzone1:
                    orders[val] = board_lot*reserve_askmult
                    message(f'{self.symbol} sell zone 1 orders: {val} and size {board_lot*reserve_askmult}',LOG)
                    self.reserve_orders.append(val)
                else:
                    orders[val] = board_lot*global_ask_mult
        orders = self.inventory_check(orders)



        self.bid_ask_time_check(orders)
        self.update_order_book(orders)


    def bid_ask_time_check(self,orders):

        on_bid = any(price <= self.bid for price in orders)
        on_ask = any(abs(price) >= self.ask for price in orders)
        has_bid = any(price > 0 for price in orders)
        has_ask = any(price < 0 for price in orders)

        if on_bid:
            self.time_best_bid+=1
        if on_ask:
            self.time_best_ask+=1
        if has_bid:
            self.time_at_bid+=1
        if has_ask:
            self.time_at_ask+=1


        self.sell_percentage = round(self.time_at_ask*100/self.inspection_count,2)
        self.ask_sell_percentage = round(self.time_best_ask*100/self.inspection_count,2)
        self.buy_percentage = round(self.time_at_bid*100/self.inspection_count,2)
        self.bid_buy_percentage =round(self.time_best_bid*100/self.inspection_count,2)

        message(f'{self.symbol} current BuyP {self.buy_percentage} BidP {self.bid_buy_percentage} SellP {self.ask_sell_percentage} AskP {self.sell_percentage}',LOG)

    def inspection_opening(self):

        today = datetime.now().strftime("%Y-%m-%d")

        if today not in self.opening:
            self.opening.append(today)
            if self.pc==0:
                message(f'{ALGO} {self.symbol} have no previous closing price. skip opening phase',NOTIFICATION)
            else:

                order = self.vars['o_Venue'][0].get()
                board_lot =  self.vars['boardlot'][0].get()
                tick_size =  self.vars['ticksize'][0].get()

                inv =self.get_variable('cur_inv')
                max_inv = self.get_variable('MaxInventorySize')

                u = self.get_variable('unrealized')
                upnl = abs(self.get_variable('MaxAllowedUPnL'))*-1

                shutdown = self.get_variable('RealizedPnLShutdown')

                o_bid_mult = self.get_variable('o_bidmult')
                o_ask_mult =  self.get_variable('o_askmult')


                if shutdown:
                    send_list = []

                    message(f' {self.symbol} shutdown. no opening orders {send_list}',NOTIFICATION)
                else:
                    if inv>=max_inv or u<=upnl:
                        send_list  = [(self.pc+tick_size)*-1]

                        
                        message(f' {self.symbol} opening mode max inventory reached: {inv>=max_inv} unreal shutdown {u<=upnl}/ real shutdown:{shutdown}. sell only {send_list}',NOTIFICATION)
                    else:


                        if inv<int(o_ask_mult*board_lot):
                            send_list =  [self.pc-tick_size]
                            message(f' {self.symbol} insufficient inventory. opening mode bid only. {send_list}',NOTIFICATION)
                        else:
                            send_list  = [(self.pc+tick_size)*-1,self.pc-tick_size]
                            message(f' {self.symbol} opening mode normal. {send_list}',NOTIFICATION)



                send_list2= []
                for i in send_list:

                    if abs(i)>=0.50:
                        send_list2.append(round(i,2))
                    else:
                        send_list2.append(round(i,3))

                for price in send_list2:

                    if price>0:
                        action = BUY 
                    else:
                        action =SELL


                    if action==BUY:

                        self.post_cmd(order, abs(price),int(board_lot*o_bid_mult),action)
                    else:
                        self.post_cmd(order, abs(price),int(board_lot*o_ask_mult),action)



    def inspection_restrictive(self):

        ## get should.


        shutdown = self.get_variable('RealizedPnLShutdown')

        if shutdown:

            vals = [self.nbids[1],self.nbids[2],self.nasks[0]*-1,self.nasks[1]*-1]

        else:

            vals = [self.nbids[1],self.nbids[2],self.rasks[0]*-1,self.rasks[1]*-1,self.rasks[2]*-1]



        a1enable = self.get_variable('r_nbbo')

        if a1enable:
            vals.append(self.nasks[0]*-1)
        else:
            if self.nasks[0]*-1 in vals:
                vals.remove(self.nasks[0]*-1)



        res_bid_mult = self.get_variable('r_bidmult')
        res_ask_mult =  self.get_variable('r_askmult')

        board_lot =self.vars['boardlot'][0].get()

        orders = {}

        for val in vals:
            if val>0:
                orders[val] = board_lot*res_bid_mult
            else:
                orders[val] = board_lot*res_ask_mult


        orders = self.inventory_check(orders)
        self.bid_ask_time_check(orders)
        self.update_order_book(orders)

    def cancel_orders(self):
        cancel_list = []

        for price in self.order_book.keys():
            cancel_list.append(price)

        for i in cancel_list:

            message(f'{self.symbol} cancel order: {i}',LOG)

            self.cancel_order(self.order_book[i])


    def cancel_order(self,ordername):

        req = f'http://127.0.0.1:8080/CancelOrder?type=ordernumber&ordernumber={ordername}'
        
        r = requests.post(req)


    def post_cmd(self,order,price,share,action):




        # symbol,                # e.g., "ACHR.NY"
        # side,                  # e.g., "B" or "S"
        # order_number,          # for tracking, stored in PapiID
        # price,                 # float
        # shares,                # int, optional (can be None)
        # depth_level=0,         # default value if unknown

        if action==BUY:
            self.manager.insert_order(self.symbol,'B',0,price,share)
        else:
            self.manager.insert_order(self.symbol,'S',0,price,share)

        order = order.replace("ACTION",action)

        if TEST_MODE:
            order = order.replace("Broker ","")

        req = f'http://127.0.0.1:8080/ExecuteOrder?symbol={str(self.symbol)}&limitprice={str(price)}&ordername={order}&shares={str(share)}'
        

        if 'Reserve' in order:
            req = req +'&displaysize='+str(int(self.board_lot))
            message(f'{self.symbol} order: {price} {share} {action} with {order}   cmd {req}',LOG)
        else:
            message(f'{self.symbol} order: {price} {share} {action} with {order}',LOG)

        r = requests.post(req)


    def update_orderbook(self,new_order):
        #refresh.
        self.order_book = new_order

        self.open_order_number = len(self.order_book)
        self.set_variable('openOrderCount',self.open_order_number)


    def add_trade_volume(self,shares):


        ### check if today

        now = datetime.now().strftime("%Y-%m-%d")

        if now !=self.today:
            self.today = now 
            self.cur_trade = 0

        self.cur_trade+=shares



    def get_l1(self):

        try:
            postbody = "http://127.0.0.1:8080/GetLv1?symbol=" + self.symbol 

            r= requests.get(postbody)

            stream_data = r.text

            bid = float(find_between(stream_data, "BidPrice=\"", "\""))
            ask = float(find_between(stream_data, "AskPrice=\"", "\""))
            pc = float(find_between(stream_data, "ClosePrice=\"", "\""))
            ts = find_between(stream_data, "MarketTime=\"", "\"")
            volume = int(find_between(stream_data, "Volume=\"", "\""))

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

            self.total_trade = volume

            self.spread = self.ask-self.bid

            self.nbids[0]=bid
            self.nasks[0]=ask


            self.adj_spread =  self.vars['AdjustedSpread'][0].get()

            if self.adj_spread>=self.ask-self.bid:
                self.adj_spread = self.ask-self.bid

            if self.adj_spread<0.005:
                self.adj_spread=0.005

            if ask>=0.51:
                self.rbids[0]=round(ask-self.adj_spread,2)
            else:
                self.rbids[0]=round(ask-self.adj_spread,3)

            if bid>=0.51:
                self.rasks[0]=round(bid+self.adj_spread,2)
            else:
                self.rasks[0]=round(bid+self.adj_spread,3)


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
            #print(e)

            postbody = f"http://127.0.0.1:8080/Register?symbol={self.symbol}&feedtype=L1" 
            r= requests.get(postbody)

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

        self.board_lot = board_lot
        self.tick_size = tick_size

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
        #print("saving:::")
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
                #print(f"[Loaded] {symbol} config from JSON")
            else:
                self.data = {}
        except Exception as e:
            #print(f"[Load Fail] Using fallback defaults: {e}")
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


import tkinter as tk

class MyUI:
    def __init__(self, root):
        self.root = root
        self.notification_pannel = tk.Frame(root)
        self.notification_pannel.pack()

        # Text widget inside the notification panel
        self.notification_text = tk.Text(self.notification_pannel, height=10, width=50, state='disabled')
        self.notification_text.pack()

    def show_notification(self, message: str, max_lines=500):
        self.notification_text.config(state='normal')
        self.notification_text.insert(tk.END, message + '\n')
        self.notification_text.see(tk.END)

        # Trim to keep only the last 500 lines
        lines = self.notification_text.get("1.0", tk.END).splitlines()
        if len(lines) > max_lines:
            self.notification_text.delete("1.0", f"{len(lines) - max_lines + 1}.0")

        self.notification_text.config(state='disabled')

# Example usage
# if __name__ == "__main__":
#     root = tk.Tk()
#     ui = MyUI(root)

#     # Simulate external function call
#     ui.show_notification("App started.")

#     for i in range(600):
#         ui.show_notification(f'Waiting for user input...{i}')

#     root.mainloop()


