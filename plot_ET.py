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

# Set stuff up
path = '/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/All/GatumPasture_L5.nc'
bad_dates = [['2015-11-02', '2016-02-11'],
             ['2016-04-19', '2016-06-02'],
             ['2016-08-09', '2016-08-29']]

# Get the raw data and make the daily data frame
df = io.OzFluxQCnc_to_data_structure(path, output_structure='pandas')
df['ET'] = df.Fe / 2257
diel_df = df[['ET', 'Fc']].groupby([lambda x: x.year, 
                                    lambda y: y.dayofyear]).mean()
date_index = map(lambda x: dt.datetime(x[0], 1, 1) + dt.timedelta(x[1] - 1), 
                    zip(diel_df.index.get_level_values(0), 
                        diel_df.index.get_level_values(1)))
diel_df.index = date_index
new_index = pd.date_range(dt.datetime(diel_df.index[0].year, 1, 1),
                          dt.datetime(diel_df.index[-1].year, 12, 31))
diel_df = diel_df.reindex(new_index)
diel_df.Fc = diel_df.Fc * 0.0864 * 12
diel_df.ET = diel_df.ET * 86.4

# Create date lists
bad_dates_len_list = map(lambda x: len(diel_df.loc[x[0]: x[1]]), bad_dates)
newyear_dates_list = filter(lambda x: x.month == 1 and x.day == 1, new_index)
year_label_loc_list = map(lambda x: dt.datetime(x.year, 2, 1), newyear_dates_list)

# Initialise plot
xtick_locs = filter(lambda x: x.day == 1, new_index)
xtick_labs = map(lambda x: dt.datetime.strftime(x, '%B')[0], xtick_locs)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (14, 10))#, sharex = True)
fig.patch.set_facecolor('white')

# Do common stuff for both plots
y_lims = [(0, 4), (-12, 6)]
y_labels = ['$ET \/(mm\/d^{-1})$', '$NEE\/(gC\/m^{-2}\/d^{-1})$']

i = 0
for ax in (ax1, ax2):
    y_lim = y_lims[i]
    ax.set_xlim([diel_df.index[0].to_pydatetime(), 
                 diel_df.index[-1].to_pydatetime()])
    ax.xaxis.set_ticks(xtick_locs)
    ax.xaxis.set_ticklabels(xtick_labs)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis = 'x', labelsize = 14)
    ax.tick_params(axis = 'y', labelsize = 14)
    ax.set_ylim(y_lim)
    ax.set_ylabel(y_labels[i], fontsize = 18, fontstyle = 'italic')
    i += 1
    for j, dateset in enumerate(bad_dates):
        bad_date_start = dt.datetime.strptime(dateset[0], '%Y-%m-%d').date()
        ax.add_patch(patches.Rectangle((bad_date_start, y_lim[0]), 
                                       bad_dates_len_list[j], y_lim[1] - y_lim[0], 
                                       color = '0.7'))
    for date in newyear_dates_list:
        label_loc = date + relativedelta(months = 1)
        ax.axvline(date, color = 'black')
        ax.text(label_loc, y_lim[1] - (y_lim[1] - y_lim[0]) * 0.1, date.year, 
                fontsize = 18)

# Do stuff specific to ax1 
ax1.plot(diel_df.index.to_pydatetime(), diel_df.ET, color = 'blue', lw = 0.3)
ax1.plot(diel_df.index.to_pydatetime(), diel_df.ET.rolling(window=14, 
                                                           center=True).mean(),
        color = 'blue', lw = 1.5)

# Do stuff specific to ax2
ax2.axhline(0, color = 'grey')
ax2.plot(diel_df.index.to_pydatetime(), diel_df.Fc, color = 'green', 
         lw = 0.3)
ax2.plot(diel_df.index.to_pydatetime(), diel_df.Fc.rolling(window=14, 
                                                           center=True).mean(),
        color = 'green', lw = 1.5)
    