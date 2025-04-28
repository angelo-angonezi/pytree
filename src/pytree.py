# pytree module

# code destined to simulating 'tree'
# command from Linux, running on python.

######################################################################
# imports

# adding project to path
from sys import path
path.append('C:\\pycharm_projects\\pytree')

# importing required libraries
from os import sep
from os import walk
from treelib import Tree
from pathlib import Path
from argparse import ArgumentParser
from src.utils.aux_funcs import get_console_width
from src.utils.aux_funcs import get_absolute_path
from src.utils.aux_funcs import print_progress_message
from src.utils.aux_funcs import get_file_size_in_bytes
from src.utils.aux_funcs import get_folder_size_in_bytes
from src.utils.aux_funcs import get_adjusted_file_size_string
from src.utils.aux_funcs import get_number_of_files_inside_folder

# importing global variables
from src.utils.global_vars import DEBUG
from src.utils.global_vars import CURRENT_OS
from src.utils.global_vars import DEBUG_FOLDER
from src.utils.global_vars import CACHE_FOLDERS
from src.utils.global_vars import DEFAULT_START_PATH

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
                        dest='specified_extension',
                        required=False,
                        type=str or None,
                        help='tree will include only files that match given extension (e.g. ".txt", ".pdf")',
                        default=None)

    parser.add_argument('-k', '--keyword',
                        dest='keyword',
                        required=False,
                        type=str or None,
                        help='tree will include only files that contain specified keyword on file name',
                        default=None)

    parser.add_argument('-nr', '--no-recolor',
                        dest='no_recolor',
                        action='store_true',
                        help='disables tree recoloring performed when running on linux',
                        default=False)

    level_help = 'defines depth level of recursion (until which subfolder tree will be created)'
    level_help += '[0=current, -1=all]'
    parser.add_argument('-l', '--level',
                        dest='level',
                        required=False,
                        type=int or None,
                        help=level_help,
                        default=-1)

    # creating arguments dictionary
    args_dict = vars(parser.parse_args())

    # returning the arguments dictionary
    return args_dict

######################################################################
# defining auxiliary functions


