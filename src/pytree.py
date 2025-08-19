# pytree module

# code destined to simulating 'tree'
# command from Linux, running on python.

######################################################################
# imports

# importing required libraries
from os import sep
from os import walk
from treelib import Tree
from pathlib import Path
from argparse import ArgumentParser
from src.utils.global_vars import CACHE_FOLDERS
from src.utils.aux_funcs import get_file_size_in_bytes
from src.classes.ProgressTracker import ProgressTracker
from src.utils.aux_funcs import get_folder_size_in_bytes
from src.utils.aux_funcs import get_adjusted_file_size_string
from src.utils.aux_funcs import get_number_of_files_inside_folder

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

    # adding arguments to parser
    parser.add_argument('start_path',
                        nargs='*',
                        type=str,
                        help='defines path to directory to start building the tree',
                        default='.')

    parser.add_argument('-d', '--dirs-only',
                        dest='dirs_only_flag',
                        required=False,
                        action='store_true',
                        help='tree displays directories only, and does not show files inside folders',
                        default=False)

    parser.add_argument('-s', '--show-sizes',
                        dest='show_sizes_flag',
                        required=False,
                        action='store_true',
                        help='tree displays files and folder sizes, in mega or gigabytes',
                        default=False)

    parser.add_argument('-c', '--show-counts',
                        dest='show_counts_flag',
                        required=False,
                        action='store_true',
                        help='tree displays the number of files or folders inside each directory',
                        default=False)

    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        required=False,
                        action='store_true',
                        help='shows progress message while reading files/folders data',
                        default=False)

    parser.add_argument('-x', '--extension',
                        dest='specific_extension',
                        required=False,
                        type=str or None,
                        help='tree will include only files that match given extension (e.g. ".txt", ".pdf")',
                        default=None)

    parser.add_argument('-k', '--keyword',
                        dest='keyword',
                        required=False,
                        type=str or None,
                        help='tree will include only files that contain specific keyword on file name',
                        default=None)

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


def get_tree(start_path: str,
             include_files: bool,
             include_counts: bool,
             include_sizes: bool,
             specific_extension: str or None = None,
             keyword: str or None = None,
             subfolder_level: int = 1,
             progress_tracker: ProgressTracker = ProgressTracker
             ) -> Tree:
    """
    # TODO: update docstring.
    Docstring.
    """
    # TODO: modularize this code!
    # defining placeholder value for Tree
    tree = Tree()

    # defining first flag
    first = True

    # getting dirs and files
    all_files_and_folders = walk(start_path)

    # iterating over dirs and files
    for root, _, files in all_files_and_folders:

        # getting cache bool list
        cache_bool_list = [cache_str in root for cache_str in CACHE_FOLDERS]

        # getting cache bool
        cache_bool = any(cache_bool_list)

        # checking if file is cache-related
        if cache_bool:

            # skipping file
            continue

        # getting root path
        root_path = Path(root)

        # converting data types
        root_path_str = str(root_path)

        # getting current file/dir level (counting OS separator occurrences)
        current_level = root_path_str.count(sep)

        # checking if desired subfolder level is not -1 (all subfolders)
        if subfolder_level != -1:

            # checking if current level is higher than defined subfolder level
            if current_level > subfolder_level:

                # skipping current file/dir
                continue

        # checking if element is first
        if first:

            # updating parent id
            parent_id = None

            # setting first flag to False
            first = False

        else:

            # updating parent id
            parent_id = root_path.parent

        # getting absolute path
        abs_path = root_path.absolute()

        # getting dir name
        dir_name = (root_path.name if root_path.name != "" else ".")
        dir_name += '/'

        # getting based text string
        text_string = f"{dir_name}"

        # getting number of files and folders inside directory
        current_dir_file_and_folder_count = get_number_of_files_inside_folder(path_to_folder=abs_path)

        # checking if should include counts
        if include_counts:

            # adding count to dir name
            text_string += f' [{current_dir_file_and_folder_count}]'

        # checking if should include sizes
        if include_sizes:

            # getting dir size
            dir_size_in_bytes = get_folder_size_in_bytes(path_to_folder=abs_path)

            # getting adjusted dir size str
            adjusted_dir_size = get_adjusted_file_size_string(file_size_in_bytes=dir_size_in_bytes)

            # appending dir size to colored string
            text_string += f' ({adjusted_dir_size})'

        # creating folder node
        tree.create_node(tag=text_string,
                         identifier=root_path,
                         parent=parent_id)

        # updating progress tracker attributes
        progress_tracker.folders_num += 1

        # iterating over files
        for file in files:

            # updating progress tracker attributes
            progress_tracker.scanned_num += 1

            # getting file id
            f_id = root_path / file

            # getting file name
            file_name = f_id.name

            # checking if user has passed specific extension
            if specific_extension is not None:

                # checking if current file is of specific extension
                if not file.endswith(specific_extension):

                    # skipping to next file
                    continue

            # checking if user has passed specific keyword
            if keyword is not None:

                # checking if current file contains specific keyword
                if keyword not in file:

                    # skipping to next file
                    continue

            # checking if should include sizes
            if include_sizes:

                # getting file size
                file_size_in_bytes = get_file_size_in_bytes(file_path=f_id)

                # getting adjusted file size str
                adjusted_file_size = get_adjusted_file_size_string(file_size_in_bytes=file_size_in_bytes)

                # appending file size to file name
                file_name += f' ({adjusted_file_size})'

                # updating progress tracker attributes
                progress_tracker.total_size += file_size_in_bytes

            # creating file node
            if include_files:

                # creating tree node from file
                tree.create_node(tag=file_name,
                                 identifier=f_id,
                                 parent=root_path)

            # updating progress tracker attributes
            progress_tracker.files_num += 1

    # returning tree
    return tree


