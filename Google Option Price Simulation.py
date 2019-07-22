# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 21:32:10 2018

@author: yuxiang
"""
import datetime
from random import gauss
from numpy import exp,sqrt,log
from scipy.stats import norm
from Stock_Volatility import get_hist_volatility

def stock_price(S,r,v,T):
    return S*exp((r-0.5*v**2)*T+v*sqrt(T)*gauss(0,1.0))

S=980
K=1015
r=0.0225
v=get_hist_volatility('GOOG','2017-12-20','2018-12-20','daily')
T=(datetime.date(2019,1,11) - datetime.date(2018,12,19)).days / 365.0
discount_factor=exp(-r*T)

trials=100000
payoff=[]

for i in range(trials):
    payoff.append(max(stock_price(S,r,v,T)-K,0))

call_price=discount_factor*(sum(payoff)/float(trials))
print('call price:',call_price)

########## BS formular
d1=(log(S/K)+(r+0.5*v**2)*T)/(v*sqrt(T))
d2=(log(S/K)+(r-0.5*v**2)*T)/(v*sqrt(T))
call_price_BS=S*norm.cdf(d1)-discount_factor*K*norm.cdf(d2)
print('call price in BS formular:',call_price_BS)

########## implied volatility
from Stock_Volatility import get_implied_volatility
option_price=8
T=7/365
sigma_guess=0.5
v_implied=get_implied_volatility('call',option_price,S,K,r,sigma_guess,T)
print('implied volatility:',v_implied)

########## volatility smile
%matplotlib inline 
import matplotlib.pyplot as plt 
import numpy as np 
from Stock_Volatility import get_implied_volatility

x=[i for i in range(100)]
plt.plot(x,np.sin(x),'-py')










