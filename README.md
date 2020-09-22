# my_pytree
a simpler 'tree' linux command, running on Python.
*requires treelib module.
contains flags for displaying file and folder sizes (-s),
and for hiding files, showing only directories (-d).

usage: pytree.py [-h] [-d] [-s] [start_path [start_path ...]]

pytree - improved 'tree' command running in python

positional arguments:
start_path        defines path to directory to start building the tree

optional arguments:
-h, --help        show this help message and exit 
-d, --dirs-only   tree displays directories only, and does not show files inside folders
-s, --show-sizes  tree displays files and folder sizes, in mega or gigabytes
