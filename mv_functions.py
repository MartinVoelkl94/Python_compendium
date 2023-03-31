#this file was created from mv_functions.ipynb using nbconvert
#!/usr/bin/env python
# coding: utf-8

# contains utility functions.
# 
# mv_functions.ipynb is meant to be used for looking up, editing or adding functions while mv_functions.py is used to import functions to other scripts or notebooks (use 'import mv_functions as mv').
# 
# The last cell of mv_functions.ipynb contains code that backs up the current mv_functions.py file and converts mv_functions.ipynb into a new mv_functions.py.

# In[1]:


import numpy as np
import pandas as pd
import types
import time
import shutil
import os
import sys
import datetime
from google.colab import drive


# In[2]:


#this part is not meant to be executed after conversion to a .py file
if 'colab' in get_ipython().config['IPKernelApp']['kernel_class']:
    # mounting to drive folder
    from google.colab import drive
    drive.mount('/content/drive')

    #acces functions from mv_functions.py
    sys.path.append('/content/drive/MyDrive/coding/Python/Compendium')
    os.chdir('/content/drive/MyDrive/coding/Python/Compendium')
    import mv_functions as mv


# In[ ]:


def tree(data, name='data', indent='|   '):
    """
    gives a condensed overview of the content of an object in a form resembling
    a folder tree. Made to be used in data exploration or when investigating a 
    new algorithm. It has similar usecases as the basic type() function but in 
    addition it also gives more information on certain common data types an is
    able to show multiple layers of nested objects.

    Parameters:
    data: an object identifiable ny type()
    name: optional. the name of the current object
    indent: used to modify visual presentation of the output

    Returns:
    prints to output instead of returning
    """
    name = [name]
    level = 0
    _tree_check_type(data, name, level, indent)   
    
def _tree_check_type(current_data, name, level, indent):
    #used by tree function function to check the type of current_data

    indents = level*indent
    current_data_name = ''.join(name)
    
    if isinstance(current_data, list):
        if level == 0:
            print(f'{indents}list:')
        else:
            print(f'{indents}list: {current_data_name}')
        level += 1
        _tree_open_list(current_data, name, level, indent)

    elif isinstance(current_data, dict):
        if level == 0:
            print(f'{indents}dictionary:')
        else:
            print(f'{indents}dictionary: {current_data_name}')
        level += 1
        _tree_open_dict(current_data, name, level, indent)

    elif isinstance(current_data, np.ndarray):
        if level == 0:
            print(f'{indents}np.ndarray:')
        else:
            print(f'{indents}np.ndarray: {current_data_name}')
        level += 1
        _tree_open_np_ndarray(current_data, name, level, indent)
    
    elif isinstance(current_data, pd.core.frame.DataFrame):
        if level == 0:
            print(f'{indents}dataframe:')
        else:
            print(f'{indents}dataframe: {current_data_name}')
        level += 1
        _tree_open_pd_dataframe(current_data, name, level, indent)
    
    else:
        print(f'{indents}{str(type(current_data))[8:-2]}')


def _tree_open_list(current_data, name, level, indent):
    #used by tree function function to open dictionaries

    counter = {}
    for ind in range(len(current_data)):
        if str(type(current_data[ind]))[8:-2] in counter.keys():
            counter[str(type(current_data[ind]))[8:-2]] += 1
        else:
            counter[str(type(current_data[ind]))[8:-2]] = 1
    
    for key in counter.keys():
        print(f'{level*indent}{key}: {counter[key]} times')


def _tree_open_dict(current_data, name, level, indent):
    #used by tree function to open dictionaries

    for key in current_data.keys():
        if isinstance(key, str):
            name.append(f'["{key}"]')
        else:
            name.append(f'[{str(key)}]')
        _tree_check_type(current_data[key], name, level, indent)
        name.pop()


def _tree_open_np_ndarray(current_data, name, level, indent):
    #used by tree function to open numpy ndarrays

    current_data_name = ''.join(name)
    
    if current_data.shape[0] == 1:
        cols = f'[0,0:{len(current_data[0,:])}]'
        print(f'{level*indent}1 col: {current_data_name}[0,:]')
        print(f'{level*indent}{len(current_data[0,:])} rows: {current_data_name}{cols}')
        
    elif current_data.shape[0] >= 2:
        rows = f'[0:{len(current_data[:,0])},:]'
        print(f'{level*indent}{len(current_data[:,0])} rows: {current_data_name}{rows}')
        
        cols = f'[:,0:{len(current_data[0,:])}]'
        print(f'{level*indent}{len(current_data[0,:])} cols: {current_data_name}{cols}')
        
    else:
        print(f'{level*indent}shape: {current_data.shape}')


def _tree_open_pd_dataframe(current_data, name, level, indent):
    #used by tree function to open pandas dataframes

    for colname in list(current_data):
        current_data_name = ''.join(name)
        n_values = len(current_data[colname])
        if isinstance(colname, str):
            print(f'{level*indent}{n_values} values in:{current_data_name}["{colname}"]')
        else:
            print(f'{level*indent}{n_values} values in: {current_data_name}[{colname}]')


# In[ ]:
