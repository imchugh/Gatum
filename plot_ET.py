#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 11:20:25 2017

@author: ian
"""

from dateutil.relativedelta import relativedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import datetime as dt

import DataIO as io

path = '/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/All/GatumPasture_L5.nc'
bad_dates = [['2015-11-02', '2016-02-11'],
             ['2016-04-19', '2016-06-02'],
             ['2016-08-09', '2016-08-29']]

df = io.OzFluxQCnc_to_data_structure(path, output_structure='pandas')

df['ET'] = df.Fe * 1800 / 2257
df['C_uptake'] = df.Fc * 1800 * 12 * 10**-6

diel_df = df[['ET', 'C_uptake']].groupby([lambda x: x.year, lambda y: y.dayofyear]).sum() / 100

date_index = map(lambda x: dt.datetime(x[0], 1, 1) + dt.timedelta(x[1] - 1), 
                    zip(diel_df.index.get_level_values(0), 
                        diel_df.index.get_level_values(1)))
diel_df.index = date_index
new_index = pd.date_range(dt.datetime(diel_df.index[0].year, 1, 1),
                          dt.datetime(diel_df.index[-1].year, 12, 31))
diel_df = diel_df.reindex(new_index)

bad_dates_len_list = map(lambda x: len(diel_df.loc[x[0]: x[1]]), bad_dates)
newyear_dates_list = filter(lambda x: x.month == 1 and x.day == 1, new_index)
year_label_loc_list = map(lambda x: dt.datetime(x.year, 2, 1), newyear_dates_list)

y_lim = (-5, 55)
xtick_locs = filter(lambda x: x.day == 1, new_index)
xtick_labs = map(lambda x: dt.datetime.strftime(x, '%B')[0], xtick_locs)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (14, 10), sharex = True)
fig.patch.set_facecolor('white')

ax1.set_xlim([diel_df.index[0].to_pydatetime(), 
             diel_df.index[-1].to_pydatetime()])
ax1.set_ylim(y_lim)
ax1.xaxis.set_ticks(xtick_locs)
ax1.xaxis.set_ticklabels(xtick_labs)

ax1.set_ylabel('$ET \/(mm\/d^{-1})$', fontsize = 18, fontstyle = 'italic')

for ax in (ax1, ax2):
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis = 'x', labelsize = 14)
    ax.tick_params(axis = 'y', labelsize = 14)
    
ax1.plot(diel_df.index.to_pydatetime(), diel_df.ET, color = 'blue', lw = 0.3)
ax1.plot(diel_df.index.to_pydatetime(), diel_df.ET.rolling(window=14, 
                                                          center=True).mean(),
        color = 'blue', lw = 1.5)
props = dict(boxstyle='square', edgecolor = None, facecolor='wheat', alpha=0.5)
for i, dateset in enumerate(bad_dates):
    bad_date_start = dt.datetime.strptime(dateset[0], '%Y-%m-%d').date()
    ax1.add_patch(patches.Rectangle((bad_date_start, y_lim[0]), 
                                   bad_dates_len_list[i], y_lim[1] - y_lim[0], 
                                   color = '0.7'))
for date in newyear_dates_list:
    ax1.axvline(date, color = 'black')
    label_loc = date + relativedelta(months = 1)
    ax1.text(label_loc, y_lim[1] - (y_lim[1] - y_lim[0]) * 0.1, date.year, 
            fontsize = 18)