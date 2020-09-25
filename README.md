# my_pytree
A simpler 'tree' linux command, running on Python.

Contains flags for displaying file and folder sizes (-s),
hiding files, showing only directories (-d),
get file count inside folder (-c) and search for specific file
extension (-x)

Requirements:
- python3;
- treelib module.

Installation:
1. Clone this repository
2. Change file permissions with 'chmod' (eg. 'chmod 777 pytree.py')
3. Add pytree.py to path or as an alias in bash_aliases file

Usage:

pytree.py [-h] [-d] [-s] [start_path [start_path ...]]

pytree - improved 'tree' command running in python

positional arguments:
start_path        defines path to directory to start building the tree

optional arguments:
-h, --help        show this help message and exit 
-d, --dirs-only   tree displays directories only, and does not show files inside folders
-s, --show-sizes  tree displays files and folder sizes, in mega or gigabytes

Examples:

$ pytree.py test_folder/
test_folder/

├── another_folder/

│   └── one_mb_file.txt

└── folder/

   ├── folder_inside_folder/
   
   │   ├── ten_kb_file.txt
    
   │   └── two_mb_file.txt
    
   └── ten_mb_file.txt

3 directories, 4 files


$ pytree.py test_folder/ -s 
test_folder/ (13.01 mb)

├── another_folder/ (1.0 mb) 

│   └── one_mb_file.txt (1.0 mb) 

└── folder/ (12.01 mb) 

   ├── folder_inside_folder/ (2.01 mb) 
    
   │   ├── ten_kb_file.txt (10.0 kb) 
   
   │   └── two_mb_file.txt (2.0 mb) 
    
   └── ten_mb_file.txt (10.0 mb) 

3 directories, 4 files, 13.01 mb 

$ pytree.py test_folder/ -s -d 
test_folder/ (13.01 mb) 

├── another_folder/ (1.0 mb) 

└── folder/ (12.01 mb) 

   └── folder_inside_folder/ (2.01 mb) 

3 directories, 4 files, 13.01 mb
