#!/usr/bin/python3

# pytree module
# Code destined to simulating 'tree' command from Linux, but running on python

######################################################################
# imports

import os
import argparse
from treelib import Tree
from pathlib import Path

#####################################################################
# toggle debug

DEBUG = False

#####################################################################
# defining default values
DEBUG_FOLDER = './../test_folder'
DEFAULT_START_PATH = '.'
ONE_BYTE = 1
ONE_KB = 1024 * ONE_BYTE
ONE_MB = 1024 * ONE_KB
ONE_GB = 1024 * ONE_MB

#####################################################################
# argument parsing related functions


def get_args_dict() -> dict:
    """
    Parses the arguments and returns a dictionary of the arguments.
    :return: Dictionary. Represents the parsed arguments.
    """
    # defining program description
    description = "pytree - improved 'tree' command running in python\n"

    # creating a parser instance
    parser = argparse.ArgumentParser(description=description)

    # adding arguments to parser
    parser.add_argument('start_path', nargs='*',
                        type=str,
                        help='defines path to directory to start building the tree',
                        default='.')

    parser.add_argument('-d', '--dirs-only',
                        dest='dirs_only_flag',
                        action='store_true',
                        help='tree displays directories only, and does not show files inside folders',
                        default=False)

    parser.add_argument('-s', '--show-sizes',
                        dest='show_sizes_flag',
                        action='store_true',
                        help='tree displays files and folder sizes, in mega or gigabytes',
                        default=False)

    # creating arguments dictionary
    args_dict = vars(parser.parse_args())

    # returning the arguments dictionary
    return args_dict


######################################################################
# defining auxiliary functions

def get_absolute_path(path_to_file_or_folder: str) -> str:
    """
    Given a path to a file or folder, returns its absolute path.
    :param path_to_file_or_folder: String. Represents partial path.
    :return: String. Represents absolute system path.
    """
    partial_path = Path(path_to_file_or_folder)
    absolute_path = partial_path.absolute()
    return absolute_path


def from_bytes_to_kilobytes(value_in_bytes: int) -> float:
    """
    Given a value in bytes, returns equivalent value in kilobytes.
    :param value_in_bytes: Integer. Represents file size value in bytes.
    :return: Float. Represents size value in kilobytes.
    """
    value_in_kilobytes = value_in_bytes / ONE_KB
    return value_in_kilobytes


def from_bytes_to_megabytes(value_in_bytes: int) -> float:
    """
    Given a value in bytes, returns equivalent value in megabytes.
    :param value_in_bytes: Integer. Represents file size value in bytes.
    :return: Float. Represents size value in megabytes.
    """
    value_in_megabytes = value_in_bytes / ONE_MB
    return value_in_megabytes


def from_bytes_to_gigabytes(value_in_bytes: int) -> float:
    """
    Given a value in bytes, returns equivalent value in gigabytes.
    :param value_in_bytes: Integer. Represents file size value in bytes.
    :return: Float. Represents size value in gigabytes.
    """
    value_in_gigabytes = value_in_bytes / ONE_GB
    return value_in_gigabytes


def get_adjusted_file_size(file_size_in_bytes: int) -> str:
    """
    Given file disk size in bytes, returns string containing file size in
    bytes, megabytes, or gigabytes, according to file size.
    :param file_size_in_bytes: String. Represents a path to a file or folder.
    :return: String. Represents file disk size in bytes, megabytes, or gigabytes.
    """
    # if file size is smaller than a megabyte
    adjusted_size_string = f'{file_size_in_bytes} bytes'

    # rewriting string if file size is bigger than a kilobyte
    if file_size_in_bytes >= ONE_KB:
        adjusted_file_size = from_bytes_to_kilobytes(value_in_bytes=file_size_in_bytes)
        adjusted_file_size = round(adjusted_file_size, 2)
        adjusted_size_string = f'{adjusted_file_size} kb'

    # rewriting string if file size is bigger than a megabyte
    if file_size_in_bytes >= ONE_MB:
        adjusted_file_size = from_bytes_to_megabytes(value_in_bytes=file_size_in_bytes)
        adjusted_file_size = round(adjusted_file_size, 2)
        adjusted_size_string = f'{adjusted_file_size} mb'

    # rewriting string if file size is bigger than a gigabyte
    if file_size_in_bytes >= ONE_GB:
        adjusted_file_size = from_bytes_to_gigabytes(value_in_bytes=file_size_in_bytes)
        adjusted_file_size = round(adjusted_file_size, 2)
        adjusted_size_string = f'{adjusted_file_size} gb'

    # returning adjusted string
    return adjusted_size_string


