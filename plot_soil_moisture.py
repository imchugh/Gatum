#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 15:23:25 2017

@author: ian
"""
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import DataIO as io
#
## Use a simple median filter to clean up the data
#def filter_this(series, outlier_val):
#    
#    hi_qtl = series.quantile(0.75)
#    lo_qtl = series.quantile(0.25)
#    IQR =  hi_qtl - lo_qtl
#    lo_outlier = lo_qtl - IQR * outlier_val
#    hi_outlier = hi_qtl + IQR * outlier_val
#    series[(series > hi_outlier) | (series < lo_outlier)] = np.nan
#    series[series > 1] = np.nan
#    return
#
## Set file paths
#soil_path='/mnt/fluxdata/Gatum_data/Soil_moisture/20170530/Gatum_pasture_soil_CR1000_Hourly.dat'
#flux_path='/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/All/GatumPasture_L3.nc'
#
## Get the soil data
#soil_df = pd.read_csv(soil_path, skiprows = [0,2,3], na_values = 'NAN')
#soil_df.index = [dt.datetime.strptime(i, '%Y-%m-%d %H:%M:%S') 
#                 for i in soil_df.TIMESTAMP]
#new_range = pd.date_range(soil_df.index[0], soil_df.index[-1], freq='60T')
#soil_df = soil_df.reindex(new_range)
#soil_df = soil_df.resample('30T').mean().interpolate()
#
## Get the soil moisture variables and do basic qc
#moisture_list = [var for var in soil_df.columns if 'VWC' in var]
#moisture_list = moisture_list[:6]
#date_list = sorted(list(set([dt.datetime.strftime(this_dt.date(), '%Y-%m-%d') 
#                             for this_dt in soil_df.index])))
#for this_var in moisture_list:
#    for this_date in date_list:
#        filter_this(soil_df.loc[this_date, this_var], 2)
#    soil_df[this_var].interpolate()
#
## Get the flux station data
#flux_df = io.OzFluxQCnc_to_data_structure(flux_path, output_structure='pandas')
#
## Align the dates of the datasets
#soil_df = soil_df.loc[soil_df.index[0]: flux_df.index[-1]]
#flux_df = flux_df.loc[soil_df.index[0]: flux_df.index[-1]]
#
## Remove the diel signal from the soil moisture measurements and take an average
#daily_soil_df = soil_df.groupby([lambda x: x.year, lambda y: y.dayofyear]).mean()
#daily_soil_df.index = [dt.datetime(this_tuple[0], 1, 1) + 
#                       dt.timedelta(days = this_tuple[1] - 1) 
#                       for this_tuple in daily_soil_df.index.get_values()]
#new_df = daily_soil_df[moisture_list].resample('30T').bfill()
#new_date_index = pd.date_range(soil_df.index[0], soil_df.index[-1], freq = '30T')
#new_df = new_df.reindex(new_date_index)
#mean_series = new_df.mean(axis = 1)

n_years = soil_df.index[-1].year - soil_df.index[0].year + 1
years = [soil_df.index[0].year + counter for counter in range(n_years)]
lst=[]
for year in years:
    lst.append([dt.datetime(year, this_month, 1) 
    for this_month in range(1,13)])
date_lst = []
for sub_list in lst:
    for item in sub_list:
        date_lst.append(item)
month_list = ['J','F','M','A','M','J','J','A','S','O','N','D'] * n_years

# Plot
fig, ax = plt.subplots(1, figsize = (14, 8))
fig.patch.set_facecolor('white')
ax.set_xlim(dt.datetime(years[0],1,1), dt.datetime(years[-1],12,31))
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks(date_lst)
ax.xaxis.set_ticklabels(month_list)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.tick_params(axis = 'x', labelsize = 14)
ax.tick_params(axis = 'y', labelsize = 14)
ax.set_xlabel('$Month$', fontsize = 18)
ax.set_ylabel(r'$\theta \/(m^3\/m^{-3})$', fontsize = 18)
for var in moisture_list:
    ax.plot(soil_df.index, soil_df[var], lw = 0.5)
ax.plot(flux_df.index, flux_df.Sws, lw = 2, color = 'grey')
ax.plot(mean_series.index, mean_series, label = 'VWC_mean', lw = 2, 
        color = 'black')
ax.legend(loc='upper left', ncol = 2, frameon = False)