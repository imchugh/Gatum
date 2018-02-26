#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:54:26 2018

@author: ian
"""

import datetime as dt
import pandas as pd
from scipy.stats import linregress
import pdb

def get_date_from_multi_index(idx):
    return [dt.date(idx.get_level_values(0)[i], idx.get_level_values(1)[i], 1) 
            for i in xrange(len(idx))]    

def get_date_from_dataframe_vars(df):
    return [dt.date(df.Year[i], df.Month[i], df.Day[i]) 
            for i in xrange(len(df))]

paths_dict = {'Cavendish':'/home/ian/Documents/Gatum project/Respiration paper/'
                          'Data/BOM/IDCJAC0009_089009_1800_Data_Cavendish.csv',
              'Gatum': '/home/ian/Documents/Gatum project/Respiration paper/'
                       'Data/BOM/IDCJAC0009_089043_1800_Data_Gatum.csv'}

df_list = []
for name in paths_dict:
    df = pd.read_csv(paths_dict[name])
    df.index = get_date_from_dataframe_vars(df)
    df = df[['Rainfall amount (millimetres)', 'Quality']]
    df.columns = ['{}_rainfall_mm'.format(name), '{}_Quality'.format(name)]
    df_list.append(df)

begin_date = min([df.index[0] for df in df_list])
end_date = max([df.index[-1] for df in df_list])
new_index = pd.date_range(begin_date, end_date, freq = 'D')
combined_df = pd.concat([df.reindex(new_index) for df in df_list], axis = 1)


month_df = combined_df.groupby([lambda x: x.year, lambda y: y. month]).sum()
params = linregress(month_df['Cavendish_rainfall_mm'], 
                    month_df['Gatum_rainfall_mm'])