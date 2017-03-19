#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 17:39:19 2017

@author: ian
"""

import numpy as np

import DataIO as io

path = ('/home/ian/OzFlux/Sites/GatumPasture/Data/Processed/2016/'
       'GatumPasture_2016_L4.nc')

# Constants
Cp = 1.013
Lv = 2.45
eps = 0.622
P = 100
T = 20

# Parameters (known)
psych_const = Cp * P / (eps * Lv) * 10**-3
delta_es = 4098 * (0.6108 * np.exp(17.27 * T / (T + 237.3))) / (T + 237.3)**2
                       
df = io.OzFluxQCnc_to_data_structure(path, output_structure = 'pandas')
                       
print psych_const
print delta_es