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
import os
import pandas as pd
from scipy.stats import linregress

import pdb

def get_date_from_multi_index(idx):
    return [dt.date(idx.get_level_values(0)[i], idx.get_level_values(1)[i], 1) 
            for i in xrange(len(idx))]    

def get_date_from_dataframe_vars(df):
    return [dt.date(df.Year[i], df.Month[i], df.Day[i]) 
            for i in xrange(len(df))]

path = '/home/ian/Dropbox/Work/Manuscripts/Writing/Gatum+_respiration/Data'
id_dict = {'Gatum': '089043', 'Cavendish': '089009'}
f_list = filter(lambda x: 'Data' in x, os.listdir(path))
paths_dict = {key: os.path.join(path, [x for x in f_list if id_dict[key] in x][0])
                    for key in id_dict}

df_list = []
for name in paths_dict:
    df = pd.read_csv(paths_dict[name])
    df.index = get_date_from_dataframe_vars(df)
    df = df[['Rainfall amount (millimetres)', 'Quality']]
    df.columns = ['{}_rainfall_mm'.format(name), '{}_Quality'.format(name)]
    df_list.append(df)

begin_date = max([df.index[0] for df in df_list])
end_date = max([df.index[-1] for df in df_list])
new_index = pd.date_range(begin_date, end_date, freq = 'D')
combined_df = pd.concat([df.reindex(new_index) for df in df_list], axis = 1)

month_df = combined_df.dropna().groupby([lambda x: x.year, 
                                         lambda y: y. month]).sum()
params = linregress(month_df['Cavendish_rainfall_mm'], 
                    month_df['Gatum_rainfall_mm'])
combined_df.loc[np.isnan(combined_df.Gatum_rainfall_mm), 
                'Gatum_rainfall_mm'] = (combined_df['Cavendish_rainfall_mm'] * 
                                        params.slope + params.intercept)
combined_s = combined_df.loc[~((combined_df.index.month==2) &
                               (combined_df.index.day==29)), 'Gatum_rainfall_mm']
compare_df = pd.DataFrame({'Long-term mean': 
                            combined_s.groupby([lambda x: x.dayofyear]).mean()[:-1]})
year_list = ['2015', '2016', '2017', '2018']
for year in year_list:
    temp_s = combined_s.loc[year]
    temp_s.index = compare_df.index
    compare_df[year] = temp_s
sums_df = compare_df.sum().round(1)

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize = (12, 12))
fig.patch.set_facecolor('white')
month_locs = np.cumsum([1] + map(lambda x: calendar.monthrange(2015, x)[1], 
                       np.arange(1,12,1)))
month_labels = map(lambda x: calendar.month_name[x][0], np.arange(1,13,1))
xlim = [1, 365]
ylim = [0, round(compare_df[['2015', '2016', '2017', '2018']].max().max() * 1.05)]
yblim = [0, 1100]
d = {'2015': ax1, '2016': ax2, '2017': ax3, '2018': ax4}
for i, year in sorted(enumerate(d.keys())):
    ax = d[year]
    if i < 2:
        ax.set_ylabel('Daily precipitation (mm)')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xticks(month_locs)
    ax.set_xticklabels(month_labels)
    ax_b = ax.twinx()
    if i >= 2:
        ax_b.set_ylabel('Cumulative precipitation (mm)')
    ax_b.set_ylim(yblim)
    ax_b.fill_between(compare_df.index, np.tile(0, len(compare_df)), 
                      compare_df['Long-term mean'].cumsum(), 
                      alpha = 0.3, color = 'grey')
    ax.bar(compare_df.index, compare_df[year], color = 'black')
    ax_b.plot(compare_df.index, compare_df[year].cumsum().interpolate(), 
              color = 'black')
    text = '{}mm'.format(str(sums_df.loc[year]))
    ax.text(0.08, 0.9, year, horizontalalignment = 'left', 
            verticalalignment = 'center', transform=ax.transAxes, 
            fontweight = 'bold')
    ax.text(0.37, 0.9, text, horizontalalignment = 'center', 
            verticalalignment = 'center', transform=ax.transAxes)
    for loc in month_locs[3], month_locs[6], month_locs[9]:
        ax.axvline(loc, color = 'grey', lw = 0.9, ls = ':')
plt.savefig('/home/ian/Dropbox/Work/Manuscripts/Writing/Gatum+_respiration/'
            'Latex/Figs/Precip.png', bbox_inches = 'tight')