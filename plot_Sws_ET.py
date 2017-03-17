#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 08:44:00 2017

@author: ian
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import DataIO as io

path = ('/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/2016/'
       'GatumPasture_2016_L4.nc')

df = io.OzFluxQCnc_to_data_structure(path,
                                      var_list = ['Sws', 'Fe', 'Fsd', 'VPD', 
                                                  'Fn'],
                                      output_structure = 'pandas')

# Drop nocturnal and missing data
df = df[df.Fsd > 5]
#df.drop('Fsd', axis = 1, inplace = True)
df.dropna(inplace = True)
df['ET'] = df.Fe * 86.4 / 2260
  
df['VPD_cat'] = pd.qcut(df.VPD, 30, labels = np.linspace(1, 30, 30))
vpd_df = df.groupby(df.VPD_cat).mean()
sws_df = df.groupby('Sws').mean()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (12, 12))
fig.patch.set_facecolor('white')
ax1.xaxis.set_ticks_position('bottom')
ax1.spines['top'].set_visible(False)
ax1.tick_params(axis = 'x', labelsize = 14)
ax1.tick_params(axis = 'y', labelsize = 14)
ax1.set_xlabel('$Sws\/\/(m^3\/m^{-3})$', fontsize = 18)
ax1.set_ylabel('$EF\/\/(F_e\//F_n)$', fontsize = 18)

ax1b = ax1.twinx()
ax1b.spines['top'].set_visible(False)
ax1b.tick_params(axis = 'y', labelsize = 14)
ax1b.set_ylabel('$VPD\/\/(kPa)$', fontsize = 18)

ax2.xaxis.set_ticks_position('bottom')
ax2.spines['top'].set_visible(False)
ax2.tick_params(axis = 'x', labelsize = 14)
ax2.tick_params(axis = 'y', labelsize = 14)
ax2.set_xlabel('$VPD\/\/(kPa)$', fontsize = 18)
ax2.set_ylabel('$EF\/\/(F_e\//F_n)$', fontsize = 18)

ax2b = ax2.twinx()
ax2b.spines['top'].set_visible(False)
ax2b.tick_params(axis = 'y', labelsize = 14)
ax2b.set_ylabel('$Sws\/\/(m^3\/m^{-3})$', fontsize = 18)

ser_1 = ax1.plot(sws_df.index, sws_df.Fe / sws_df.Fn, 
                 label = 'EF', lw = 2, color = 'black')
ser_1b = ax1b.plot(sws_df.index, sws_df.VPD, 
                   label = 'VPD', ls = ':', lw = 2, color = 'black')
a1_ser = ser_1 + ser_1b
labs = [ser.get_label() for ser in a1_ser]
ax1.legend(a1_ser, labs, frameon = False, fontsize = 18, loc = [0.8, 0.2])

ser_2 = ax2.plot(vpd_df.VPD, vpd_df.Fe / vpd_df.Fn * 1800 / 2260, 
                 label = 'EF', lw = 2, color = 'black')
ser_2b = ax2b.plot(vpd_df.VPD, vpd_df.Sws, 
                   label = 'Sws', ls = ':', lw = 2, color = 'black')
a2_ser = ser_2 + ser_2b
labs = [ser.get_label() for ser in a2_ser]
ax2.legend(a2_ser, labs, frameon = False, fontsize = 18, loc = [0.8, 0.2])
