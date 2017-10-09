# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

path=path = os.getcwd()
files = os.listdir(path+'/equity_index/xFDAX')
files_csv = [f for f in files if f[-3:] == 'csv' and f[0]!='~']
print('Read csv files from: \n',files_csv)

df = pd.DataFrame()
for count,file in enumerate(files_csv):
    if(count == 0):
        df = pd.read_csv(path+'/equity_index/xFDAX/'+file)
#        df = pd.read_csv(path+'/equity_index/xFDAX/'+file).set_index(['Time'])
#        df['AskPriceAfter'].plot(title='AskPriceAfter',linewidth=0.6)
#    else:
#        data_one_day = pd.read_csv(path+'/equity_index/xFDAX/'+file)
#        data_one_day = pd.read_csv(path+'/equity_index/xFDAX/'+file).set_index(['Time'])
#        print('Data one day read.')
#        data_one_day['AskPriceAfter'].plot(title='AskPriceAfter',linewidth=0.6)
#        df = df.append(data_one_day,ignore_index=True)
#print('df: \n',df)
        
# Functions of calcul and normalisation of indicateurs
#self type: dataframe
# performance=(Sn - S0)/S0
def performance_simple(self):
    try:
        return (self.loc[len(self)-1]/self.loc[0]) - 1
    except:
        print('Error at performance !')


def log_daily_performance(self):
    try:
        return (self.pct_change() + 1).apply(np.log)
    except:
        print('Error at log_performance !')


#ddof: degree of freedom   
# return Var(daily log return)
def volatility(self):
    try:
        return np.sqrt(len(self))*log_daily_performance(self).std(ddof=0)# ddof = -1 ?
    except:
        print('Error at volatility !')

def sharpe(self):
    try:
        return performance_simple(self)/volatility(self)
    except:
        print('Error at sharpe !')

def max_drawdown(self):
    try:
        Rolling_Max = self.rolling(window=len(self)-1,min_periods=1,center=False).max()
        Daily_Drawdown = self/Rolling_Max - 1
        return Daily_Drawdown.min()
    except:
        print('Error at max_drawdown !')

def time_to_recovery(self):
    Rolling_Max = self.rolling(window=len(self)-1,min_periods=1,center=False).max()
    recovery = pd.DataFrame()
    recovery['rec'] = (self != Rolling_Max)
    r = recovery['rec']
    recovery['change'] = (r!=r.shift())
    index_list = recovery[recovery['change']].index
    recovery_sum = 0
    for i in range(2,len(index_list),2):
        recovery_sum += index_list[i]-index_list[i-1]
    if(len(index_list)%2 == 1):
        return recovery_sum/((len(index_list)-1)/2)
    else:
        return (recovery_sum + len(self)-1-index_list[len(index_list)-1])/((len(index_list))/2)

def skew(self):
    try:
        mean = self.mean()
        cube_mean = self.pow(3).mean() 
        std = self.std(ddof=0) # ddof = ?
        return (cube_mean - 3*mean*std*std - mean**3)/std**3
    except:
        print('Error at skew !')

#####??????????????????????????????    
#we take the average as the time gap?
time_gap=df['Time'] - df['Time'].shift(1)
#time_gap=1/time_gap
#print(time_gap)
time_gap.plot()

# the time gap we take the data 
time=15
#the data is about in frequence 1/9 s
gap=time*60*9
mi_price = ((df['AskPriceAfter'] + df['BidPriceAfter'])/2)[::gap]        
mi_price = mi_price.reset_index(drop=True)
#print(mi_price)
daily_return = (np.log(mi_price) - np.log(mi_price.shift(1)))

# KPI
print('='*20)
print('For time gap = ',time,'min')
print('Sharpe Ratio:',sharpe(mi_price))
print('Volatility:',volatility(mi_price))
print('Max Drawdown:',max_drawdown(mi_price))
print('Time to Recovery:',time_to_recovery(mi_price))
print('Skew:',skew(mi_price))
print('='*20)

# Plot
fig, axes = plt.subplots(nrows=1, ncols=2,sharey=True)
daily_return[:].plot(ax=axes[0],title='Daily_return (log)',linewidth=1)
daily_return[:].plot.hist(ax=axes[1],bins=50,orientation='horizontal',color='g',title='Distribution of daily_return')

