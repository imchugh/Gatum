# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 14:43:21 2016

@author: imchugh
"""

import DataIO as io
import os
import numpy as np
import pandas as pd
import datetime as dt
import solar_functions as sf
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.gridspec as gridspec
import modis_functions as mf
import pdb

reload(sf)
reload(mf)

def ramp_func_lin_T_Fsd(df, VWC_lo, VWC_hi, pr_param, a, b):

    VWC = df.Sws_mean
    T = df.night_T_mean
    pr = df.day_Fc_mean
    
    VWC_ind = np.where(VWC < VWC_lo, 0, 
                       np.where(VWC > VWC_hi, 1, 
                                (VWC - VWC_lo) / (VWC_hi - VWC_lo)))
    pr_ind = pr_param * pr
    return VWC_ind * pr_ind * a * np.exp(b * T)

def ramp_func_lin_T(df, VWC_lo, VWC_hi, a, b):

    VWC = df.Sws_mean
    T = df.night_T_mean
    Fsd = df.Fsd_sum
    
    VWC_ind = np.where(VWC < VWC_lo, 0, 
                       np.where(VWC > VWC_hi, 1, 
                                (VWC - VWC_lo) / (VWC_hi - VWC_lo)))

    return VWC_ind * a * np.exp(b * T)


def soil_m_func(df, VWC_lo, VWC_hi, a):

    VWC = df.Sws_mean
    Fsd = df.Fsd_sum
    VWC_ind = np.where(VWC < VWC_lo, 0, 
                       np.where(VWC > VWC_hi, 1, 
                                (VWC - VWC_lo) / (VWC_hi - VWC_lo)))
    
    return VWC_ind * a * Fsd

lat = -37.386853
lon = 142.003519
alt = 300
GMT_zone = 10
Ta_Ts_ratio = [5,1]
modis_prod = 'MOD15A2'
modis_data_band = 'Lai_1km'
modis_QC_band = 'FparLai_QC'

path1 = '/home/imchugh/Documents/Gatum/EC_data/2015/'
name1 = 'GatumPasture_2015_L4.nc'
f_name1 = os.path.join(path1, name1)
df1 = io.OzFluxQCnc_to_data_structure(f_name1, 
                                      var_list=['Fc', 'Ta', 'Ts', 'Fsd', 'Sws', 
                                                'ustar'], 
                                      output_structure='pandas')

path2 = '/home/imchugh/Documents/Gatum/EC_data/2016/'
name2 = 'GatumPasture_2016_L4.nc'
f_name2 = os.path.join(path2, name2)
df2 = io.OzFluxQCnc_to_data_structure(f_name2, 
                                      var_list=['Fc', 'Ta', 'Ts', 'Fsd', 'Sws', 
                                                'ustar'],
                                      output_structure='pandas')
df2.Fc = df2.Fc * 1000 / 44
df = pd.concat([df1, df2])
#df = df1
start_date = dt.datetime(df1.index[0].year, 1, 1)
end_date = dt.datetime(df2.index[-1].year, 3, 31, 23, 30)
new_index = pd.date_range(start_date, end_date, freq='30T')
df = df.reindex(new_index)

# Get sunrise and sunset times
date_time = np.array([dt.datetime(i.year, i.month, i.day, i.hour, i.minute) 
                      for i in df.index])
rise_times = sf.get_ephem_solar({'date_time': date_time},
                                lat = lat, lon = lon, alt = alt, 
                                GMT_zone = GMT_zone, return_var = 'rise')
set_times = sf.get_ephem_solar({'date_time': date_time},
                               lat = lat, lon = lon, alt = alt, 
                               GMT_zone = GMT_zone, return_var = 'set')

# Create a time constraint tuple set for grabbing day data
rise_datetimes = [dt.datetime.combine(rise_times['date'][i], 
                                      rise_times['rise'][i]) 
                  for i in xrange(len(rise_times['date']))]

set_datetimes = [dt.datetime.combine(set_times['date'][i], 
                                     set_times['set'][i]) 
                 for i in xrange(len(set_times['date']))]
day_ranges = zip(rise_datetimes, set_datetimes)

# Create a time constraint tuple set for grabbing night data (ignore the 
# first night because it has no prior day, and we are examining the effects of
# prior day productivity on nocturnal respiration)
start_set_d = sf.get_ephem_solar({'date_time': set_datetimes[0] - dt.timedelta(1)},
                                 lat = lat, lon = lon, alt = alt, 
                                 GMT_zone = GMT_zone, return_var = 'set')
start_set = dt.datetime.combine(start_set_d['date'][0], start_set_d['set'][0]) 
end_rise_d = sf.get_ephem_solar({'date_time': rise_datetimes[-1] + dt.timedelta(1)},
                                 lat = lat, lon = lon, alt = alt, 
                                 GMT_zone = GMT_zone, return_var = 'rise')
end_rise = dt.datetime.combine(end_rise_d['date'][0], end_rise_d['rise'][0]) 
night_ranges = zip(set_datetimes, rise_datetimes[1:] + [end_rise])                       

# Use day datetimes to make a date array for plotting
dates = [this_date.date() for this_date in rise_datetimes]

# Get modis LAI data
#modis_start = dates[0]
#modis_end = dates[-1]
#modis_dict = mf.get_MODIS_subset(lat, lon, modis_prod, modis_data_band,
#                                modis_QC_band, 
#                                requestStart = modis_start,
#                                requestEnd = modis_end)
#modis_df = pd.DataFrame(modis_dict)
#modis_df.index = modis_df.date
#modis_df['QC_int'] = np.array([int(i, 2) for i in modis_dict['QC']])
#modis_df['data'][modis_df['QC_int'] <> 0] = np.nan
#modis_df = modis_df.reindex(dates)

# Find the max number of values for each of day and night
max_day_recs = np.array([(this_range[1] - this_range[0]).seconds / 1800 
                         for this_range in day_ranges])
max_night_recs = np.array([(this_range[1] - this_range[0]).seconds / 1800 
                           for this_range in night_ranges])

new_df = pd.DataFrame({'max_day_recs': max_day_recs,
                       'max_night_recs': max_night_recs}, index = dates)
                       
new_df['actual_day_recs'] = np.array([df.loc[this_date[0]:this_date[1], 'Fc'].dropna().count() 
                                     for this_date in day_ranges])
new_df['actual_night_recs'] = np.array([df.loc[this_date[0]:this_date[1], 'Fc'].dropna().count() 
                                       for this_date in night_ranges])
new_df['night_Fc_mean'] = np.array([df.loc[this_date[0]:this_date[1], 'Fc'].dropna().mean() 
                                   for this_date in night_ranges])
new_df['day_Fc_mean'] = np.array([df.loc[this_date[0]:this_date[1], 'Fc'].dropna().mean() 
                                 for this_date in day_ranges])
new_df['Fsd_sum'] = np.array([(df.loc[this_date[0]:this_date[1], 'Fsd'] * 1800 / 10**6).sum() 
                             for this_date in day_ranges])
new_df['day_Ta_mean'] = np.array([df.loc[this_date[0]:this_date[1], 'Ta'].mean() 
                             for this_date in day_ranges])
new_df['night_Ta_mean'] = np.array([df.loc[this_date[0]:this_date[1], 'Ta'].mean() 
                             for this_date in night_ranges])       
new_df['night_Ts_mean'] = np.array([df.loc[this_date[0]:this_date[1], 'Ts'].mean() 
                             for this_date in night_ranges])                                 
new_df['Sws_mean'] = np.array([df.loc[this_date[0]:this_date[1], 'Sws'].mean() 
                              for this_date in day_ranges])
new_df['night_T_mean'] = (np.array([df.loc[this_date[0]:this_date[1], 'Ta'].mean() 
                                  for this_date in night_ranges]) * 
                          Ta_Ts_ratio[0] + 
                          np.array([df.loc[this_date[0]:this_date[1], 'Ts'].mean() 
                                  for this_date in night_ranges]) *
                          Ta_Ts_ratio[1]) / (Ta_Ts_ratio[0] + Ta_Ts_ratio[1])

new_df['LUE'] = new_df['day_Fc_mean'] / new_df['Fsd_sum']
new_df['LAI'] = modis_df.data.interpolate().rolling(window = 30, center = True).mean()

s_new_df = new_df.dropna()

test_params, test_cov = curve_fit(ramp_func_lin_T_Fsd, 
                                  s_new_df[['Sws_mean', 'night_T_mean', 'day_Fc_mean']], 
                                  s_new_df['night_Fc_mean'], 
                                  p0 = [0, 0.2, 0.1, 0.5, 0.5])
new_df['Modelled_ER_pr'] = ramp_func_lin_T_Fsd(new_df, 
                                               test_params[0], 
                                               test_params[1], 
                                               test_params[2],
                                               test_params[3],
                                               test_params[4])

#lite_params, lite_cov = curve_fit(ramp_func_lin_T, 
#                                  s_new_df[['Sws_mean', 'night_T_mean', 'Fsd_sum']], 
#                                  s_new_df['night_Fc_mean'], 
#                                  p0 = [0, 0.2, 0.5, 0.5])
#new_df['Modelled_ER'] = ramp_func_lin_T(new_df, 
#                                        lite_params[0], 
#                                        lite_params[1], 
#                                        lite_params[2],
#                                        lite_params[3])

#
#
#day_params, day_cov = curve_fit(soil_m_func, 
#                                s_new_df[['Sws_mean', 'Fsd_sum']],
#                                s_new_df['day_Fc_mean'],
#                                p0=[0.05, 0.25, 1])
#
#est = soil_m_func(new_df,
#                  day_params[0],
#                  day_params[1],
#                  day_params[2])

fig = plt.figure(figsize = (12, 12))
fig.patch.set_facecolor('white')
gs = gridspec.GridSpec(2, 1)#, height_ratios=[2,1.5])
ax1 = plt.subplot(gs[0])
ax1.set_ylabel('$NEE\/(\mu mol\/CO_2\/m^{-2}\/s^{-1})$', fontsize = 18)
ax1.xaxis.set_ticks_position('bottom')
ax1.yaxis.set_ticks_position('left')
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.tick_params(axis = 'x', labelsize = 14)
ax1.tick_params(axis = 'y', labelsize = 14)

ax1.plot(dates, 
         new_df.night_Fc_mean.rolling(window = 10, center = True).mean(), 
         color = 'black', lw = 2, label = '$ER_{obs}$')
#ax1.plot(rise_datetimes, new_df.day_Fc_mean, color = 'green')
ax1.plot(dates, 
         new_df.day_Fc_mean.rolling(window = 10, center = True).mean(), 
         color = 'black', lw = 2, ls = ':')
#ax1.plot(dates, new_df.Modelled_ER.rolling(window = 10, center = True).mean(), 
#         color = 'magenta', lw = 2, label = '$ER_{mod}$')
ax1.plot(dates, new_df.Modelled_ER_pr.rolling(window = 10, center = True).mean(), 
         color = 'cyan', lw = 2, label = '$ER_{mod\_pr}$')
ax1.legend(loc = [0.05, 0.16], frameon = False, fontsize = 16)
ax1.axhline(0, color = 'black')

#ax2 = plt.subplot(gs[1])
#ax2.plot(modis_df.index, modis_df.data.interpolate().rolling(window = 30, 
#                                                             center = True).mean())
#ax2.set_ylabel('$T_{air}\/(^oC)\//\/VWC\/(\%)$', fontsize = 18)
#ax2.xaxis.set_ticks_position('bottom')
#ax2.yaxis.set_ticks_position('left')
#ax2.spines['right'].set_visible(False)
#ax2.spines['top'].set_visible(False)
#ax2.tick_params(axis = 'x', labelsize = 14)
#ax2.tick_params(axis = 'y', labelsize = 14)
#ax2.plot(rise_datetimes, new_df.Sws_mean.rolling(window = 10).mean() * 100, 
#         color = 'b', lw = '2', label = '$VWC$')
#ax2.plot(rise_datetimes, new_df.night_T_mean.rolling(window = 10).mean(), 
#         color = 'red', lw = 2, label = '$T_{air}$')
#ax2.legend(loc = [0.05, 0.7], frameon = False, fontsize = 16)         
         
fig.show()