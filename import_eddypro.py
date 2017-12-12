#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 13:11:07 2017

@author: ian
"""

import pandas as pd
import datetime as dt
import numpy as np

path = ('/mnt/fluxdata/Gatum_data/EddyPro/Output/20171017/'
        'eddypro_01_full_output_2017-11-23T134702_adv.csv')

df = pd.read_csv(path, skiprows = [0, 2])

df.index = map(lambda x: dt.datetime.strptime(' '.join(x), '%Y-%m-%d %H:%M'), 
               zip(df.date, df.time))
df = df.reindex(pd.date_range(df.index[0], df.index[-1], freq = '30T'))
df.loc[(df.co2_flux >20) | (df.co2_flux <-20), 'co2_flux'] = np.nan
df.loc[:, 'co2_flux'] = df.loc[:, 'co2_flux'] * 0.044

df.to_csv('/home/ian/Desktop/test.csv')