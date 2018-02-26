#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:54:26 2018

@author: ian
"""

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
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

month_df = combined_df.dropna().groupby([lambda x: x.year, 
                                         lambda y: y. month]).sum()
params = linregress(month_df['Cavendish_rainfall_mm'], 
                    month_df['Gatum_rainfall_mm'])
combined_df.loc[np.isnan(combined_df.Gatum_rainfall_mm), 'Gatum_rainfall_mm'] = (
        combined_df['Cavendish_rainfall_mm'] * params.slope + params.intercept)

compare_df = combined_df.groupby([lambda x: x.dayofyear]).mean()[:-1]
temp_df = combined_df.loc['2015-03-01':'2016-02-28'].reset_index()
temp_df.index = np.linspace(1, 365, 365)
compare_df['2015'] = temp_df['Gatum_rainfall_mm']
temp_df = combined_df.loc['2016-03-01':'2017-02-28'].reset_index()
temp_df.index = np.linspace(1, 365, 365)
compare_df['2016'] = temp_df['Gatum_rainfall_mm']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (12, 4), sharex = True)
fig.patch.set_facecolor('white')

ax1_b = ax1.twinx()
ax1_b.plot(compare_df.index, compare_df['Gatum_rainfall_mm'].cumsum())
ax1_b.fill_between(compare_df.index, np.tile(0, len(compare_df)), 
                   compare_df['Gatum_rainfall_mm'].cumsum(), alpha = 0.5)
ax1.bar(compare_df.index, compare_df['2015'], color = 'black')