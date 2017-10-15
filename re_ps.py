#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 12:51:46 2016

@author: imchugh
"""
import pdb
import copy as cp
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import math
import pandas as pd
from scipy.stats import linregress

import DataIO as io
import data_formatting as dt_fm
import data_filtering as filt
import respiration_H2O as re
import photosynthesis as ps
import random_error as rand_err

###############################################################################
# Function to get data

def get_data(configs_dict, use_storage = True):
    
    data_file = configs_dict['files']['in_file']
    var_list = configs_dict['variables'].values()
    data_dict, attr = io.OzFluxQCnc_to_data_structure(data_file, 
                                                      var_list = var_list, 
                                                      QC_var_list = ['Fc'], 
                                                      return_global_attr = True)
    configs_dict['options']['measurement_interval'] = int(attr['time_step'])

    names_dict = dt_fm.get_standard_names(convert_dict = configs_dict['variables'])
    data_dict = dt_fm.rename_data_dict_vars(data_dict, names_dict)
    
    return data_dict    

###############################################################################
# Constants

config_file = '/home/ian/Code/Python/Config_files/Gatum_master_configs.txt'

##############################################################################
# Do respiration

re_configs_dict = io.build_algorithm_configs_dict(config_file_location = 
                                                      config_file, 
                                                  algorithm = 
                                                      'respiration_configs')

re_data_dict = get_data(re_configs_dict)

filt.screen_low_ustar(re_data_dict, re_configs_dict['options']['ustar_threshold'],
                      re_configs_dict['options']['noct_threshold'])

re_rslt_dict, re_params_dict, re_error_dict = re.main(re_data_dict, 
                                                      re_configs_dict['options'])

###############################################################################
# Do photosynthesis

ps_configs_dict = io.build_algorithm_configs_dict(config_file_location = 
                                                       config_file, 
                                                  algorithm = 
                                                       'photosynthesis_configs')

ps_data_dict = get_data(ps_configs_dict)

ps_data_dict['PAR'] = ps_data_dict['Fsd'] * 0.46 * 4.6

new_params_dict = cp.deepcopy(re_params_dict)

ps_rslt_dict, ps_params_dict, ps_error_dict = ps.main(ps_data_dict, 
                                                      ps_configs_dict['options'], 
                                                      new_params_dict)

##############################################################################

df = pd.DataFrame(re_data_dict)
df.index = df['date_time']
df['Re'] = re_rslt_dict['Re']
new_df = df.groupby(lambda x: x.dayofyear).mean()
new_df.index = [dt.date(2015, 1, 1) + dt.timedelta(i - 1) for i in new_df.index]
new_index = pd.date_range(re_params_dict['date'][0], 
                          re_params_dict['date'][-1],
                          freq = 'D')
new_df = new_df.reindex(new_index)
new_df['scalar'] = 1 / (1 + np.exp(re_params_dict['theta1'] - 
                                   re_params_dict['theta2'] * new_df.Sws))

night_df = cp.deepcopy(df)
night_df = night_df[night_df.Fsd < 5]
night_df = night_df[['NEE_series', 'Re']]
re_df = night_df.groupby(lambda x: x.dayofyear).mean()
