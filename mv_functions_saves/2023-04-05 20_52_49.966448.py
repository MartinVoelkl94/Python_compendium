#this file was created from mv_functions.ipynb using nbconvert
#!/usr/bin/env python
# coding: utf-8

# contains utility functions.
# 
# mv_functions.ipynb is meant to be used for looking up, editing or adding functions while mv_functions.py is used to import functions to other scripts or notebooks (use 'import mv_functions as mv').
# 
# The last cell of mv_functions.ipynb contains code that backs up the current mv_functions.py file and converts mv_functions.ipynb into a new mv_functions.py.

# In[4]:


import numpy as np
import pandas as pd
import types
import time
import shutil
import os
import sys
import pickle
import datetime
from google.colab import drive


# In[ ]:


#this part is not meant to be executed after conversion to a .py file
if 'colab' in get_ipython().config['IPKernelApp']['kernel_class']:
    # mounting to drive folder
    from google.colab import drive
    drive.mount('/content/drive')

    #acces functions from mv_functions.py
    sys.path.append('/content/drive/MyDrive/coding/Python/Compendium')
    os.chdir('/content/drive/MyDrive/coding/Python/Compendium')
    import mv_functions as mv


# In[73]:


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
    level = 0  #tracks progress through layers of nested objects
    _tree_check_type(data, name, level, indent)   
    

def _tree_check_type(current_data, name, level, indent):
    #used by tree function to check the type of current_data

    indents = level*indent
    current_data_name = ''.join(name)
    
    #the following if-statements check for common data types and then go a
    #level deeper when encountering a list, dict, array or dataframe
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
    #used by tree function to open and display contents of lists.

    counter = {}
    for ind in range(len(current_data)):
        if str(type(current_data[ind]))[8:-2] in counter.keys():
            counter[str(type(current_data[ind]))[8:-2]] += 1
        else:
            counter[str(type(current_data[ind]))[8:-2]] = 1
    
    for key in counter.keys():
        print(f'{level*indent}{key}: {counter[key]} times')


def _tree_open_dict(current_data, name, level, indent):
    #used by tree function to open and display contents of dictionaries.

    for key in current_data.keys():
        if isinstance(key, str):
            name.append(f'["{key}"]')
        else:
            name.append(f'[{str(key)}]')
        _tree_check_type(current_data[key], name, level, indent)
        name.pop()


def _tree_open_np_ndarray(current_data, name, level, indent):
    #used by tree function to open and display contents of numpy arrays.

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
    #used by tree function to open and display contents of pandas dataframes.

    for colname in list(current_data):
        current_data_name = ''.join(name)
        n_values = len(current_data[colname])
        if isinstance(colname, str):
            print(f'{level*indent}{n_values} values in:{current_data_name}["{colname}"]')
        else:
            print(f'{level*indent}{n_values} values in: {current_data_name}[{colname}]')


# In[74]:


def save(data, path=None, readme='no readme found',
         supp={}, overwrite=False, verbose=True):
    """
    Makes working with various objects a little faster and more convenient.
    Not meant for use in production ready code. Saves any type of python object
    thats compatible with the pickle library as a file while offering some
    additional convenience:
        -one function for all data types
        -therefore can be used when type of output is unknown beforehand
        -option to include a readme string to explain the data
        -option to include additional supplementary data
        -if chosen or default (data0.pkl) filename already exists it increments
            the number in the filename instead of overwriting the old file

    Parameters:
    data: any object compatible with the pickle library.
    path: optional. filename or filepath to save the data as. if none is
        provided, the data is saved in the current folder as data0.pkl.
        if the chosen or default name is already taken, ascending numbers
        (up to 1000) are added until the name is valid. its not necessary
        (but possible) to add the '.pkl' extension when calling the function.
    readme: optional. a string that can be saved with the data, for example
        to explain where the data came from or how it was generated.
        when loading the data   with the corresponding function mv.load the
        string can be recalled.
    supp: optional. a dictionary containing any additional object/s to be saved
        together with the main data, for example the source of the data or the
        code that produced it.
    overwrite: whether or not existing files should be overwritten if they
        have the same name as the one chosen for the data to save.
    verbose: if confirmation and location of the saved file should be printed
    """

    if path == None: #neither directory nor filename provided
        filename = 'data'
        directory = os.getcwd()

    elif '/' in path:  #directory provided
        directory = '/'.join(path.split('/')[:-1])
        if path.split('/')[-1] == '':  #directory provided but no filename
            filename = 'data'
        else:  #directory and filename provided
            filename = path.split('/')[-1]

    else:  #filename provided but no directory
        directory = os.getcwd()
        filename = path

    #cut of extension (if one is given)
    filename = filename.split('.')[0]

    #put data, readme and supplements into dictionary
    save_dict = {'data': data, 'readme': readme, 'supplementary': supp}

    #set path to save data in ignoring existing files with that name
    if overwrite == True:
        save_path = f'{directory}/{filename}.pkl'
    #increment filenumber as to not overwrite existing files instead
    else:
        existing_filenames = os.listdir(directory)
        for i in range(1000):
            save_name = f'{filename}{str(i)}.pkl'
            if save_name not in existing_filenames:
                save_path = f'{directory}/{save_name}'
                break

    #save data
    with open(save_path, 'wb') as file:
        pickle.dump(save_dict, file)
        if verbose:
            print('data saved in: ', save_path)



def load(path='data0', readme=False, supp=False, verbose=False):
    """
    loads objects saved with mv.save.

    Parameters:
    path: optional. filename or filepath of the object to load. if non is given,
        the default path of mv.save (data0.pkl) is used.
    readme: wether to load the readme string saved with the object
    supp: wether to load the dictionary of supplements saved with the object
    verbose: switches 'commentary' on or off
    """
    
    if '.pkl' not in path and '.pckl' not in path:
        path = f'{path}.pkl'

    with open(path, 'rb') as file:
        save_dict = pickle.load(file)
        
    if readme:
        print('readme:\n', save_dict['readme'])
        
    if supp:
        if verbose:
            print('supplementary information loaded from: ', path)
        return(save_dict['supplementary'])
    else:
        if verbose:
            print('data without supplementary information loaded from: ', path)
        return(save_dict['data'])


# In[ ]:
