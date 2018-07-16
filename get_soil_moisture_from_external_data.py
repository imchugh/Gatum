#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 10:18:40 2017

@author: ian
"""

import pandas as pd
import xlrd


path = '/mnt/fluxdata/Gatum_pasture_data/External_data/Gatum_north.xlsx'
alt_path = '/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/2016/GatumPasture_2016_L1.xls'
header_row = 0

swap_dict = {'Ave_Vol_5cm': 'Sws_5cm',
             'Ave_Vol_15cm': 'Sws_15cm',
             'Ave_Vol_30cm': 'Sws_30cm',
             'T_5cm': 'Ts_5cm',
             'T_15cm': 'Ts_15cm'}

soil_book = xlrd.open_workbook(path)
soil_sheet = soil_book.sheet_by_name('Data')
date_list = map(lambda x: xlrd.xldate_as_datetime(x, datemode=soil_book.datemode), 
                soil_sheet.col_values(0, header_row + 1))
df = pd.DataFrame(index = date_list)
row_names_list = soil_sheet.row_values(header_row)
for var in sorted(swap_dict.keys()):
    idx = row_names_list.index(var)
    df[swap_dict[var]] = pd.to_numeric(soil_sheet.col_values(idx, header_row + 1),
                                       errors = 'coerce')
df = df[~df.index.duplicated(keep = 'first')]    
new_index = pd.date_range(df.index[0], df.index[-1], freq = '60T')
df = df.reindex(new_index)
df = df.resample('30T').interpolate()

