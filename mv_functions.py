#this file was created from mv_functions.ipynb using nbconvert
#!/usr/bin/env python
# coding: utf-8

# contains utility functions.
# 
# mv_functions.ipynb is meant to be used for looking up, editing or adding functions while mv_functions.py is used to import functions to other scripts or notebooks.
# 
# The last cell of mv_functions.ipynb contains code that backs up the current mv_functions.py file and converts mv_functions.ipynb into a new mv_functions.py.
# 
# To avoid namespace conflicts due to some of the function names beeing rather generic, i recommend using:
# 
# ```python
# import mv_functions as mv
# 
# data = [1,2,3]
# mv.save(data)
# ```
# 
# instead of:
# ```python
# from mv_functions import save
# 
# data = [1,2,3]
# save(data)
# ```

# # packages

# In[11]:


import numpy as np
import pandas as pd
import random
import types
import time
import datetime

import os
import sys
import shutil
import pickle


#this part is not meant to be executed after conversion to a .py file
if 'colab' in get_ipython().config['IPKernelApp']['kernel_class']:
    # mounting to drive folder
    from google.colab import drive
    drive.mount('/content/drive')

    #acces functions from mv_functions.py
    sys.path.append('/content/drive/MyDrive/coding/Python/Compendium')
    os.chdir('/content/drive/MyDrive/coding/Python/Compendium')
    import mv_functions as mv


# # mv.tree

# In[ ]:


def tree(data, name='data', indent='|   '):
    """
    gives a condensed overview of the content of an object in a form resembling
    a folder tree. Made to be used in data exploration or when investigating 
    outputs generated by unknown code. It has similar usecases as the basic
    type() function but in addition it also gives more information on certain
    common data types and is able to show multiple layers of nested objects.

    Parameters:
    data: an object identifiable by type()
    name: optional. the name of the current object
    indent: used to modify visual presentation of the output

    Returns:
    no return value. prints visualization of object structure to output instead
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
            print(f'{level*indent}{n_values} values in: {current_data_name}["{colname}"]')
        else:
            print(f'{level*indent}{n_values} values in: {current_data_name}[{colname}]')


# # mv.save

# In[ ]:


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
        -if chosen or default (data.pkl) filename already exists it increments
            the number in the filename instead of overwriting the old file

    Parameters:
    data: any object compatible with the pickle library.
    path: optional. filename or filepath to save the data as. if none is
        provided, the data is saved in the current folder as data.pkl.
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

    Returns:
    no return value. prints location of saved data unless verbose=False
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

    #cut off extension (if one is given)
    filename = filename.split('.')[0]

    #combine directory and filename:
    save_path = f'{directory}/{filename}.pkl'

    #put data, readme and supplements into dictionary
    save_dict = {'data': data, 'readme': readme, 'supplementary': supp}


    #if filename doesnt exist or should be overwritten:
    if not os.path.exists(save_path) or overwrite == True:
        pass
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


# # mv.load

# In[ ]:


def load(path='data', readme=False, supp=False, verbose=False):
    """
    loads objects saved with mv.save.

    Parameters:
    path: optional. filename or filepath of the object to load. if non is given,
        the default path of 'data.pkl' is used.
    readme: wether to load the readme string saved with the object
    supp: wether to load any additional supplements saved with the object
    verbose: switches 'commentary' on or off

    Returns:
    returns one of 3 things related to the loaded data.
        - the data itself
        - a readme file (if one was saved with the data)
        - supplementary data (if it was saved with the data)
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


# # mv.samples

# In[ ]:


