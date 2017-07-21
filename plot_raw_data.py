#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 11:53:18 2017

@author: ian
"""

from scipy.stats import linregress
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import DataIO as io

path='/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/All/GatumPasture_L3.nc'
var_to_plot = 'Fc_CR3'

df = io.OzFluxQCnc_to_data_structure(path, output_structure = 'pandas')

sub_df1 = df.loc['2015', ['Fc_CR3', 'Fc_EP', 'Fc', 'Fc_EP_qc']]
sub_df2 = df.loc['2016', ['Fc_CR3', 'Fc_EP', 'Fc', 'Fc_EP_qc']]

data_list = [sub_df1, sub_df2]

params_2015 = linregress(sub_df1.dropna()[var_to_plot][sub_df1.dropna()['Fc_EP_qc'] == 0], 
                         sub_df1.dropna()['Fc_EP'][sub_df1.dropna()['Fc_EP_qc'] == 0])

params_2016 = linregress(sub_df2.dropna()[var_to_plot][sub_df2.dropna()['Fc_EP_qc'] == 0], 
                         sub_df2.dropna()['Fc_EP'][sub_df2.dropna()['Fc_EP_qc'] == 0])

stats_list = [params_2015, params_2016]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (12, 8))
fig.patch.set_facecolor('white')

i = 0
for ax in (ax1, ax2):
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.spines['top'].set_visible(False)    
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis = 'x', labelsize = 14)
    ax.tick_params(axis = 'y', labelsize = 14)
    ax.set_xlabel('$F_c\_logger\/(\mu molC\/m^2\/s^{-1})$', fontsize = 18)
    if i == 0:
        ax.set_ylabel('$F_c\_EddyPro\/(\mu molC\/m^2\/s^{-1})$', fontsize = 18)
    ax.plot(data_list[i][var_to_plot][data_list[i].Fc_EP_qc==0], 
            data_list[i].Fc_EP[data_list[i].Fc_EP_qc==0],
            color = '0.7',
            ls = '',
            marker = 'o')
    xlims = ax.get_xlim()
    line_x = np.arange(xlims[0], xlims[1] + 1)
    line_y = line_x * stats_list[i].slope + stats_list[i].intercept
    ax.plot(line_x, line_y, color = 'black', ls = '--', lw = 2)
    ax.text(0.1, 0.9, 'y = {0}x + {1}'.format(round(stats_list[i].slope, 2),
                                              round(stats_list[i].intercept, 2)),
            transform = ax.transAxes,
            fontsize = 16)
    i = i + 1