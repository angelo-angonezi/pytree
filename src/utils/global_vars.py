# global variables module

# Code destined to storing global
# variables used in main script.

######################################################################
# defining global variables

UPDATE_TIME = 0.1
MEMORY_LIMIT = 85
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
