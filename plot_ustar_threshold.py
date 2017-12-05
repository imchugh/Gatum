#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 14:45:41 2017

@author: ian
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import DataIO as io

path='/media/ian/STORE N GO/RockyMouth_2015_16_L3.nc'
#path = '/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/All/GatumPasture_L3.nc'
num_cats = 50

df = io.OzFluxQCnc_to_data_structure(path, output_structure='pandas')

noct_df = df.loc[df.Fsd < 20]


noct_df['ustar_cat'] = pd.qcut(df.ustar, num_cats, 
                               labels = np.linspace(1, num_cats, num_cats))

means_df = noct_df.groupby('ustar_cat').mean()

fig, ax = plt.subplots(1, figsize = (12, 8))
fig.patch.set_facecolor('white')
ax.set_ylabel(r'$R_e\/(\mu mol\/m^{-2}\/s^{-1})$', fontsize = 22)
ax.set_xlabel('$u_{*}\/(m\/s^{-1})$', fontsize = 22)
ax.tick_params(axis = 'x', labelsize = 14)
ax.tick_params(axis = 'y', labelsize = 14)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')    
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
#ax.axvline(0.1275, color = 'black')
ax.plot(means_df.ustar, means_df.Fc, marker = 'o', mfc = '0.5', color = '0.5')
