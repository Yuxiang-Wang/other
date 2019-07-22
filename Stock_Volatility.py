# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 22:06:09 2018

@author: yuxiang
"""

from numpy import exp,sqrt,log
from scipy.stats import norm

def get_hist_volatility(ticker,startdate,enddate,frequency):
    import pandas as pd
    import numpy as np
    from yahoofinancials import YahooFinancials
    
    histprice = YahooFinancials(ticker)
    dfprice = pd.DataFrame(histprice.get_historical_price_data(startdate,enddate,frequency)[ticker]['prices'])
    dfprice.insert(0,'cusip',ticker) 
    df=dfprice[['cusip','formatted_date','close']]
    
    df.loc[:,'lag_close']=df.close.shift(1)
    df['daily_return']=df.close/df.close.shift(1)-1
    df['volatility']=np.std(df.daily_return)
    
    v_daily=df.loc[0,'volatility']
    v_annual=v_daily*np.sqrt(365)
    return v_annual

def BS_price(call_or_put,S,K,r,v,T):
    d1=(log(S/K)+(r+0.5*v**2)*T)/(v*sqrt(T))
    d2=d1-v*sqrt(T)
    if(call_or_put=='call'):
        return S*norm.cdf(d1)-exp(-r*T)*K*norm.cdf(d2)
    else:
        return S*norm.cdf(-d1)-exp(-r*T)*K*norm.cdf(-d2)

def BS_vage(call_or_put,S,K,r,v,T):
    d1=(log(S/K)+(r+0.5*v**2)*T)/(v*sqrt(T))
    return S*norm.pdf(d1)*sqrt(T)

def get_implied_volatility(call_or_put,option_price,S,K,r,sigma,T):
    MAX_ITERATION=100
    EPS=1.0e-7

    for i in range(MAX_ITERATION): #i=1 sigma=0.5 call_or_put='call'
        sigma=sigma-(BS_price(call_or_put,S,K,r,sigma,T)-option_price)/BS_vage(call_or_put,S,K,r,sigma,T)
        if(abs(option_price-BS_price(call_or_put,S,K,r,sigma,T))<EPS):
            return sigma
    
    return 0
        
     











        
