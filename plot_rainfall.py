#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:54:26 2018

@author: ian
"""

import calendar
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

fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (12, 4))
fig.patch.set_facecolor('white')
int_idx = np.concatenate([np.linspace(3,12,10), np.linspace(1,2,2)]).astype(int)
month_locs = np.cumsum([1] + map(lambda x: calendar.monthrange(2015, x)[1], 
                                 int_idx[:-1]))
month_labels = map(lambda x: calendar.month_name[x][0], int_idx)
xlim = [1, 365]
ylim = [0, round(compare_df[['2015', '2016']].max().max() * 1.05)]
yblim = [0, 1000]
d = {'2015': ax1, '2016': ax2}
for i, year in enumerate(d.keys()):
    ax = d[year]
    if i == 0:
        ax.set_ylabel('Daily precipitation (mm)')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xticks(month_locs)
    ax.set_xticklabels(month_labels)
    ax_b = ax.twinx()
    if i == 1:
        ax_b.set_ylabel('Cumulative precipitation (mm)')
    ax_b.set_ylim(yblim)
    ax_b.fill_between(compare_df.index, np.tile(0, len(compare_df)), 
                      compare_df['Gatum_rainfall_mm'].cumsum(), 
                      alpha = 0.3)
    ax.bar(compare_df.index, compare_df[year], color = 'black')
    ax_b.plot(compare_df.index, compare_df[year].cumsum(), color = 'black')
    ax.text(30, 50, year, verticalalignment = 'center')
    for loc in month_locs[3], month_locs[6], month_locs[9]:
        ax.axvline(loc, color = 'orange', lw = 0.9, ls = ':')