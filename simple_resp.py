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
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def ramp_func_lin_T(df, VWC_lo, VWC_hi, a, b):

    VWC = df.Sws
    T = df[T_name]
    
    VWC_ind = np.where(VWC < VWC_lo, 0, 
                       np.where(VWC > VWC_hi, 1, 
                                (VWC - VWC_lo) / (VWC_hi - VWC_lo)))
    return VWC_ind * a * np.exp(b * T)

def soil_m_func(df, VWC_lo, VWC_hi):

    VWC = df.Sws
    
    VWC_ind = np.where(VWC < VWC_lo, 0, 
                       np.where(VWC > VWC_hi, 1, 
                                (VWC - VWC_lo) / (VWC_hi - VWC_lo)))
                                
    return VWC_ind

def soil_T_func(df, a, b):
    
    T = df[T_name]
    
    return a * np.exp(b * T)
    
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

#df = pd.concat([df1, df2])
df = df1
start_date = dt.datetime(df1.index[0].year, 1, 1)
end_date = dt.datetime(df2.index[-1].year, 3, 31, 23, 30)
new_index = pd.date_range(start_date, end_date, freq='30T')
df = df.reindex(new_index)

path3 = '/home/imchugh/Documents/Gatum/'
name3 = 'MeanCefflux.xlsx'
f_name3 = os.path.join(path3, name3)
df3 = pd.read_excel(f_name3)
df3.index = df3.Date
df3 = df3.loc[:'2015']
df3 = df3.reindex(new_index)

ustar_th = 0.05
T_name = 'Ta'

sub_df = df[df.Fsd < 5]
sub_df.Fc = np.where(sub_df.ustar < ustar_th, np.nan, sub_df.Fc)
daily_mean_df = sub_df.groupby([lambda x: x.year, lambda y: y.dayofyear]).mean()
daily_count_df = sub_df.groupby([lambda x: x.year, lambda y: y.dayofyear]).count()
for var in daily_mean_df.columns:
    daily_mean_df[var][daily_count_df[var] < 5] = np.nan

date_tuples = zip(daily_mean_df.index.get_level_values(0), 
                  daily_mean_df.index.get_level_values(1))
dts = [dt.datetime(i[0], 1, 1) + dt.timedelta(i[1]) for i in date_tuples]
daily_mean_df.index = dts
new_index = pd.date_range(dts[0], dts[-1], freq = 'D')
daily_mean_df = daily_mean_df.reindex(new_index)

s_daily_df = daily_mean_df[['Fc', 'Sws', T_name]].dropna()
#s_daily_df = s_daily_df.loc['2015']

test_params, test_cov = curve_fit(ramp_func_lin_T, 
                                  s_daily_df[['Sws', T_name]], 
                                  s_daily_df['Fc'], 
                                  p0 = [0, 0.2, 0.5, 0.5])
                                  
daily_mean_df['Modelled_ER'] = ramp_func_lin_T(daily_mean_df, 
                                               test_params[0], 
                                               test_params[1], 
                                               test_params[2],
                                               test_params[3]) * 0.0864 * 12

daily_mean_df.Fc = daily_mean_df.Fc * 0.0864 * 12

                             
fig, ax1 = plt.subplots(1, 1, figsize = (12, 8))
fig.patch.set_facecolor('white')

ax1.set_ylabel('$NEE\/(gC\/m^{-2}\/d^{-1})$', fontsize = 18)
ax1.xaxis.set_ticks_position('bottom')
ax1.yaxis.set_ticks_position('left')
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
tick_loc_list = [i for i in daily_mean_df.index if i.day == 1]
tick_lab_list = [dt.datetime.strftime(i, '%Y-%m-%d') for i in tick_loc_list]
ax1.set_xticks(tick_loc_list)
ax1.set_xticklabels(tick_lab_list, rotation = 'vertical', fontsize = 14)
ax1.tick_params(axis = 'y', labelsize = 14)

ax1.plot(daily_mean_df.index, daily_mean_df.Fc.rolling(window = 7, 
                                                       center = True).mean(), 
         lw = 1.5, color = 'black', label = '$Measured\/ER$')         
ax1.plot(daily_mean_df.index, daily_mean_df.Modelled_ER.rolling(window = 7, 
                                                                center = True).mean(), 
         lw = 1.5, color = 'cornflowerblue', label = '$Modelled\/ER$')
ax1.plot(daily_mean_df.index, soil_m_func(daily_mean_df, test_params[0], 
                                          test_params[1]),
         color='Magenta', label = '$f(M)$')
ax1.plot(daily_mean_df.index, soil_T_func(daily_mean_df, 
                                          test_params[2],
                                          test_params[3]).rolling(
                                              window = 7, center = True).mean()
                                              * 0.0864 * 12,
         color='Red', label = '$f(T)$')
ax1.plot(df3.index, df3['Mean C efflux (gC/m2/d)'], marker = '+', mew = 2, 
         ms = 10, mec = 'black', label = '$Chambers$', ls = 'None')

ax1.legend(loc = (0.2, 0.75), frameon = False, numpoints = 1)

plt.tight_layout()
plt.show()

