# pytree module
# Code destined to simulating 'tree' command from Linux, but running on python

######################################################################
# imports

import argparse
from os import walk
from sys import argv
from treelib import Tree
from pathlib import Path

#####################################################################
# toggle debug

DEBUG = True

#####################################################################
# defining default values
DEBUG_FOLDER = './../test_folder'
DEFAULT_START_PATH = '.'

#####################################################################
# argument parsing related functions


def get_args_dict() -> dict:
    """
    Parses the arguments and returns a dictionary of the arguments.
    :return: Dictionary. Represents the parsed arguments.
    """
    # creating a parser instance
    parser = argparse.ArgumentParser(description="PyTree - 'tree' command running in python")

    # adding arguments to parser
    parser.add_argument('-s', '--start-path',
                        type=str,
                        required=False,
                        help='Defines path to directory to start building the tree.',
                        default=DEFAULT_START_PATH)

    parser.add_argument('-b', '--debug',
                        type=str,
                        required=False,
                        help='Defines whether code runs in debug mode.',
                        default=False)

    parser.add_argument('-d', '--dirs-only',
                        type=str,
                        required=False,
                        help='Tree displays directories only, and does not show files inside folders.',
                        default=False)

    # saving arguments to a dictionary instance
    args_dict = vars(parser.parse_args())

    # returning the arguments dictionary
    return args_dict


######################################################################
# defining auxiliary functions


def pytree(start_path: str = '.',
           include_files: bool = True,
           include_directories: bool = True,
           force_absolute_ids: bool = True
           ) -> None:
    """
    Returns a `treelib.Tree` representing the filesystem under `start_path`.
    You can then print the `Tree` object using `tree.show()`
    :param start_path: String. Represents an absolute or relative path.
    :param include_files: Boolean. Indicates whether to also include the files in the tree.
    :param include_directories: Boolean. Indicates whether to also include the directories in the tree.
    :param force_absolute_ids: Boolean. Indicates whether ids should be absolute. They will
    be relative if start_path is relative, and absolute otherwise.
    """
    # creating tree instance
    tree = Tree()
    first = True

    # getting dirs and files
    all_files_and_folders = walk(start_path)

    # starting dirs and files count
    total_dirs_num = 0
    total_files_num = 0

    # iterating over dirs and files
    for root, _, files in all_files_and_folders:
        p_root = Path(root)
        if first:
            parent_id = None
            first = False
        else:
            parent = p_root.parent
            parent_id = parent.absolute() if force_absolute_ids else parent

        # getting root id
        p_root_id = p_root.absolute() if force_absolute_ids else p_root

        # creating folder node
        if include_directories:
            tree.create_node(tag="%s/" % (p_root.name if p_root.name != "" else "."),
                             identifier=p_root_id, parent=parent_id)

        # increasing total dirs count
        total_dirs_num += 1

        if include_files:
            # iterating over files
            for f in files:
                f_id = p_root_id / f

                # creating file node
                tree.create_node(tag=f_id.name, identifier=f_id, parent=p_root_id)

                # increasing total files count
                total_files_num += 1

    # getting dirs and files string

    # checking dirs num
    if total_dirs_num == 1:
        dirs_string = 'directory'
    else:
        dirs_string = 'directories'

    # checking files num
    if total_files_num == 1:
        files_string = 'file'
    else:
        files_string = 'files'

    # defining dirs and files string
    dirs_and_files_string = f'{total_dirs_num} {dirs_string}, {total_files_num} {files_string}'

    # getting tree size
    size = tree.size()

    # checking if tree is empty
    if size == 0:
        # printing invalid input message
        print('Invalid input. Must be a directory.\nPlease check input and try again.')
    else:
        # displaying tree
        print(tree, end='\b')
        spacer = '-' * len(dirs_and_files_string)
        print(spacer)
        print(dirs_and_files_string)

######################################################################
# defining main function


def main():
    # trying to get argument
    try:
        directory = argv[1]

    # defining directory if user has not given any
    except IndexError:
        directory = '.'

    # getting tree
    pytree(start_path=directory,
           include_files=True,
           include_directories=True,
           force_absolute_ids=False)


######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
