#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 15:09:48 2017

@author: ian
"""

import datetime as dt
import pandas as pd
import numpy as np

import modis_functions as mf
reload(mf)

lat = -37.386853
lon = 142.003519
alt = 300
GMT_zone = 10
Ta_Ts_ratio = [5,1]
modis_prod = 'MCD15A2H'
modis_data_band = 'Lai_500m'
modis_QC_band = 'FparLai_QC'

# Get modis LAI data
modis_start = dt.datetime(2015,2,9).date()
modis_end = dt.datetime(2017,6,1).date()
modis_dict = mf.get_MODIS_subset(lat, lon, modis_prod, modis_data_band,
                                 modis_QC_band, 
                                 requestStart = modis_start,
                                 requestEnd = modis_end)
modis_df = pd.DataFrame(modis_dict)
modis_df.index = modis_df.date
modis_df['QC_int'] = np.array([int(i, 2) for i in modis_dict['QC']])
modis_df['data'][modis_df['QC_int'] <> 0] = np.nan
