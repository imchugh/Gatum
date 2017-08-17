#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 11:46:46 2017

@author: ian
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import datetime as dt
import numpy as np

import DataIO as io


path='/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/All/GatumPasture_L3.nc'

df = io.OzFluxQCnc_to_data_structure(path, output_structure='pandas')
df['T_rad'] = (df.Flu / (5.67 * 10**-8)) ** (1/4.0) - 273.15

T_list = ['Ts_10cma', 'Ts_10cmb', 'Ta', 'Ta_GF', 'Ts_GF', 'T_rad']

daily_df = (df[T_list].groupby([lambda x: x.year, lambda y: y.dayofyear]).mean())
daily_df.index = [dt.datetime(i[0], 1, 1) + dt.timedelta(i[1]) 
                 for i in daily_df.index]

diel_df = (df[T_list].groupby([lambda x: x.hour, lambda y: y.minute]).mean())
diel_df.index = np.arange(48) / 2.0
diel_df.dropna(inplace = True)


fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (16, 8))
fig.patch.set_facecolor('white')
ax1.plot(df.index, df.Ta, label = 'Air')
ax1.plot(df.index, df.T_rad, label = 'Surface')

ax2.plot(df.T_rad, df.Ta, marker = 'o', color = '0.7', ms = 2, ls = '')
