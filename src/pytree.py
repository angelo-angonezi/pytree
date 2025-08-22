# generate objects dfs module

print('initializing...')  # noqa

# Code destined to generating
# per object data frame.

######################################################################
# imports

# importing required libraries
print('importing required libraries...')  # noqa
import os
from os import walk
from os.path import sep
from os.path import join
from treelib import Tree
from os.path import split
from os.path import isdir
from os.path import getsize
from os.path import abspath
from os.path import normpath
from argparse import ArgumentParser
from src.classes.PyTree import PyTree
from src.utils.aux_funcs import is_cache
from src.utils.aux_funcs import get_start_path
from src.utils.global_vars import CACHE_FOLDERS
from src.classes.PyTree import ModuleProgressTracker
from src.classes.ProgressTracker import ProgressTracker
print('all required libraries successfully imported.')  # noqa

#####################################################################
# argument parsing related functions


def get_args_dict() -> dict:
    """
    Parses the arguments and returns a dictionary of the arguments.
    :return: Dictionary. Represents the parsed arguments.
    """
    # defining program description
    description = "pytree - a simpler 'tree' command running in python"

    # creating a parser instance
    parser = ArgumentParser(description=description)

    # start path param
    parser.add_argument('start_path',
                        nargs='*',
                        type=str or list,
                        help='defines path to directory to start building the tree',
                        default='.')

    # dirs only param
    parser.add_argument('-d', '--dirs-only',
                        dest='dirs_only',
                        required=False,
                        action='store_true',
                        help='tree displays directories only, and does not show files inside folders',
                        default=False)

    # show sizes param
    parser.add_argument('-s', '--show-sizes',
                        dest='show_sizes',
                        required=False,
                        action='store_true',
                        help='tree displays files and folder sizes, in mega or gigabytes',
                        default=False)

    # show counts param
    parser.add_argument('-c', '--show-counts',
                        dest='show_counts',
                        required=False,
                        action='store_true',
                        help='tree displays the number of files or folders inside each directory',
                        default=False)

    # verbose param
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        required=False,
                        action='store_true',
                        help='shows progress message while reading files/folders data',
                        default=False)

    # extension param
    parser.add_argument('-x', '--extension',
                        dest='extension',
                        required=False,
                        type=str or None,
                        help='tree will include only files that match given extension (e.g. ".txt", ".pdf")',
                        default=None)

    # keyword param
    parser.add_argument('-k', '--keyword',
                        dest='keyword',
                        required=False,
                        type=str or None,
                        help='tree will include only files that contain specific keyword on file name',
                        default=None)

    # level param
    parser.add_argument('-l', '--level',
                        dest='level',
                        required=False,
                        type=int or None,
                        help="defines tree's depth (until which subfolder tree will be created) [0=current, -1=all]",
                        default=-1)

    # creating arguments dictionary
    args_dict = vars(parser.parse_args())

    # returning the arguments dictionary
    return args_dict

######################################################################
# defining auxiliary functions


def pytree(start_path: str,
           dirs_only: bool,
           include_counts: bool,
           include_sizes: bool,
           verbose: bool,
           extension: str,
           keyword: str,
           level: int,
           progress_tracker: ModuleProgressTracker
           ) -> None:
    """
    Prints folder structure tree
    on the console.
    """
    # updating progress tracker attributes
    progress_tracker.verbose = verbose

    # initializing PyTree object
    tree = PyTree(start_path=start_path,
                  dirs_only=dirs_only,
                  include_counts=include_counts,
                  include_sizes=include_sizes,
                  extension=extension,
                  keyword=keyword,
                  level=level,
                  progress_tracker=progress_tracker)

    # updating tree dict
    tree.update_tree_dict()

    # updating tree
    tree.update_tree()


def parse_and_run(args_dict: dict,
                  progress_tracker: ModuleProgressTracker
                  ) -> None:
    """
    Extracts args from args_dict
    and runs module function.
    """
    # getting start path
    start_path = args_dict['start_path']
    start_path = get_start_path(start_path)

    # getting dirs only bool
    dirs_only = args_dict['dirs_only']

    # getting include counts bool
    include_counts = args_dict['show_counts']

    # getting include sizes bool
    include_sizes = args_dict['show_sizes']

    # getting verbose bool
    verbose = args_dict['verbose']

    # getting extension
    extension = args_dict['extension']

    # getting keyword
    keyword = args_dict['keyword']

    # getting level
    level = args_dict['level']

    # running pytree function
    pytree(start_path=start_path,
           dirs_only=dirs_only,
           include_counts=include_counts,
           include_sizes=include_sizes,
           verbose=verbose,
           extension=extension,
           keyword=keyword,
           level=level,
           progress_tracker=progress_tracker)

######################################################################
# defining main function


def main():
    """Runs main code."""
    # initializing current module progress tracker instance
    progress_tracker = ModuleProgressTracker()

    # running code in separate thread
    progress_tracker.run(function=parse_and_run,
                         args_parser=get_args_dict)

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
