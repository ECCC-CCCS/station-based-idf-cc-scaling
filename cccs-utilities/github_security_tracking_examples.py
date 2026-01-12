#!/usr/bin/env python
# coding: utf-8

#%%
# ### Importing filepaths from a separate file in python
# - file must be in same directory as you are working in
# - OR, add filepath to py-paths using sys.path.append

# add to pypaths using sys.path.append
import sys
import os
sys.path.append(os.path.expanduser('~/scripts/CanLEAD-FWI/modules')) # os.path.expanduser allows us to use ~ notation instead of using abs filepath

from scaling_filepaths import * # import everything
from scaling_filepaths import noonpaths # import only noonpaths class

#%%
# ### for bash executables in git directories
# - won't be able to use classes

# in bash
source scaling_filepaths

#%%
# ### bash jobsub files
# - switching directories for accessing files for submission 
# - or writing the git hash and repo to file, using 'subprocess' you must be in the correct directory (can also change inside py, I like to do it here)

cd ~/scripts/CanLEAD-FWI/modules

#%%
# ### .gitignore
# 
# Add your filepaths.py to .gitignore, so it will never be tracked and accidentally push to GitHub 
# 
# Some common configurations: https://gist.github.com/octocat/9257657
# Configure ignored files for all repos on your computer: https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files#configuring-ignored-files-for-all-repositories-on-your-computer
#  - git config --global core.excludesfile ~/.gitignore_global (read above link)
  
# in command line, create a gitignore file
touch .gitignore
echo "filepaths.py" >> .gitignore # add file to gitignore

# or, can add manually
vim .gitignore # open .gitignore
# add files and file groups (using *), you don't want:
filepaths.py
*.sh # I personally don't want to include my run files, and don't otherwise work in bash much
*.pyc 

# add git .gitignore to tracking
git add .gitignore
git status # note filepaths.py is not tracked!

#%%
# ### Access Git hashes (aka commit ID) to bash or py output, or file attributes
# Not in the right working dir? Add arg cwd=os.path.dirname(os.path.abspath(__file__)) to subprocess.check_output(), or change dir before running script

# for py scripts run on linux/unix

import subprocess 
git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip() ## doesn't work on windows
# can add '--short' tage before HEAD to get short hash

## Want to add automatic link to repo? 
link = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).decode('ascii').strip() 
#https://github.com/ECCC-CCCS/CanLEAD-FWI.git

useable_link = link.split('.git')[0] + '/commit/' + git_hash
print(useable_link)

#%%

# for py on Windows, use following function, from https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script
import os

def get_git_revision(base_path): 
    import pathlib
    git_dir = pathlib.Path(base_path) / '.git'
    with (git_dir / 'HEAD').open('r') as head:
        ref = head.readline().split(' ')[-1].strip()
    with (git_dir / ref).open('r') as git_hash:
        return git_hash.readline().strip()
   
get_git_revision(os.getcwd())

##  ex, add to xarray attrs

#ds.attrs['git hash'] = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip() 
#ds.attrs['git repo'] = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).decode('ascii').strip() 

#%%

# In bash
git config --get remote.origin.url # bash
git rev-parse HEAD






