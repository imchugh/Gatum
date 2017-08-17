#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 14:13:53 2017

@author: ian
"""

import datetime as dt
import pandas as pd

import DataIO as io

# Set file paths
soil_path='/mnt/fluxdata/Gatum_data/Soil_moisture/20170530/Gatum_pasture_soil_CR1000_Hourly.dat'
flux_path='/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/All/GatumPasture_L3.nc'

# Get the soil data
soil_df = pd.read_csv(soil_path, skiprows = [0,2,3], na_values = 'NAN')
soil_df.index = [dt.datetime.strptime(i, '%Y-%m-%d %H:%M:%S') 
                 for i in soil_df.TIMESTAMP]
new_range = pd.date_range(soil_df.index[0], soil_df.index[-1], freq='60T')
soil_df = soil_df.reindex(new_range)
soil_df = soil_df.resample('30T').mean().interpolate()

# Get the soil moisture variables and do basic qc
moisture_list = [var for var in soil_df.columns if 'VWC' in var]
moisture_list = moisture_list[:6]
date_list = sorted(list(set([dt.datetime.strftime(this_dt.date(), '%Y-%m-%d') 
                             for this_dt in soil_df.index])))

# Get the flux station data
flux_df = io.OzFluxQCnc_to_data_structure(flux_path, output_structure='pandas')

# Align the dates of the datasets
soil_df = soil_df.loc[soil_df.index[0]: flux_df.index[-1]]
flux_df = flux_df.loc[soil_df.index[0]: flux_df.index[-1]]

soil_t_list = [var for var in soil_df if 'Soil_Temp' in var]
soil_t_list.append('Ts_fluxstn')
soil_df['Ts_fluxstn'] = flux_df.Ts
daily_ts_df = (soil_df[soil_t_list].groupby([lambda x: x.year, 
                                             lambda y: y.dayofyear]).max() - 
               soil_df[soil_t_list].groupby([lambda x: x.year, 
                                             lambda y: y.dayofyear]).min())
daily_ts_df.index = [dt.datetime(this_tuple[0], 1, 1) + 
                     dt.timedelta(days = this_tuple[1] - 1) 
                     for this_tuple in daily_ts_df.index.get_values()]