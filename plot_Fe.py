#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 15:03:51 2017

@author: ian
"""

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import pandas as pd
from scipy.stats import linregress

import DataIO as io

# Get data
f = '/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/All/GatumPasture_L3.nc'
df = io.OzFluxQCnc_to_data_structure(f, output_structure='pandas')
sub_df = df[['Fe_CR3', 'Fe_EP']].dropna()

# Do stats
res = linregress(sub_df.Fe_CR3, sub_df.Fe_EP)
x_line = np.linspace(-100, 400, 11)
y_line = x_line * res.slope + res.intercept

# Plot it
font = FontProperties()
font.set_family('sans serif')
font.set_style('italic')
fig, ax = plt.subplots(1, 1, figsize = (12, 8))
fig.patch.set_facecolor('white')
ax.set_xlim([-100, 400])
ax.set_ylim([-100, 400])
ax.set_xlabel('F$_e\__{CR3}$ (W m$^{-2}$)', fontsize = 18, fontproperties = font)
ax.set_ylabel('F$_e\__{EP}$ (W m$^{-2}$)', fontsize = 18, fontproperties = font)
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.tick_params(axis = 'x', labelsize = 14)
ax.tick_params(axis = 'y', labelsize = 14)
ax.plot(sub_df.Fe_CR3, sub_df.Fe_EP, marker = 'o', color = '0.5', ms = 3, 
        ls = '')
ax.plot(x_line, y_line, color = 'black')
txt = 'y = {0}x + {1} (r$^2$ = {2})'.format(str(round(res.slope, 2)), 
                                            str(round(res.intercept, 2)),
                                            str(round(res.rvalue ** 2, 2)))
ax.text(-50, 400, txt, fontsize = 18, fontproperties = font, 
        horizontalalignment = 'left', verticalalignment = 'center')