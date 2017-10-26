#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 14:09:14 2017

@author: ian
"""

# Imports
import numpy as np
import os
import pandas as pd
import xlrd

# Functions
def get_data(fp):

    header_row = [0, 1]
    var_dict = {1: 'Tair', 2: 'Tsoil', 5: 'Solar radn', 8: 'Rel Hum'}    
    book = xlrd.open_workbook(fp)
    sheet = book.sheet_by_name('Sheet1')
    datetimes = sheet.col_values(0, max(header_row) + 1)
    valid_tuple = [(xlrd.xldate_as_datetime(this_datetime, datemode = book.datemode), i) 
                   for i, this_datetime in enumerate(datetimes) if 
                   isinstance(this_datetime, float)]
    datelist, index = zip(*valid_tuple)
    df = pd.DataFrame(index = datelist)
    for i in var_dict:
        df[var_dict[i]] = pd.to_numeric(list(np.array(sheet.col_values(i, max(header_row) + 1))
                                             [np.array(index)]), errors = 'coerce')
    return df

# Initialisations
in_path = '/mnt/fluxdata/Gatum_data/External_data/'
out_path = '/mnt/fluxdata/Gatum_data/External_data/met_concat.csv'

# Main program
f_list = filter(lambda x: 'Logged weather data' in x, os.listdir(in_path))
fp_list = map(lambda x: os.path.join(in_path, x), f_list)
df = pd.concat(map(lambda x: get_data(x), fp_list))
df.sort_index(inplace = True)
df = df[~df.index.duplicated(keep = 'first')] 
new_index = pd.date_range(df.index[0], df.index[-1], freq = '60T')
df = df.reindex(new_index)
df = df.resample('30T').interpolate()
df.to_csv(out_path, index_label = 'Datetime')