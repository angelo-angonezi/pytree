# pytree
A Python CLI utility for visualizing folder trees with sizes and counts.

## Installation

pytree requires **Python version 3.9+** in order to run. You can install pytree in your Python environment with the command:
```shell
pip install pytree2
```

## Usage

```shell
pytree [-h] [-d] [-s] [-c] [-x EXTENSION] [-k KEYWORD] [-l LEVEL] [start_path ...]
```

```shell
pytree - a python cli utility for visualizing folder trees with sizes and counts

positional arguments:
  start_path            defines path to directory to start building the tree

optional arguments:
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
```

### Examples

#### Basic usage
```shell
$pytree test_folder
```

```shell
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
Additionally, pytree will print a summary line in the end, with the folder/file count and total size.
```shell
$pytree test_folder -dcs
```

```shell
test_folder [2] (13 mb)
├── another_folder [2] (1 mb)
│   └── empty_folder [0] (0 bytes)
└── folder [3] (12 mb)
    └── folder_inside_folder [3] (2 mb)

5 folders, 6 files, 13 mb
```

#### Specifying extension/keyword
You can also specify a search keyword (by passing **-x** your_extension) or keyword (by passing **-k** your_keyword), e.g:
```shell
$pytree test_folder -cs -x .pdf
```

```shell
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
