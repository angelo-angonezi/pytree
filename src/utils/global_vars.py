# global variables module

# Code destined to storing global
# variables used in main script.

######################################################################
# imports

from sys import platform
from os.path import join

######################################################################
# defining global variables

CURRENT_OS = platform
DEBUG = False
DEBUG_FOLDER = join('.', 'test_folder')
DEFAULT_START_PATH = '.'
ONE_BYTE = 1
MULTIPLIER = 1024
ONE_KB = ONE_BYTE * MULTIPLIER
ONE_MB = ONE_KB * MULTIPLIER
ONE_GB = ONE_MB * MULTIPLIER
ONE_TB = ONE_GB * MULTIPLIER
CACHE_FOLDERS = ['__pycache__',  # defines marker for cache folders (will be skipped)
                 '.git',         # git related files
                 '.idea']        # pycharm related files

######################################################################
# end of current module
