# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 15:11:36 2022

Putting your filepaths in classes is optional.
Classes can allow you to better organize directories, and allow auto-print of names on import.
However, it may just be more work if you only have a few commonly used paths.

@author: VanVlietL
"""

## filepaths without using classes

fp1 = '/random/path/to/file'
fp2 = '/another/random/path/to/file'

## using classes

class fwipaths:
    input_dir = 'C:\\Users\\VanVlietL\\Documents\\Data\\'
    output_dir = 'C:\\Users\\VanVlietL\\Documents\\Data\\figs\\'
    
class noonpaths:
    input_dir = 'C:\\Users\\VanVlietL\\Documents\\Data\\Noon\\'
    output_dir = 'C:\\Users\\VanVlietL\\Documents\\Data\\Noon\\'
    
class randompaths:
    input_dir = 'C:\\Users\\VanVlietL\\Documents\\Random\\'
    output_dir = 'C:\\Users\\VanVlietL\\Documents\\Random\\Out\\'
    
### some special lines to print what you're importing from classes ### 

for obj in [noonpaths, fwipaths, randompaths]:
    print(f'\n{obj}')
    [print(f'  {a}') for a in dir(obj()) if not a.startswith('__')]

del(obj) # don't want to import this