# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 16:40:47 2018

@author: yuxiang
"""



##################### import stocks data from yahoofinancials

import pandas as pd
import numpy as np
from yahoofinancials import YahooFinancials

# import symbols
stocks = pd.read_excel('D:/Users/yuxiang/spyder/symbol.xlsx', sheetname=0) 
stocks.columns
ticker = stocks['Ticker ']

getpriceError={}  # some tickers in the symbol excel have different name on yahoofinancials
# getpriceError dict is for recording those error tickers
startdate = '2015-08-01'
enddate = '2018-09-01'
import pyodbc
conn = pyodbc.connect("driver={ODBC Driver 13 for SQL Server};"
                "Server=DESKTOP-U9EDO5C\SQLEXPRESS;"
                "Database=test;"
                "Trusted_Connection=yes;")

# for every ticker, get price info from yahoofinancials and import it into database
n=1
for i in ticker:   
    try:
        print(n,i)
        histprice = YahooFinancials(i)
        dfprice = pd.DataFrame(histprice.get_historical_price_data(startdate,enddate,'monthly')[i]['prices'])
        dfprice.insert(0,'cusip',i) 
        df=dfprice.drop(columns='date')
        cursor = conn.cursor()
        for index,row in df.iterrows():
            #print(index,row['cusip'], row['formatted_date']) 
            cursor.execute('''INSERT INTO dbo.beta([cusip],[date],[adjclose],[close],
                            [high],[low],[open],[volume]) 
                            values (?,?,?,?,?,?,?,?)''',row['cusip'], 
                                             row['formatted_date'],
                                             row['adjclose'],
                                             row['close'],
                                             row['high'],
                                             row['low'],
                                             row['open'],
                                             row['volume'])         
            conn.commit()
        cursor.close()

        print(n,i,'insert into database done')
        n=n+1
        getpriceError[i]=0
    except:
        print(i,'error')
        getpriceError[i]=1
        pass


# get rid of error tickers
beta_ticker = ticker
for i in beta_ticker:
    if getpriceError[i]==1:
        beta_ticker=beta_ticker[beta_ticker!=i]

# get risk-free rate and market rate
FFfactor = pd.read_csv('D:/Users/yuxiang/spyder/F-F_Research_Data_Factors.CSV')
FFfactor = FFfactor.rename(index=str,columns={'Unnamed: 0':'date'})
FFfactor = FFfactor[FFfactor.date>=201508]
FFfactor['mkt']=FFfactor['Mkt-RF'].astype(float)+FFfactor.RF.astype(float)
FFfactor['date']=pd.to_datetime(FFfactor['date'], format='%Y%m')
market = FFfactor[['date','mkt']]

##################### import data from database and calculate beta

query = ('SELECT [cusip],[date],[adjclose] FROM [dbo].[beta]')
price=pd.read_sql(query,conn)
n=1
for i in beta_ticker:  #i = 'AAN'
    tempprice = price[price['cusip']==i]  
    tempprice=tempprice.sort_values(by='date',axis=0)
    tempprice['adjreturn']=np.log(tempprice.adjclose/tempprice.adjclose.shift(1))
    beta = tempprice.dropna(axis=0)
    beta['date']=pd.to_datetime(beta['date'], format='%Y-%m-%d')
    beta = beta.merge(market,how='left',on='date')
    beta.adjreturn = beta.adjreturn*100
    
    cov = np.cov(beta.adjreturn,beta.mkt)
    tempprice['Beta'] = cov[0][1]/cov[1][1] 
    
    print(n,i,'beta done')
      
    cursor = conn.cursor()
    j=1
    
    for index,row in tempprice.iterrows():
        #print(index,row['Beta']) 
        cursor.execute('''update dbo.beta
                       set beta= ?
                       where cusip= ?''',row['Beta'],row['cusip'])         
        conn.commit()
        print(n,j,i,'insert beta done ------')
        j=j+1
    cursor.close()
    n=n+1

conn.close()
    
        
        
        
        

  