def get_file_size_in_bytes(file_path: str) -> int:
    """
    Given a path to a file, returns file disk size in bytes.
    :param file_path: String. Represents a path to a file or folder
    :return: Integer. Represents file disk size in bytes.
    """
    return os.path.getsize(file_path)


def get_folder_size_in_bytes(path_to_folder: str) -> int:
    """
    Given a path to a file, returns file disk size in bytes.
    :param path_to_folder: String. Represents a path to a file or folder
    :return: Integer. Represents folder disk size in bytes.
    """
    full_dir_size = 0
    everything_in_folder = os.walk(path_to_folder)

    # iterating over dirs and files
    for root, _, files in everything_in_folder:
        for file in files:
            file_path = os.path.join(root, file)
            file_size = get_file_size_in_bytes(file_path=file_path)
            full_dir_size += file_size

    return full_dir_size


def pytree(start_path: str = '.',
           include_files: bool = True,
           include_sizes: bool = False,
           force_absolute_ids: bool = True
           ) -> None:
    """
    Returns a `treelib.Tree` representing the filesystem under `start_path`.
    You can then print the `Tree` object using `tree.show()`
    :param start_path: String. Represents an absolute or relative path.
    :param include_files: Boolean. Indicates whether to also include the files in the tree.
    :param include_sizes: Boolean. Indicates whether or not tree should display file and folder sizes, in megabytes.
    :param force_absolute_ids: Boolean. Indicates whether ids should be absolute. They will
    be relative if start_path is relative, and absolute otherwise.
    """
    # creating tree instance
    tree = Tree()
    first = True

    # getting dirs and files
    all_files_and_folders = os.walk(start_path)

    # starting dirs, files and size count
    total_dirs_num = 0
    total_files_num = 0
    total_disk_size = 0

    # iterating over dirs and files
    for root, _, files in all_files_and_folders:
        p_root = Path(root)
        if first:
            parent_id = None
            first = False
        else:
            parent = p_root.parent
            parent_id = parent.absolute() if force_absolute_ids else parent

        # getting absolute path
        abs_path = p_root.absolute()

        # getting root id
        p_root_id = abs_path if force_absolute_ids else p_root

        # getting dir name
        dir_name = (p_root.name if p_root.name != "" else ".")
        dir_name += '/'

        # adding dir size to name
        if include_sizes:
            dir_size_in_bytes = get_folder_size_in_bytes(path_to_folder=abs_path)
            adjusted_dir_size = get_adjusted_file_size(file_size_in_bytes=dir_size_in_bytes)
            dir_name += f' ({adjusted_dir_size})'

        # creating folder node
        tree.create_node(tag=dir_name,
                         identifier=p_root_id,
                         parent=parent_id)

        # increasing total dirs count
        total_dirs_num += 1

        # iterating over files
        for f in files:
            # getting file name
            f_id = p_root_id / f
            file_name = f_id.name

            # adding file size to name
            if include_sizes:
                file_size_in_bytes = get_file_size_in_bytes(file_path=f_id)
                adjusted_file_size = get_adjusted_file_size(file_size_in_bytes=file_size_in_bytes)
                file_name += f' ({adjusted_file_size})'

            # creating file node
            if include_files:
                tree.create_node(tag=file_name,
                                 identifier=f_id,
                                 parent=p_root_id)

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
    dirs_and_files_string = f'{total_dirs_num - 1} {dirs_string}, {total_files_num} {files_string}'

    # adding full size
    if include_sizes:
        full_size = get_folder_size_in_bytes(path_to_folder=start_path)
        adjusted_full_size = get_adjusted_file_size(file_size_in_bytes=full_size)
        full_size_string = f', {adjusted_full_size}'
        dirs_and_files_string += full_size_string

    # getting tree size
    size = tree.size()

    # checking if tree is empty
    if size == 0:
        # printing invalid input message
        print('Invalid input. Must be a directory.\nPlease check input and try again.')
    else:
        # displaying tree
        print(tree)
        print(dirs_and_files_string)

######################################################################
# defining main function


def main():
    # getting args dict
    args_dict = get_args_dict()

    # checking if user has passed specific folder
    start_path = args_dict['start_path'][0]
    if start_path is None:
        start_path = DEFAULT_START_PATH

    # checking whether tree should contain only dirs or also the files
    include_files_param = not(args_dict['dirs_only_flag'])

    # checking whether tree should contain file and folder size information
    include_sizes_param = args_dict['show_sizes_flag']

    # checking debug toggle
    if DEBUG:
        # getting debug tree
        pytree(start_path=DEBUG_FOLDER,
               include_files=True,
               include_sizes=True,
               force_absolute_ids=False)

    else:
        # getting tree
        pytree(start_path=start_path,
               include_files=include_files_param,
               include_sizes=include_sizes_param,
               force_absolute_ids=False)

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
