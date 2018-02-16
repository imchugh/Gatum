#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:54:26 2018

@author: ian
"""

import datetime as dt
import pandas as pd
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

s_list = []
for name in paths_dict:
    df = pd.read_csv(paths_dict[name])
    df.index = get_date_from_dataframe_vars(df)
    grp_s = (df.groupby([lambda x: x.year, lambda y: y.month]).sum()
             ['Rainfall amount (millimetres)'])
    grp_s.index = get_date_from_multi_index(grp_s.index)
    grp_s.name = name
    s_list.append(grp_s)

begin_date = min([s.index[0] for s in s_list])
end_date = max([s.index[-1] for s in s_list])
new_index = pd.date_range(begin_date, end_date, freq = 'MS')
combined_df = pd.concat([s.reindex(new_index) for s in s_list], axis=1)
