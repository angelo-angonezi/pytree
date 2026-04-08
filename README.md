# pytree
A Python CLI utility for visualizing folder trees with sizes and counts.

## Installation

_pytree_ requires **Python version 3.10+** in order to run. You can install _pytree_ in your Python environment with the command:
```shell
pip install pytree2
```

## Usage

```shell
pytree [-h] [-d] [-s] [-c] [-x EXTENSION] [-k KEYWORD] [-l LEVEL] [start_path ...]
```

```
pytree - a python cli utility for visualizing folder trees with sizes and counts

positional arguments:
  start_path            defines path to directory to start building the tree

options:
  -h, --help            show this help message and exit
  -d, --dirs-only       tree displays directories only, and does not show files inside folders
  -s, --show-sizes      tree displays files and folder sizes, in mega or gigabytes
  -c, --show-counts     tree displays the number of files or folders inside each directory
  -x EXTENSION, --extension EXTENSION
                        tree will include only files that match given extension (e.g. ".txt", ".pdf")
  -k KEYWORD, --keyword KEYWORD
                        tree will include only files that contain specific keyword on file name
  -l LEVEL, --level LEVEL
                        defines tree's depth (until which subfolder tree will be created) [0=start_path, -1=all]
  -loc, --lines-of-code
                        tree displays the number of lines of code/comment for .py files in dir
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        saves tree as a table in given output path [.csv]
```

### Examples

#### Basic usage
```shell
pytree test_folder
```

```
test_folder
├── another_folder
│   ├── empty_folder
│   └── one_mb_file.txt
└── folder
    ├── a_python_file.py
    ├── folder_inside_folder
    │   ├── not_a_text_file.pdf
    │   ├── ten_kb_file.txt
    │   └── two_mb_file.txt
    └── ten_mb_file.txt
```

#### Using optional arguments
By concatenating the optional arguments, you can get a clear view of the folder structure.
Additionally, _pytree_ will print a summary line in the end, with the folder/file count and total size.
```shell
pytree test_folder -dcs
```

```
test_folder [2] (13 mb)
├── another_folder [2] (1 mb)
│   └── empty_folder [0] (0 bytes)
└── folder [3] (12 mb)
    └── folder_inside_folder [3] (2 mb)

5 folders, 6 files, 13 mb
```

#### Specifying extension/keyword
You can also specify a search keyword (by passing **-x** _your_extension_) or keyword (by passing **-k** _your_keyword_), e.g:
```shell
pytree test_folder -cs -x .pdf
```

```
test_folder [2] (136 bytes)
├── another_folder [1] (0 bytes)
│   └── empty_folder [0] (0 bytes)
└── folder [1] (136 bytes)
    └── folder_inside_folder [1] (136 bytes)
        └── not_a_text_file.pdf (136 bytes)

5 folders, 6 files (1 valid), 136 bytes
```
Notice that by using this option together with the **-c** and **-s** flags, the counts and sizes in the final summary
line will contain a counter for files matching search criteria, and the total size will reflect only matching files,
providing an easy and quick way of scanning folders and identifying large files of a specified extension/keyword.

#### Saving tree
You can save the tree (file and folder information) by specifying an output path (by passing **-o** _path/to/table.csv_), e.g:
```shell
pytree test_folder -cs -o tree.csv
```

```
test_folder [2] (13 mb)
├── another_folder [2] (1 mb)
│   ├── empty_folder [0] (0 bytes)
│   └── one_mb_file.txt (1 mb)
└── folder [3] (12 mb)
    ├── a_python_file.py (154 bytes)
    ├── folder_inside_folder [4] (2 mb)
    │   ├── another_python_file.py (314 bytes)
    │   ├── not_a_text_file.pdf (136 bytes)
    │   ├── ten_kb_file.txt (10 kb)
    │   └── two_mb_file.txt (2 mb)
    └── ten_mb_file.txt (10 mb)

5 folders, 7 files, 13 mb
Saved output table to "tree.csv"
```
The output .csv will contain the same information as specified by the keywords, such as level (**-l**),
keyword (**-k**), size (**-s**) and dirs_only (**-d**). 

#### Lines of code
_pytree_ can also be used to obtain the count (and percentage) of lines of code (loc) and comments for python files inside
input directory, e.g:
```shell
pytree test_folder -c -loc
```

```
test_folder [2]
├── another_folder [1]
│   └── empty_folder [0]
└── folder [2]
    ├── a_python_file.py {2 lines of code (33%), 4 comments (67%)}
    └── folder_inside_folder [1]
        └── another_python_file.py {4 lines of code (40%), 6 comments (60%)}

5 folders, 7 files (2 valid), 6 lines of code (38%), 10 comments (62%)
```
This will provide a lines of code and comments count for all .py files in the tree,
as well as a summary for the whole directory.