def pytree(start_path: str = '.',
           include_files: bool = True,
           include_sizes: bool = False,
           include_counts: bool = False,
           verbose: bool = True,
           specific_extension: str or None = None,
           keyword: str or None = None,
           subfolder_level: int = 1,
           no_recolor: bool = False,
           force_absolute_ids: bool = True,
           windows: bool = False
           ) -> None:
    """
    Prints 'tree' of files and subfolders inside
    given start folder, including file size and
    file count, according to given parameters.
    :param start_path: String. Represents an absolute or relative path.
    :param include_files: Boolean. Indicates whether to also include the files in the tree.
    :param include_sizes: Boolean. Indicates whether tree should display file and folder sizes, in megabytes.
    :param include_counts: Boolean. Indicates whether tree should display file and folder counts.
    :param verbose: Boolean. Indicates whether tree should display progress message while reading.
    :param specific_extension: String. Represents a specific file extension to be searched.
    :param keyword: String. Represents a specific keyword to be searched.
    :param subfolder_level: Integer. Represents subfolder depth to be used when creating tree.
    :param no_recolor: Boolean. Indicates whether to skip recoloring step done when running on linux.
    :param force_absolute_ids: Boolean. Indicates whether ids should be absolute. They will
    be relative if start_path is relative, and absolute otherwise.
    :param windows: Boolean. Indicates whether program is running on windows system.
    """
    # creating tree instance
    tree = Tree()

    # defining first flag
    first = True

    # getting dirs and files
    all_files_and_folders = walk(start_path)

    # starting dirs, files and size count
    total_dirs_num = 0
    total_files_num = 0

    # defining placeholder value for scanned files num
    scanned_files_num = 0

    # printing execution message
    f_string = f'reading data...'
    print_progress_message(base_string=f_string,
                           conditional=verbose)

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

        # getting path root
        p_root = Path(root)

        # converting path root to string
        p_root_str = str(p_root)

        # getting current file/dir level (counting OS separator occurrences)
        current_level = p_root_str.count(sep)

        # checking if desired subfolder level is not -1 (all subfolders)
        if subfolder_level != -1:

            # checking if current level is higher than defined subfolder level
            if current_level > subfolder_level:

                # skipping current file/dir
                continue

        # setting parent id
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

        # getting based text string
        colored_text_string = f"{dir_name}"

        # getting recolor bool
        recolor = (not windows) and (not no_recolor)

        # checking whether to recolor string
        if recolor:

            # coloring dir string
            colored_text_string = f"\033[0;34;42m{dir_name}"

            # recoloring to white so that it doesn't affect other nodes
            colored_text_string += f"\033[0;37;48m"

        # getting number of files and folders inside directory
        current_dir_file_and_folder_count = get_number_of_files_inside_folder(path_to_folder=abs_path)

        # adding count to dir name
        if include_counts:
            colored_text_string += f' [{current_dir_file_and_folder_count}]'

        # adding dir size to name
        if include_sizes:

            # getting dir size
            dir_size_in_bytes = get_folder_size_in_bytes(path_to_folder=abs_path)

            # getting adjusted dir size str
            adjusted_dir_size = get_adjusted_file_size_string(file_size_in_bytes=dir_size_in_bytes)

            # appending dir size to colored string
            colored_text_string += f' ({adjusted_dir_size})'

        # creating folder node
        tree.create_node(tag=colored_text_string,
                         identifier=p_root_id,
                         parent=parent_id)

        # increasing total dirs count
        total_dirs_num += 1

        # iterating over files
        for file in files:

            # updating scanned files num
            scanned_files_num += 1

            # printing execution message
            f_string = f'reading data... '
            f_string += f'| files: {total_files_num} '
            f_string += f'| folders: {total_dirs_num} '
            f_string += f'| scanned: {scanned_files_num} '
            print_progress_message(base_string=f_string,
                                   conditional=verbose)

            # getting file id
            f_id = p_root_id / file

            # getting file name
            file_name = f_id.name

            # checking if user has passed specific extension
            if specific_extension is not None:

                # checking if current file is of specified extension
                if not file.endswith(specific_extension):

                    # skipping to next file
                    continue

            # checking if user has passed specific keyword
            if keyword is not None:

                # checking if current file is of specified keyword
                if keyword not in file:

                    # skipping to next file
                    continue

            # adding file size to name
            if include_sizes:

                # getting file size
                file_size_in_bytes = get_file_size_in_bytes(file_path=f_id)

                # getting adjusted file size str
                adjusted_file_size = get_adjusted_file_size_string(file_size_in_bytes=file_size_in_bytes)

                # appending file size to file name
                file_name += f' ({adjusted_file_size})'

            # creating file node
            if include_files:

                # creating tree node from file
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

        # getting start path absolute path
        start_abs_path = get_absolute_path(path_to_file_or_folder=start_path)

        # getting folder size in bytes
        full_size = get_folder_size_in_bytes(path_to_folder=start_abs_path)

        # getting adjusted folder size string
        adjusted_full_size = get_adjusted_file_size_string(file_size_in_bytes=full_size)
        full_size_string = f', {adjusted_full_size}'

        # appending folder size to dirs and files string
        dirs_and_files_string += full_size_string

    # getting tree size
    size = tree.size()

    # checking if tree is empty
    if size == 0:

        # printing invalid input message
        f_string = 'Invalid input. Must be a directory.\n'
        f_string += 'Please check input and try again.'
        print(f_string)

    # if tree is not empty
    else:

        # getting console width
        console_width = get_console_width()

        # adding spacer
        f_string = 'showing tree...'
        f_string += ' ' * (console_width - 5)
        f_string += '\n'
        print_progress_message(base_string=f_string,
                               conditional=verbose)

        # displaying tree
        print(tree)

        # printing folder summary
        print(dirs_and_files_string)

######################################################################
# defining main function


def main():
    """
    Runs main code.
    :return: None.
    """
    # getting args dict
    args_dict = get_args_dict()

    # checking if user has passed specific folder
    start_path = args_dict['start_path'][0]

    # if user has not passed specific folder
    if start_path is None:

        # getting default start path (".")
        start_path = DEFAULT_START_PATH

    # checking whether tree should contain only dirs or also the files
    include_files_param = not(args_dict['dirs_only_flag'])

    # checking whether tree should contain file and folder size information
    include_sizes_param = args_dict['show_sizes_flag']

    # checking whether tree should contain file and folder counts information
    include_counts_param = args_dict['show_counts_flag']

    # checking whether display progress message while reading info
    verbose = args_dict['verbose']

    # checking if user has passed specific extension to be looked for
    specific_extension_param = args_dict['specified_extension']

    # checking if user has passed specific keyword to be looked for
    specific_keyword_param = args_dict['keyword']

    # getting subfolder level
    level = args_dict['level']

    # getting no recolor toggle
    no_recolor = args_dict['no_recolor']

    # checking whether to recolor folder strings
    windows = CURRENT_OS.startswith('win')

    # checking debug toggle

    # if debug toggle is on
    if DEBUG:

        # getting debug tree from default parameters
        pytree(start_path=DEBUG_FOLDER,
               include_files=True,
               include_sizes=True,
               include_counts=True,
               verbose=True,
               specific_extension='.txt',
               keyword=False,
               subfolder_level=1,
               no_recolor=True,
               force_absolute_ids=False,
               windows=False)

    # if debug toggle is off
    else:

        # getting tree based on parsed parameters
        pytree(start_path=start_path,
               include_files=include_files_param,
               include_sizes=include_sizes_param,
               include_counts=include_counts_param,
               verbose=verbose,
               specific_extension=specific_extension_param,
               keyword=specific_keyword_param,
               subfolder_level=level,
               no_recolor=no_recolor,
               force_absolute_ids=False,
               windows=windows)

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
