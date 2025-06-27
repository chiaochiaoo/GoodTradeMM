from google.cloud import storage
import os
import mplfinance as mpf
import pandas as pd
import numpy as np
import datetime, pytz
import json
import requests 
import mysql.connector
import csv
import matplotlib.pyplot as plt
import json
import warnings

warnings.filterwarnings("ignore")

pd.options.mode.chained_assignment = None  # default='warn'

def upload_file_to_gcs(source_file_name, destination_blob_name):

    storage_client = storage.Client.from_service_account_json('key.json') #((attached json file path here)) 

    bucket = storage_client.bucket('stdb1')

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def update_data2(symbols):
    MYSQL_USER = "webuser"
    MYSQL_PASSWORD = "Domination77$$"
    MYSQL_DATABASE = "summitdata"
    PORT = 3306

    total = []
    try:
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

            for symbol in symbols:
                # Generate the SQL query
                query = f"SELECT * FROM stockdata WHERE SymbolGroup = '{symbol} Group'"
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if rows:
                    column_names = [i[0] for i in cursor.description]
                    csv_file_name = f"chart_data/{symbol}.csv"

                    # Ensure the directory exists
                    os.makedirs(os.path.dirname(csv_file_name), exist_ok=True)

                    # Write the results to a CSV file
                    with open(csv_file_name, mode='w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(column_names)
                        writer.writerows(rows)

                    # Read the CSV into a DataFrame and convert to JSON
                    df = pd.read_csv(csv_file_name)
                    json_file_name = f"mm/{symbol}-sd.json"

                    # Ensure the directory exists
                    os.makedirs(os.path.dirname(json_file_name), exist_ok=True)
                    df.to_json(json_file_name, orient='records', lines=True)

                    total.append(pd.read_csv(csv_file_name))
                else:
                    print(f"No data found for symbol: {symbol}")


            ############# SGDJ #############
            query = f"SELECT * FROM stockdata WHERE SymbolGroup = 'Index Group'"
            cursor.execute(query)
            rows = cursor.fetchall()

            symbol = "SGDJ"
            if rows:
                column_names = [i[0] for i in cursor.description]
                csv_file_name = f"chart_data/{symbol}.csv"

                # Ensure the directory exists
                os.makedirs(os.path.dirname(csv_file_name), exist_ok=True)

                # Write the results to a CSV file
                with open(csv_file_name, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(column_names)
                    writer.writerows(rows)

                # Read the CSV into a DataFrame and convert to JSON
                df = pd.read_csv(csv_file_name)
                json_file_name = f"mm/{symbol}-sd.json"

                # Ensure the directory exists
                os.makedirs(os.path.dirname(json_file_name), exist_ok=True)
                df.to_json(json_file_name, orient='records', lines=True)

                total.append(pd.read_csv(csv_file_name))


            ##################################

            cursor.close()
            connection.close()

            df = pd.concat(total)
            df.to_csv("chart_df.csv")
        else:
            print("Failed to connect to MySQL database")

    except mysql.connector.Error as e:
        print("Error connecting to MySQL:", e)

def update_data(symbols):
    MYSQL_USER = "webuser"
    MYSQL_PASSWORD = "Domination77$$"
    MYSQL_DATABASE = "summitdata"
    PORT = 3306

    total = []
    buy = []
    sell = []
    try:
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
            mmdata_symbols = ['ELEM.CN', 'LEXT.CN', 'ESPN.VN', 'BATX.CN', 'CRTL.CN', 'ANT.CN']

            for symbol in symbols:
                
                # Query for timeandsalesdata
                query = f"SELECT * FROM timeandsalesdata WHERE Symbol = '{symbol}' AND MarketDate >= CURDATE() - INTERVAL (WEEKDAY(CURDATE()) + 7) DAY AND MarketDate < CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY AND WEEKDAY(MarketDate) < 5 ORDER BY MarketDate DESC;"
                # query = f"SELECT * FROM timeandsalesdata WHERE Symbol = '{symbol}' AND MarketDate BETWEEN '2024-11-25' AND '2024-11-29'  ORDER BY MarketDate DESC;"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                column_names = [i[0] for i in cursor.description]
                csv_file_name = "temp_csv/" + symbol + ".csv"

                # Write the results to a CSV file
                with open(csv_file_name, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(column_names)
                    writer.writerows(rows)

                total.append(df_process(symbol, csv_file_name))

                buy.append(buy_volume(symbol,csv_file_name))
                sell.append(sell_volume(symbol,csv_file_name))
               

                # Only run the mmdata query for specified symbols
                query = f"SELECT * FROM mmdata WHERE Symbol = '{symbol}' AND MarketDate >= CURDATE() - INTERVAL (WEEKDAY(CURDATE()) + 7) DAY AND MarketDate < CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY AND WEEKDAY(MarketDate) < 5 ORDER BY MarketDate DESC;"
                # query = f"SELECT * FROM mmdata WHERE Symbol = '{symbol}' AND MarketDate  BETWEEN '2024-11-25' AND '2024-11-29'  ORDER BY MarketDate DESC;"
                cursor.execute(query)
                rows = cursor.fetchall()
                column_names = [i[0] for i in cursor.description]
                csv_file_name = "temp_csv/" + symbol + "mm.csv"

                # Write the results to a CSV file
                with open(csv_file_name, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(column_names)
                    writer.writerows(rows)

                df = pd.read_csv(csv_file_name)
                df.to_json("mm/" + symbol + ".json", orient='records', lines=True)

                print(symbol)

            cursor.close()
            connection.close()

        df = pd.concat(total)
        df.to_csv("df.csv")

        b = pd.concat(buy)
        b.to_csv("buy.csv")

        s = pd.concat(sell)
        print(s)
        s.to_csv("sell.csv")
    except Exception as e:
        print("Error connecting to MySQL:", e)




def eod_chart(symbol):

    data = {}
    url = "https://financialmodelingprep.com/api/v3/historical-price-full/"+symbol+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"
    r = requests.get(url)
    d = r.json()
    data[symbol] = d['historical'][:10]

    df = pd.DataFrame.from_dict(data[symbol])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    file = symbol.split(".")[0]
    mpf.plot(df, type='candle', style='yahoo', title=symbol+' Price', volume=True,savefig=file+"_EOD.png",panel_ratios=(6, 2),panel_spacing=0.5,tight_layout=True)#,# savefig='stock_price.png'

def intraday_chart(symbol):

    days = 6
    total = []
    for i in range(days//2):

        start = datetime.datetime.today() - datetime.timedelta(days=3*i)
        end = start - datetime.timedelta(days=2)
        #print(start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d'))

        start = start.strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')

        # if len(total)%20==0:
        #   print(end,start,len(total))
        postbody = "https://financialmodelingprep.com/api/v3/historical-chart/1min/"+symbol+"?from="+end+"&to="+start+"&apikey=a901e6d3dd9c97c657d40a2701374d2a"

        r= requests.get(postbody)

        d = json.loads(r.text)
        d = pd.DataFrame.from_dict(d)
        total.append(d)

    ndf = pd.concat(total)
    ndf['date'] = pd.to_datetime(ndf['date'])
    ndf['day'] = ndf['date'].dt.strftime('%Y-%m-%d')
    ndf['time'] = ndf['date'].dt.strftime('%H:%M')
    ndf = ndf.sort_values(by=['date']).reset_index(drop=True)
    ndf = ndf.loc[ndf['day'].isin(ndf['day'].unique()[-5:])]
    ndf.set_index('date', inplace=True)

    file = symbol.split(".")[0]
    mpf.plot(ndf, type='candle', style='charles', title=symbol+' Intraday Chart', volume=True,savefig=file+"_INTRA.png",tight_layout=True)#  savefig='stock_price.png'


def df_process(symbol,csv_file_name):
    df = pd.read_csv(csv_file_name)
    #print(df['MarketTime'])
    df['MarketTime'] = pd.to_datetime(df['MarketTime'])
    df['ts'] = df['MarketDate']+" "+df['MarketTime'].dt.strftime('%H:%M:%S.%f')

    ndf = pd.DataFrame(df.groupby('ts')['Size'].sum())
    ndf['open'] = df.groupby('ts')['Price'].first()
    ndf['high'] = df.groupby('ts')['Price'].max()
    ndf['low'] = df.groupby('ts')['Price'].min()
    ndf['close'] = df.groupby('ts')['Price'].last()
    ndf.sort_index(inplace=True)
    ndf['day'] = pd.to_datetime(ndf.index) 
    ndf['day'] = ndf['day'].dt.strftime('%Y-%m-%d')
    ndf['day'] = ndf.index
    ndf['day'] = pd.to_datetime(ndf['day'])
    ndf.set_index('day', inplace=True)
    ndf['volume'] = ndf['Size']
    ndf['symbol'] = symbol

    return ndf

def buy_volume(symbol,csv_file_name):
    df = pd.read_csv(csv_file_name)
    df['MarketTime'] = pd.to_datetime(df['MarketTime'])
    df['ts'] = df['MarketDate']+" "+df['MarketTime'].dt.strftime('%H:%M')

    df = df.loc[df['Tick']=="U"]
    ndf = pd.DataFrame(df.groupby('ts')['Size'].sum())
    ndf['symbol'] = symbol
    return ndf 

def sell_volume(symbol,csv_file_name):
    df = pd.read_csv(csv_file_name)
    df['MarketTime'] = pd.to_datetime(df['MarketTime'])
    df['ts'] = df['MarketDate']+" "+df['MarketTime'].dt.strftime('%H:%M')

    df = df.loc[df['Tick']=="D"]
    ndf = pd.DataFrame(df.groupby('ts')['Size'].sum())
    ndf['symbol'] = symbol
    return ndf 


def upload_charts(comparisons):
    for k,i in comparisons.items():
        for j in i:
            folder = k.split(".")[0]
            file_ = j.split(".")[0]
            source_file_name_image = "mm/"+j+'.json'
            destination_blob_name_image = 'mmdata/'+folder+'/'+file_+'.json'
            upload_file_to_gcs(source_file_name_image, destination_blob_name_image)     


    source_file_name_image = "close.json"
    destination_blob_name_image = 'mmdata/close.json'
    upload_file_to_gcs(source_file_name_image, destination_blob_name_image)

    for file in comparisons.keys():
      try:
          file_ = file.split(".")[0]

          source_file_name_image = "EOD/"+file+'.png'
          destination_blob_name_image = 'images/'+file_+'/EOD.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "INTRA/"+file+'.png'
          destination_blob_name_image = 'images/'+file_+'/INTRA.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE/"+file+'.png'
          destination_blob_name_image = 'images/'+file_+'/COMPARE.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)


          ########################################################################
      except Exception as e:
          print(e)
      try:

          source_file_name_image = "COMPARE2/"+file+'.png'
          destination_blob_name_image = 'images/'+file_+'/COMPARE2.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:

          source_file_name_image = "COMPARE2/"+file+'_volume.png'  
          destination_blob_name_image = 'images/'+file_+'/volume.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:

          source_file_name_image = "COMPARE2/"+file+'_buyvolume.png'  
          destination_blob_name_image = 'images/'+file_+'/buyvolume.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_sellvolume.png'  
          destination_blob_name_image = 'images/'+file_+'/sellvolume.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
          #######################################################################
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_AverageDailyPriceCloseTenDayVsTwoHundredDay.png'
          destination_blob_name_image = 'images/'+file_+'/AverageDailyPriceCloseTenDayVsTwoHundredDay.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_FiveDayPriceChange.png'
          destination_blob_name_image = 'images/'+file_+'/FiveDayPriceChange.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_RSIThreeDayVsThirtyDay.png'
          destination_blob_name_image = 'images/'+file_+'/RSIThreeDayVsThirtyDay.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_FiveDayVsNinetyDayAverageVolumeChange.png'
          destination_blob_name_image = 'images/'+file_+'/FiveDayVsNinetyDayAverageVolumeChange.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_FiveDayVsThirtyDayAverageVolume.png'
          destination_blob_name_image = 'images/'+file_+'/FiveDayVsThirtyDayAverageVolume.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_ThirtyDayPriceChange.png'
          destination_blob_name_image = 'images/'+file_+'/ThirtyDayPriceChange.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_WeeklyNotionalTradedAmount.png'
          destination_blob_name_image = 'images/'+file_+'/WeeklyNotionalTradedAmount.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_TotalBuyVolumeByBroker.png'
          destination_blob_name_image = 'images/'+file_+'/TotalBuyVolumeByBroker.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_TotalSellVolumeByBroker.png'
          destination_blob_name_image = 'images/'+file_+'/TotalSellVolumeByBroker.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:

          source_file_name_image = "COMPARE2/"+file+'_Totalvolume.png'
          destination_blob_name_image = 'images/'+file_+'/Totalvolume.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)



          ############################## NEW CHARTS #############################
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_BuyVolumeProfile.png'
          destination_blob_name_image = 'images/'+file_+'/BuyVolumeProfile.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_BuyVolumeProfileCount.png'
          destination_blob_name_image = 'images/'+file_+'/BuyVolumeProfileCount.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_SellVolumeProfile.png'
          destination_blob_name_image = 'images/'+file_+'/SellVolumeProfile.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_SellVolumeProfileCount.png'
          destination_blob_name_image = 'images/'+file_+'/SellVolumeProfileCount.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_Total_Volume_By_Date.png'
          destination_blob_name_image = 'images/'+file_+'/Total_Volume_By_Date.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'_Total_volume_by_price.png'
          destination_blob_name_image = 'images/'+file_+'/Total_volume_by_price.jpg'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)


          #######################################################################
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "COMPARE2/"+file+'.json'
          destination_blob_name_image = 'images/'+file_+'/COMPARE2.json'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
      try:
          source_file_name_image = "mm/"+file+'-sd.json'
          destination_blob_name_image = 'mmdata/'+file_+'/mm.json'
          upload_file_to_gcs(source_file_name_image, destination_blob_name_image)
      except Exception as e:
          print(e)
    #   try:
    #     #   source_file_name_image = "mm/"+file+'.json'
    #     #   destination_blob_name_image = 'mmdata/'+file_+'/mm.json'
    #     #   upload_file_to_gcs(source_file_name_image, destination_blob_name_image)

    #   except Exception as e:
    #       print(e)




import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import ast
if __name__ == "__main__":


    comparisons = {}
    
    comparisons["ELEM.CN"] = ["ELEM.CN","AGX.VN","TK.VN","KUYA.CN","SGDJ"]
    comparisons["BATX.CN"] = ["BATX.CN","VOLT.CN","NILI.VN","ERKA.CN","BY.CN","SGDJ"]
    comparisons["LEXT.CN"] = ["LEXT.CN","PEX.VN","UCU.VN","AXM.VN","SGDJ"]
    comparisons["ESPN.VN"] = ["ESPN.VN","EMO.VN","DMET.CC","PGZ.VN","SGDJ"]
    comparisons["CRTL.CN"] = ["CRTL.CN","GXP.CN","NF.CN","NSU.VN","SGDJ"]
    comparisons["ANT.CN"] = ["ANT.CN","GSS.VN","GAND.CN","GLDS.CN","SGDJ"]
    comparisons["BLGV.CN"] = ["BLGV.CN","BRC.VN","NXS.VN","SGDJ"]


    total = []
    for i in comparisons.values():
      for j in i:
        total.append(j)

    total = list(set(total))
    

    update_data(total)
    update_data2(list(comparisons.keys()))

    #### MM DATA ###

    for symbol in comparisons.keys():
        sd = pd.read_csv("temp_csv/" + symbol + "mm.csv").fillna(0)


        # BUY
        buy = {}
        for i,j in sd['BuyerVolumeByID'].items():
            try:
                day = ast.literal_eval(j)
                for s,item in day['BuyerVolumes'].items():

                    if s not in buy:
                        buy[s] = item
                    else:
                        buy[s] += item 
            except Exception as e:
                #print(e) 
                pass

        buy = dict(sorted(buy.items(), key=lambda item: item[1], reverse=True))

        plt.title('Total Buy Volume by Broker,'+symbol)
        plt.xlabel('Date')
        plt.ylabel('Volume')

        colors = plt.cm.viridis(np.linspace(0, 1, len(list(buy.keys()))))
        plt.figure(figsize=(10, 6))
        plt.bar(list(buy.keys()), list(buy.values()), color=colors)

        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        #plt.show()
        plt.tight_layout()
        
        plt.savefig("COMPARE2/"+symbol+'_TotalBuyVolumeByBroker.png')

        # SELL
        sell = {}
        for i,j in sd['SellerVolumeByID'].items():
            try:
                day = ast.literal_eval(j)
                for s,item in day['SellerVolumes'].items():

                    if s not in sell:
                        sell[s] = item
                    else:
                        sell[s] += item 
            except Exception as e:
                pass

        sell = dict(sorted(sell.items(), key=lambda item: item[1], reverse=True))

        plt.title('Total Sell Volume by Broker')
        plt.xlabel('Date')
        plt.ylabel('Volume')

        categories = sell.keys()
        values = sell.values()

        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

        # Create the bar plot
        plt.figure(figsize=(10, 6))
        plt.bar(categories, values, color=colors)

        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        #plt.show()
        plt.tight_layout()
        
        plt.savefig("COMPARE2/"+symbol+'_TotalSellVolumeByBroker.png')


    # ##################################################################
        volume = {}
        count = {}
        for i,j in sd['BuyVolumeProfile'].items():
            try:
                day = ast.literal_eval(j)
                for s,item in day['VolumeAtPrice'].items():
                    if s not in volume:
                        volume[s] = item['Volume']
                        count[s] = item['OrderCount']
                    else:
                        volume[s] += item['Volume']
                        count[s] += item['OrderCount']
            except Exception as e:
                pass

        #print(count)
        volume = dict(sorted(volume.items(), key=lambda item: item[0], reverse=False))
        count = dict(sorted(count.items(), key=lambda item: item[0], reverse=False))

        plt.figure(figsize=(10, 6))
        plt.title('Total Buy Volume')
        plt.xlabel('Price')
        plt.ylabel('Volume')

        categories = volume.keys()
        values = volume.values()

        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

        # Create the bar plot
        
        plt.bar(categories, values, color=colors)

        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        #plt.show()
        plt.tight_layout()
        
        plt.savefig("COMPARE2/"+symbol+'_BuyVolumeProfile.png') 


        plt.figure(figsize=(10, 6))
        plt.title('Total Buy Count')
        plt.xlabel('Price')
        plt.ylabel('Trades Executed')

        categories = count.keys()
        values = count.values()

        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

        # Create the bar plot
        
        plt.bar(categories, values, color=colors)

        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        #plt.show()
        plt.tight_layout()
        
        plt.savefig("COMPARE2/"+symbol+'_BuyVolumeProfileCount.png') 


    #########################################################
        sell = {}
        count = {}
        for i,j in sd['SellVolumeProfile'].items():
            try:
                day = ast.literal_eval(j)
                for s,item in day['VolumeAtPrice'].items():
                    if s not in sell:
                        count[s] = item['OrderCount']
                        sell[s] = item['Volume']
                    else:
                        sell[s] += item['Volume']
                        count[s]+= item['OrderCount']
            except Exception as e:
                pass

        sell = dict(sorted(sell.items(), key=lambda item: item[0], reverse=False))
        count = dict(sorted(count.items(), key=lambda item: item[0], reverse=False))
        

        plt.figure(figsize=(10, 6))
        plt.title('Total Sell Volume')
        plt.xlabel('Price')
        plt.ylabel('Volume')

        categories = sell.keys()
        values = sell.values()

        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

        # Create the bar plot
        
        plt.bar(categories, values, color=colors)

        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        #plt.show()
        plt.tight_layout()
        
        plt.savefig("COMPARE2/"+symbol+'_SellVolumeProfile.png') 


        plt.figure(figsize=(10, 6))
        plt.title('Total Sell Count')
        plt.xlabel('Price')
        plt.ylabel('Trades Executed')

        categories = count.keys()
        values = count.values()

        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

        # Create the bar plot
        
        plt.bar(categories, values, color=colors)

        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        #plt.show()
        plt.tight_layout()
        
        plt.savefig("COMPARE2/"+symbol+'_SellVolumeProfileCount.png') 

        ### Total Volume By Price #####################################################################################
        total_volume_by_price = {}
        for i,item in sd['volumeprofile'].items():
            item  = ast.literal_eval(item)['VolumeAtPrice']

            for p,v in item.items():
                if p not in total_volume_by_price:
                    total_volume_by_price[p] = v 
                else:
                    total_volume_by_price[p] += v
        #print(total_volume_by_price)


        total_volume_by_price = dict(sorted(total_volume_by_price.items(), key=lambda item: item[0], reverse=False))



        categories = list(total_volume_by_price.keys())
        values = total_volume_by_price.values()

        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

        # Create the bar plot
        plt.figure(figsize=(10, 6))

        plt.title('Total Volume by Price')
        plt.ylabel('Price')
        plt.xlabel('Volume')
        plt.barh(categories, values)# #, color=colors

        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        #plt.show()
        #plt.tight_layout()
        
        plt.savefig("COMPARE2/"+symbol+'_Total_Volume_By_Price.png')

        ### Total Volume Volume by date

        #print(sd[['MarketDate','TradedSharesByAll']])
        #print(total_volume_by_price)
 
        categories = sd['MarketDate'].values
        values = sd['TradedSharesByAll'].values

        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

        # Create the bar plot
        plt.figure(figsize=(10, 6))
        plt.barh(categories, values)#

        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        #plt.show()
        #plt.tight_layout()
        plt.title('Total Volume by Date')
        plt.ylabel('Date')
        plt.xlabel('Total Volume')

        plt.savefig("COMPARE2/"+symbol+'_Total_Volume_By_Date.png')

    #intraday

    df = pd.read_csv("df.csv").fillna(0)

    for key in comparisons.keys():
        try:
            print(key, 'eod')
            select = df.loc[df['symbol']==key]
            select['day'] = pd.to_datetime(select['day'])
            select=select.set_index('day')
            mpf.plot(select, type='candle', style='yahoo', title=key[:-3]+' Intraday Chart', volume=True,savefig="INTRA/"+key+".png")#"INTRA/"+#,tight_layout=True
        except Exception as e:
            print(e,"??")

    df['day'] = pd.to_datetime(df['day'])
    df['hour']=df['day'].dt.strftime('%m-%d %H')
    df['day'] = df['day'].dt.strftime('%Y-%m-%d') 
    ddf =pd.DataFrame(df.groupby(['day','symbol'])['Size'].sum())
    ddf['open'] = df.groupby(['day','symbol'])['open'].first()
    ddf['high'] = df.groupby(['day','symbol'])['high'].max()
    ddf['low'] = df.groupby(['day','symbol'])['low'].min()
    ddf['close'] = df.groupby(['day','symbol'])['close'].last()
    ddf.sort_index(inplace=True)
    ddf['volume'] = ddf['Size']
    ddf.reset_index(inplace=True)

    ddf.groupby('symbol')['close'].last().to_json('close.json')

    for key in comparisons.keys():
        try:
            select = ddf.loc[ddf['symbol']==key]
            select['day'] = pd.to_datetime(select['day'])
            select.set_index('day', inplace=True)
            mpf.plot(select, type='candle', style='yahoo', title=key[:-3]+' EOD Chart', volume=True,savefig="EOD/"+key+".png")#,panel_ratios=(6, 2),panel_spacing=0.5,tight_layout=True
        except Exception as e:
            print(e)

    buy = pd.read_csv("buy.csv")
    sell = pd.read_csv("sell.csv")

    buy['day'] = pd.to_datetime(buy['ts'])
    buy['hour']=buy['day'].dt.strftime('%m-%d %H')

    sell['day'] = pd.to_datetime(sell['ts'])
    sell['hour']=sell['day'].dt.strftime('%m-%d %H')

    for key in comparisons.keys():

        x = df.loc[df['symbol']==key].groupby('hour')['volume'].sum()
        plt.figure(figsize=(10, 6))
        plt.plot(pd.to_datetime(x.index,format='%m-%d %H').strftime('%m-%d %I%p'), x.values)
        
        #plt.tight_layout()
        
        plt.title('Volume by '+key+' over Time')
        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        #plt.show()
        plt.tight_layout()
        
        plt.savefig("COMPARE2/"+key+'_volume.png')


    
        x = buy.loc[buy['symbol']==key].groupby('hour')['Size'].sum()
        plt.figure(figsize=(10, 6))
        plt.plot(pd.to_datetime(x.index,format='%m-%d %H').strftime('%m-%d %I%p'), x.values)

        #plt.tight_layout()
        
        plt.title('Buy Volume by '+key[:-3]+' over Time')
        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.xticks(rotation=-30)
        plt.xticks(fontsize=8) 

        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=40))


        #plt.show()
        plt.tight_layout()
        
        plt.savefig("COMPARE2/"+key+'_buyvolume.png')


        x = sell.loc[sell['symbol']==key].groupby('hour')['Size'].sum()
        plt.figure(figsize=(10, 6))
        plt.plot(pd.to_datetime(x.index,format='%m-%d %H').strftime('%m-%d %I%p'), x.values)
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=40))

        plt.tight_layout()
        
        plt.title('Sell Volume by '+key[:-3]+' over Time')
        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.xticks(rotation=-30)
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=40))

        #plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=20))

        #plt.show()
        plt.tight_layout()
        
        plt.savefig("COMPARE2/"+key+'_sellvolume.png')

        ###

        
        plt.figure(figsize=(10, 6))

        # Prepare common date range (remove time, get unique dates from both buy/sell)
        sell['hour'] = pd.to_datetime(sell['hour'], format='%m-%d %H')
        buy['hour'] = pd.to_datetime(buy['hour'], format='%m-%d %H')
        all_dates = pd.date_range(
            start=min(buy['hour'].min(), sell['hour'].min()).date(),
            end=max(buy['hour'].max(), sell['hour'].max()).date(),
            freq='D'
        )

        # Group sell by date
        sell_grouped = sell.loc[sell['symbol'] == key].copy()
        sell_grouped['date'] = pd.to_datetime(sell_grouped['hour']).dt.date
        sell_vol = sell_grouped.groupby('date')['Size'].sum().reindex(all_dates, fill_value=0)

        # Group buy by date
        buy_grouped = buy.loc[buy['symbol'] == key].copy()
        buy_grouped['date'] = pd.to_datetime(buy_grouped['hour']).dt.date
        buy_vol = buy_grouped.groupby('date')['Size'].sum().reindex(all_dates, fill_value=0)

        # Plot
        plt.plot(all_dates, sell_vol.values, label="sell")
        plt.plot(all_dates, buy_vol.values, label="buy")

        # Format x-axis
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.xticks(rotation=-30)

        # Title and labels
        plt.title('Total Volume by ' + key[:-3] + ' over Time')
        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.legend()
        plt.tight_layout()
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))
        
        plt.savefig("COMPARE2/"+key+'_Totalvolume.png')

    
    for key,symbols in comparisons.items():

        try:
            d = ddf.loc[ddf['symbol'].isin(symbols)]
            pivot_df = d.pivot_table(index='day', columns='symbol', values='volume', fill_value=0)

            ax = pivot_df.plot(kind='bar',  figsize=(10, 6))#stacked=True,

            # Access y-axis and set tick formatter
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: format(int(x), ',')))

            plt.xlabel('Date')
            plt.ylabel('Volume')
            plt.title('Volume by Symbol over Time')
            plt.legend(title='Symbol', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()

            plt.savefig("COMPARE/"+key+'.png')

            d = ddf.loc[ddf['symbol'].isin(symbols)]
            df = d.pivot_table(index='day', columns='symbol', values='close', fill_value=0)


            #display(df)
            percentage_change = {}
            
            for column in df.columns:
              first_day_price = df[column].iloc[0]
              last_day_price = df[column].iloc[-1]
              pct_change = np.log(last_day_price) - np.log(first_day_price)

              percentage_change[column] = pct_change*100

            pct_change_df = pd.DataFrame(list(percentage_change.items()), columns=['symbol', 'percentage_change']).fillna(0)

            print(key,pct_change_df)
            # pct_change_df.to_json("COMPARE2/" + key + ".json")

            # pct_change_df = pct_change_df.fillna(0)

            # Save to JSON
            pct_change_df.to_json("COMPARE2/" + key + ".json")


            pct_change_df = pct_change_df.sort_values(by='percentage_change').round(2)
            plt.figure(figsize=(10, 6))
            plt.barh(pct_change_df['symbol'], pct_change_df['percentage_change'],color=['blue', 'green'])#,
            plt.xlabel('Percentage Change %')
            plt.title('Percentage Change')
            plt.grid(axis='x', linestyle='--', alpha=0.7)

            plt.savefig("COMPARE2/"+key+'.png')
        except Exception as e:
            print("COMPARE 2 ERROR",e,key,symbols)


    df = pd.read_csv("chart_df.csv",index_col=0)

    for k,i in comparisons.items():

      select = df.loc[df['Symbol'].isin(i)]

      plt.figure(figsize=(10, 6))

      colors = ['green' if val > 0 else 'red' for val in select['ThirtyDayPriceChange'].values*100]
      plt.barh(select['Symbol'], select['ThirtyDayPriceChange'],color=colors)#,
      plt.title('Thirty Day Price Change')
      plt.xlabel('Percentage Change %')
      plt.grid(axis='x', linestyle='--', alpha=0.7)
      plt.savefig("COMPARE2/"+k+'_ThirtyDayPriceChange.png')

      plt.figure(figsize=(10, 6))

      colors = ['green' if val > 0 else 'red' for val in select['FiveDayVsThirtyDayAverageVolume'].values*100]
      plt.barh(select['Symbol'], select['FiveDayVsThirtyDayAverageVolume']*100,color=colors)#,
      plt.title('Five Day Vs Thirty Day Average Volume')
      plt.xlabel('Percentage Change %')
      plt.grid(axis='x', linestyle='--', alpha=0.7)
      plt.savefig("COMPARE2/"+k+'_FiveDayVsThirtyDayAverageVolume.png')

      plt.figure(figsize=(10, 6))
      colors = ['green' if val > 0 else 'red' for val in select['FiveDayVsNinetyDayAverageVolumeChange'].values*100]
      plt.barh(select['Symbol'], select['FiveDayVsNinetyDayAverageVolumeChange']*100,color=colors)#,
      plt.title('Five Day Vs Ninety Day Average Volume Change')
      plt.xlabel('Percentage Change %')
      plt.grid(axis='x', linestyle='--', alpha=0.7)
      plt.savefig("COMPARE2/"+k+'_FiveDayVsNinetyDayAverageVolumeChange.png')

      plt.figure(figsize=(10, 6))
      colors = ['green' if val > 0 else 'red' for val in select['RSIThreeDayVsThirtyDay'].values]
      plt.barh(select['Symbol'], select['RSIThreeDayVsThirtyDay']*100,color=colors)#,
      plt.title('RSI Three Day Vs Thirty Day')
      plt.xlabel('Percentage Change %')
      plt.grid(axis='x', linestyle='--', alpha=0.7)
      plt.savefig("COMPARE2/"+k+'_RSIThreeDayVsThirtyDay.png')



      plt.figure(figsize=(10, 6))

      colors = ['green' if val > 0 else 'red' for val in select['AverageDailyPriceCloseTenDayVsTwoHundredDay'].values]
      plt.barh(select['Symbol'], select['AverageDailyPriceCloseTenDayVsTwoHundredDay'].values*100,color=colors)#,
      plt.title('Average Daily Price Close TenDay Vs Two Hundred Day')
      plt.xlabel('Percentage Change %')
      plt.grid(axis='x', linestyle='--', alpha=0.7)
      plt.savefig("COMPARE2/"+k+'_AverageDailyPriceCloseTenDayVsTwoHundredDay.png')

      plt.figure(figsize=(10, 6))

      colors = ['green' if val > 0 else 'red' for val in select['FiveDayPriceChange'].values*100]
      plt.barh(select['Symbol'], select['FiveDayPriceChange'],color=colors)#,
      plt.title('Five Day Price Change')
      plt.xlabel('Percentage Change %')
      plt.grid(axis='x', linestyle='--', alpha=0.7)
      plt.savefig("COMPARE2/"+k+'_FiveDayPriceChange.png')

      #################################################################################
      plt.figure(figsize=(10, 6))
      plt.bar(select['Symbol'], select['WeeklyNotionalTradedAmount'],color=['blue', 'green'])#,
      plt.title('Weekly Notional Traded Amount')

      plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '${:,.0f}'.format(y)))

      y_labels = [f'${label}' for label in ax.get_yticks()]

      # plt.gca().yaxis.set_ticklabels(y_labels)
      plt.grid(axis='x', linestyle='--', alpha=0.7) 

      plt.savefig("COMPARE2/"+k+'_WeeklyNotionalTradedAmount.png')

    upload_charts(comparisons)



