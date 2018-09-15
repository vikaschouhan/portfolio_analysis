##################################################
# Indicators not defined by talib are defined here
# 
import pandas as pd
import numpy as np
import talib

## Super trend indicator
# Author :  Mathieu Meynier
# Original link : https://www.quantopian.com/posts/error-computing-super-trend-indicator
def SuperTrend(data, period, multiplier, columns=['h', 'l', 'o', 'c']):
    high_i   = columns[0]
    low_i    = columns[1]
    open_i   = columns[2]
    close_i  = columns[3]

    data['MP'] = (data[high_i]+data[low_i])/2
    data['ATR'] = talib.ATR(data[high_i], data[low_i], data[close_i].shift(1), timeperiod=period)
    data['ATR'] = data['ATR'].fillna(0)

    data['BASIC UPPERBAND'] = data['MP'] + multiplier * data['ATR']
    data['BASIC LOWERBAND'] = data['MP'] - multiplier * data['ATR']
    data['FINAL UPPERBAND'] = np.float64()
    data['FINAL LOWERBAND'] = np.float64()

    for i in range(0, len(data)):
        if i < period:
            data.iloc[i, data.columns.get_loc('FINAL UPPERBAND')] = 0
            data.iloc[i, data.columns.get_loc('FINAL LOWERBAND')] = 0
        else:
            data.iloc[i, data.columns.get_loc('FINAL UPPERBAND')] = np.where(np.logical_or(data['BASIC UPPERBAND'].iloc[i] < data['FINAL UPPERBAND'].iloc[i-1]  
                                               , data[close_i].iloc[i-1]>data['FINAL UPPERBAND'].iloc[i-1]),
                                               data['BASIC UPPERBAND'].iloc[i], data['FINAL UPPERBAND'].iloc[i-1])
    
            data.iloc[i, data.columns.get_loc('FINAL LOWERBAND')] = np.where(np.logical_or(data['BASIC LOWERBAND'].iloc[i] > data['FINAL LOWERBAND'].iloc[i-1] 
                                               , data[close_i].iloc[i-1]<data['FINAL LOWERBAND'].iloc[i-1]),
                                               data['BASIC LOWERBAND'].iloc[i], data['FINAL LOWERBAND'].iloc[i-1])
    # endfor
        
    
    data['SuperTrend'] = 0
    
    for i in range(0, len(data)):
        if i < period:
            data.iloc[i, data.columns.get_loc('SuperTrend')] = 0
        else:
            conditions = [np.logical_and(data['SuperTrend'].iloc[i-1] == data['FINAL UPPERBAND'].iloc[i-1],  \
                 data[close_i].iloc[i] < data['FINAL UPPERBAND'].iloc[i])
                 , np.logical_and(data['SuperTrend'].iloc[i-1] == data['FINAL UPPERBAND'].iloc[i-1], data[close_i].iloc[i] > data['FINAL UPPERBAND'].iloc[i])
                 , np.logical_and(data['SuperTrend'].iloc[i-1] == data['FINAL LOWERBAND'].iloc[i-1], data[close_i].iloc[i] > data['FINAL LOWERBAND'].iloc[i])
                 , np.logical_and(data['SuperTrend'].iloc[i-1] == data['FINAL LOWERBAND'].iloc[i-1], data[close_i].iloc[i] < data['FINAL LOWERBAND'].iloc[i])]
            choices = [data['FINAL UPPERBAND'].iloc[i], data['FINAL LOWERBAND'].iloc[i], data['FINAL LOWERBAND'].iloc[i], data['FINAL UPPERBAND'].iloc[i]]
            data.iloc[i, data.columns.get_loc('SuperTrend')] = np.select(conditions, choices)
    # endfor

    # Drop all zeros
    data = data.drop(data[(data.SuperTrend == 0.0)].index)
    return data
# enddef
