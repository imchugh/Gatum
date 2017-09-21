#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 10:56:46 2017

@author: ian
"""

import os
    
def check_ok(fname):
    if not 'ts_data' in fname: return False
    return True if len(fname.split('_')) == 8 else False

def rebuild_name(fname):
    fname_list = fname.split('_')
    return '_'.join(fname_list[:3] + fname_list[4:])

path = '/mnt/fluxdata/Gatum_data/2_Converted/C_2017-08-03_Pasture'

files = filter(lambda x: os.path.isfile, os.listdir(path))
ok_list = filter(check_ok, files)
old_names = map(lambda x: os.path.join(path, x), ok_list)
new_names = map(lambda x: os.path.join(path, rebuild_name(x)), ok_list)
names_swap_pairs = zip(old_names, new_names)
for this_pair in names_swap_pairs:
    os.rename(this_pair[0], this_pair[1])