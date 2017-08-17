# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:38:02 2016

@author: imchugh
"""
import os
import pandas as pd
import datetime as dt
import numpy as np
import pdb
from scipy.optimize import curve_fit

import DataIO as io
import datetime_functions as dtf

def LRF_2 (data_d, alpha, beta, theta, gamma_0, gamma_1):
    NEE = (1 / (2 * theta) * (alpha * data_d['PAR'] + beta - 
                              np.sqrt((alpha * data_d['PAR'] + beta) ** 2 -
                                      4 * alpha * beta * theta * data_d['PAR'])) -
           gamma_0 * np.exp(data_d['Ts'] * gamma_1))

    return NEE
    
   
def LRF(data_d, alpha, beta, gamma):
    NEE = ((alpha * data_d['PAR']) / (1 - (data_d['PAR'] / 2000) + 
                                     (alpha * data_d['PAR'] / beta)) + 
           gamma) #ER_1 * np.exp(data_d['PAR'] * ER_2))

    return NEE

ustar_threshold = 0.1
noct_threshold = 10

path1 = '/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/2015/'
name1 = 'GatumPasture_2015_L4.nc'
f_name1 = os.path.join(path1, name1)
df1 = io.OzFluxQCnc_to_data_structure(f_name1, 
                                      var_list=['Fc', 'Ta', 'Ts', 'Fsd', 'Sws', 
                                                'ustar'], 
                                      output_structure='pandas')

path2 = '/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/2016/'
name2 = 'GatumPasture_2016_L4.nc'
f_name2 = os.path.join(path2, name2)
df2 = io.OzFluxQCnc_to_data_structure(f_name2, 
                                      var_list=['Fc', 'Ta', 'Ts', 'Fsd', 'Sws', 
                                                'ustar'],
                                      output_structure='pandas')
df2.Fc = df2.Fc * 1000 / 44
df = pd.concat([df1, df2])
#df = df1
start_date = dt.datetime(df1.index[0].year, 1, 1)
end_date = dt.datetime(df2.index[-1].year, 3, 31, 23, 30)
new_index = pd.date_range(start_date, end_date, freq='30T')
df = df.reindex(new_index)

data_dict = {this_col: np.array(df[this_col]) for this_col in df.columns}
data_dict['date_time'] = np.array([dt.datetime(this_date.year, this_date.month, 
                                   this_date.day, this_date.hour, 
                                   this_date.minute) for this_date in df.index])

data_dict['PAR'] = data_dict['Fsd'] * 0.46 * 4.6

window_dict = dtf.get_moving_window(data_dict, 'date_time', 3, 1)

sorted_datetime = window_dict.keys()
sorted_datetime.sort()

vars_list = [var for var in data_dict.keys() if not var == 'date_time']
alpha_list = []
beta_list = []
gamma_list = []
dates_list = []
theta_list = []
Amax_list = []
gamma0_list = []
gamma1_list = []

dummy_arr = np.empty(len(sorted_datetime))
dummy_arr[:] = np.nan
params_list = ['alpha', 'beta', 'gamma']
results_dict = {var: dummy_arr.copy() for var in params_list}
for i, datetime in enumerate(sorted_datetime):
    
    this_dict = window_dict[datetime]

    total_recs = len(this_dict['Fc'])    
    nan_list = []
    for var in vars_list:
        nan_list.append(~np.isnan(this_dict[var]))
    nan_list.append(np.array(this_dict['ustar'] > ustar_threshold))
    nan_list.append(np.array(this_dict['Fsd'] > noct_threshold))
    all_nan_array = np.tile(True, len(this_dict[var]))
    for l in nan_list:
        all_nan_array = all_nan_array & l
    avail_recs = len(l[l])
    pct_avail_recs = np.round(float(avail_recs) / total_recs * 100, 1)
    if pct_avail_recs > 20:
        driver_dict = {var: this_dict[var][l] for var in ['PAR', 'Ts']}
        response_arr = this_dict['Fc'][l]
        p0 = [-0.1, -10, 1]
        try:
            params, cov = curve_fit(LRF, driver_dict, response_arr, 
                                    p0 = p0)
        except Exception, e:
            print 'Fail!'
            continue
        if params[1] > 100 or params[1] < -100 or np.all(p0==np.array(params)):
            print 'Aaaaargggghhhh!'
        else:
            for j, var in enumerate(params_list):
                results_dict[var][i] = params[j]

#        try:
#            params, cov = curve_fit(LRF_2, driver_dict, response_arr * -1, 
#                                    p0 = [0.01, 10, 1, 1, 1])
#        except Exception, e:
#            print e
#            continue
#
#        if not params[1] > 100:
#            alpha_list.append(params[0])
#            beta_list.append(params[1])
#            theta_list.append(params[2])
#            gamma0_list.append(params[3])
#            gamma1_list.append(params[4])
#            dates_list.append(datetime)
            
    print ('For {0}, {1}% of all records were available'
           .format(dt.datetime.strftime(datetime, '%Y-%m-%d'), 
                   str(pct_avail_recs)))

sub_df = df.loc['2015-06-30':'2015-08-30']
sub_df['PAR'] = sub_df.Fsd * 4.6 * 0.46
sub_df.dropna(inplace=True)

#params, cov = curve_fit(LRF_2, sub_df, sub_df['Fc'] * -1, 
#                        p0 = [0.01, 10, 1, 1, 1])  
    
    