def samples(dirname='samples'):
    """
    creates a folder with sample files in various formats for use in
    Python_compendium.ipynb or for testing functions.

    Returns:
    no return value. prints type and location of created data.
    """
    if os.path.exists(dirname):
        print(f'folder "{dirname}" found')
    else:
        os.mkdir(dirname)
        print(f'created folder "{dirname}"')
        


    #list as .txt
    list1 = [f'random number: {random.randint(0, 100)}' for x in range(20)]

    with open(f'{dirname}/list.txt', 'w') as file:
        for line in list1:
            file.write(f'{line}\n')
        print(f'created file "{dirname}/list.txt"')



    #numpy arrays as .npy, .txt, .csv
    numpy_array = np.array([[x*y for x in range(5)] for y in range(6)])

    np.save(f'{dirname}/array.npy', numpy_array)
    print(f'created file "{dirname}/array.npy"')
    np.savetxt(f'{dirname}/array.txt', numpy_array, delimiter=',')
    print(f'created file "{dirname}/array.txt"')
    np.savetxt(f'{dirname}/array.csv', numpy_array, delimiter=',')
    print(f'created file "{dirname}/array.csv"')



    #pandas dataframes as .csv, .xlsx
    df = pd.DataFrame([(1, 2.0, 'Hello', True), (2, 3.0, 'World', False)],
                    index=['A', 'B'],
                    columns=[1, 2, 3, 4])

    df.to_csv(f'{dirname}/df.csv', index=True)
    print(f'created file "{dirname}/df.csv"')
    df.to_excel(f'{dirname}/df.xlsx', index=True)
    print(f'created file "{dirname}/df.xlsx"')



    #dictionary as .pkl
    dict1 = {'name': 'Herbert', 'age': 22, 'height': 172}

    with open(f'{dirname}/dict.pkl', 'wb') as file:
            pickle.dump(dict1, file)
            print(f'created file "{dirname}/dict.pkl"')



    #nested object as .pkl
    integer = 1
    boolean = True
    dict1 = {'name': 'Herbert', 'age': 22, 'height': 172, 1: 'id'}
    list1 = [0, 1, 2, 'abc']
    list2 = [[0,1,2], ['a', 'b'], [True, True, False], 0, 0.2, 'a', True, dict1]
    array1 = [(1, 2.0, 'Hello'), (2, 3.0, 'World')]
    array2 = np.array(array1)
    dict2 = {'id': 'a5', 'contents': list2, 'date': 2021}
    df1 = pd.DataFrame(array1, index=['X', 'Y'], columns=['A', 'B', 3])

    nested = {'int': integer, 'boolean': boolean, 'dict1': dict1,
            'dict2': dict2, 'list1': list1,'list2': list2,
            'array': array1, 'array2': array2, 'dataframe': df1}

    with open(f'{dirname}/nested.pkl', 'wb') as file:
            pickle.dump(nested, file)
            print(f'created file "{dirname}/nested.pkl"')


# # mv.clean

# In[25]:


def clean(path=None, timespan=10, delete=False, bin_dir='bin', names=False,
        extensions=['.py', '.txt', '.csv', '.xlsx', '.npy', '.pkl']):
    """
    looks in current working directory (default) or any given filepath for any
    files modified within a specified timespan (default 10s) and puts them in
    a trashbin folder. If delete is set to True it will delete the folder.
    In default mode it only deletes files with the extensions .py, .txt, .csv,
    .xlsx, .npy, .pkl.

    Returns:
    returns list with names of moved/deleted files if names=True.
    prints location of trashbin folder, and if it was deleted.
    """

    now = time.time()
    if path == None:
        path = os.getcwd()
    if not os.path.exists(f'{path}/{bin_dir}'):
        os.mkdir(f'{path}/{bin_dir}')

    if isinstance(extensions, str):
        extensions = [extensions]

    all_files = os.listdir(path)
    files = []
    for file in all_files:
        for extension in extensions:
            if extension in file:
                files.append(file)
                break
    print(files)
    moved = []
    for file in files:
        mod_time = os.path.getmtime(f'{path}/{file}')
        if now - mod_time < timespan:
            shutil.move(f'{path}/{file}', f'{path}/{bin_dir}/{file}')
            moved.append(file)
    print(f'{len(moved)} files moved to {path}/{bin_dir}')

    if delete or len(os.listdir(f'{path}/{bin_dir}')) == 0:
        shutil.rmtree(f'{path}/{bin_dir}')
        print(f'deleted {path}/{bin_dir}')

    if names:
        return moved


# # mv.sift

# In[ ]:


def sift(dict_or_list, filters, rename=False):
    """
    takes a list or dictionary and returns a filtered version were a filter
    string, or list of filters is part of the entries/keys. When a dictionary
    is filtered and rename=True, the keys of the filtered dictionary are
    renamed to the filtered versions. this is generally not advised.
    Since there is already a function named filter, this one is named sift.

    Returns:
    returns a filtered version of the provided dictionary.
    """

    if not isinstance(filters, list):
        filters = [filters]

    if isinstance(dict_or_list, list):
        filtered = _filter_list(dict_or_list, filters)

    if isinstance(dict_or_list, dict):
        filtered = _filter_dict(dict_or_list, filters, rename)

    return(filtered)


def _filter_list(a_list, filters):
    filtered = []
    for filter in filters:
        for item in a_list:
            if not isinstance(item, str):
                break
            if filter in item and item not in filtered:
                filtered.append(item)
    return(filtered)
    

def _filter_dict(a_dict, filters, rename):
    filtered = {}  
    for filter in filters:
        for key in a_dict.keys():
            if not isinstance(key, str):
                break
            if filter in key and key not in filtered.keys():
                if rename:
                    filtered[filter] = a_dict[key]
                else:
                    filtered[key] = a_dict[key]
    return(filtered)

