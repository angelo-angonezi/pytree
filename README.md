# pytree
A simpler 'tree' linux command, running on Python.

Contains flags for displaying file and folder sizes (-s);
hiding files, showing only directories (-d);
get file count inside folder (-c); search for specific file
extension (-x); and subfolder level (-l).

Requirements:
- python3;
- treelib package (https://pypi.org/project/treelib/ or https://anaconda.org/conda-forge/treelib).

Installation:
1. Clone this repository
2. Run code via command "python /path_to_install/src/pytree.py"
3. (optional) Add previous command to path or as an alias in bash_aliases file - so that "pytree" command is available globally

--
Usage:

pytree.py [-h] [-d] [-s] [-c] [-x SPECIFIED_EXTENSION] [-l LEVEL] [start_path [start_path ...]]

pytree - a simpler 'tree' command running in python

positional arguments:
  start_path            defines path to directory to start building the tree

optional arguments:
  -h, --help            show this help message and exit
  -d, --dirs-only       tree displays directories only, and does not show files inside folders
  -s, --show-sizes      tree displays files and folder sizes, in mega or gigabytes
  -c, --show-counts     tree displays the number of files or folders inside each directory
  -x SPECIFIED_EXTENSION, --extension SPECIFIED_EXTENSION
                        tree will include only files that match given extension (e.g. ".txt", ".pdf")
  -l LEVEL, --level LEVEL
                        defines depth level of recursion (until which subfolder tree will be
                        created)[0=current, -1=all]

--
Examples:

$ python pytree.py test_folder/
test_folder/

├── another_folder/

│   └── one_mb_file.txt

└── folder/

   ├── folder_inside_folder/
   
   │   ├── ten_kb_file.txt
    
   │   └── two_mb_file.txt
    
   └── ten_mb_file.txt

3 directories, 4 files


$ python pytree.py test_folder/ -s 
test_folder/ (13.01 mb)

├── another_folder/ (1.0 mb) 

│   └── one_mb_file.txt (1.0 mb) 

└── folder/ (12.01 mb) 

   ├── folder_inside_folder/ (2.01 mb) 
    
   │   ├── ten_kb_file.txt (10.0 kb) 
   
   │   └── two_mb_file.txt (2.0 mb) 
    
   └── ten_mb_file.txt (10.0 mb) 

3 directories, 4 files, 13.01 mb 

$ python pytree.py test_folder/ -s -d 
test_folder/ (13.01 mb) 

├── another_folder/ (1.0 mb) 

└── folder/ (12.01 mb) 

   └── folder_inside_folder/ (2.01 mb) 

3 directories, 4 files, 13.01 mb