def pytree(start_path: str,
           include_files: bool,
           include_sizes: bool,
           include_counts: bool,
           verbose: bool,
           specific_extension: str or None = None,
           keyword: str or None = None,
           subfolder_level: int = 1,
           progress_tracker: ProgressTracker = ProgressTracker
           ) -> None:
    """
    # TODO: update docstring.
    Docstring.
    """
    # updating progress tracker toggles
    progress_tracker.include_files = include_files
    progress_tracker.include_sizes = include_sizes
    progress_tracker.include_counts = include_counts
    progress_tracker.verbose = verbose

    # getting current tree
    # TODO: convert this all to a single class!
    current_tree = get_tree(start_path=start_path,
                            include_files=include_files,
                            include_counts=include_counts,
                            include_sizes=include_sizes,
                            specific_extension=specific_extension,
                            keyword=keyword,
                            subfolder_level=subfolder_level,
                            progress_tracker=progress_tracker)

    # updating progress tracker tree
    progress_tracker.tree = current_tree


def parse_and_run(args_dict: dict,
                  progress_tracker: ProgressTracker
                  ) -> None:
    """
    Extracts args from args_dict
    and runs module function.
    """
    # checking if user has passed specific folder
    start_path = args_dict['start_path'][0]

    # checking whether tree should contain only dirs or also the files
    include_files_param = not (args_dict['dirs_only_flag'])

    # checking whether tree should contain file and folder counts information
    include_counts_param = args_dict['show_counts_flag']

    # checking whether tree should contain file and folder size information
    include_sizes_param = args_dict['show_sizes_flag']

    # checking whether display progress message while reading info
    verbose = args_dict['verbose']

    # checking if user has passed specific extension to be looked for
    specific_extension = args_dict['specific_extension']

    # checking if user has passed specific keyword to be looked for
    keyword = args_dict['keyword']

    # getting subfolder level
    level = args_dict['level']

    # running pytree function
    pytree(start_path=start_path,
           include_files=include_files_param,
           include_sizes=include_sizes_param,
           include_counts=include_counts_param,
           verbose=verbose,
           specific_extension=specific_extension,
           keyword=keyword,
           subfolder_level=level,
           progress_tracker=progress_tracker)

######################################################################
# defining main function


def main():
    """Runs main code"""
    # initializing current progress tracker instance
    progress_tracker = ProgressTracker()

    # running code in separate thread
    progress_tracker.run(function=parse_and_run,
                         args_parser=get_args_dict)

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module