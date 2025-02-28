# pytree module

# code destined to simulating 'tree'
# command from Linux, running on python.

######################################################################
# imports

# importing required libraries
from os import sep
from os import walk
from os import system
from sys import stdout
from os import listdir
from time import sleep
from sys import platform
from os.path import join
from treelib import Tree
from pathlib import Path
from os.path import getsize
from argparse import ArgumentParser

#####################################################################
# debug toggle

DEBUG = False
CACHE_STR = '__pycache__'  # defines marker for cache folders (will be skipped)

#####################################################################
# defining default values and global parameters

CURRENT_OS = platform
DEBUG_FOLDER = join('.', 'test_folder')
DEFAULT_START_PATH = '.'
ONE_BYTE = 1
MULTIPLIER = 1024
ONE_KB = ONE_BYTE * MULTIPLIER
ONE_MB = ONE_KB * MULTIPLIER
ONE_GB = ONE_MB * MULTIPLIER
ONE_TB = ONE_GB * MULTIPLIER

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
                        action='store_true',
                        help='tree displays directories only, and does not show files inside folders',
                        default=False)

    parser.add_argument('-s', '--show-sizes',
                        dest='show_sizes_flag',
                        action='store_true',
                        help='tree displays files and folder sizes, in mega or gigabytes',
                        default=False)

    parser.add_argument('-c', '--show-counts',
                        dest='show_counts_flag',
                        action='store_true',
                        help='tree displays the number of files or folders inside each directory',
                        default=False)

    parser.add_argument('-v', '--verbose',
                        dest='verbose',
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

    level_help = 'defines depth level of recursion (until which subfolder tree will be created)'
    level_help += '[0=current, -1=all]'
    parser.add_argument('-l', '--level',
                        dest='level',
                        required=False,
                        type=int or None,
                        help=level_help,
                        default=-1)

    loop_help = 'defines whether to run code in loop (useful for tracking transfer/generation progress)'
    loop_help += '[overrides verbose to False]'
    parser.add_argument('-p', '--loop',
                        dest='loop',
                        action='store_true',
                        help=loop_help,
                        default=False)

    # creating arguments dictionary
    args_dict = vars(parser.parse_args())

    # returning the arguments dictionary
    return args_dict

######################################################################
# defining auxiliary functions


def clear_console(windows: bool) -> None:
    """
    Clears console window, using the respective
    OS clear command ('cls' for windows and 'clear' otherwise).
    :param windows: Boolean. Indicates whether program is running on windows system.
    :return: None.
    """
    # defining base clear command
    clear_command = 'clear'

    # checking if running on windows
    if windows:

        # updating clear command
        clear_command = 'cls'

    # running clear command
    system(clear_command)


def flush_string(string: str) -> None:
    """
    Given a string, writes and flushes it in the console using
    sys library, and resets cursor to the start of the line.
    (writes N backspaces at the end of line, where N = len(string)).
    :param string: String. Represents a message to be written in the console.
    :return: None.
    """
    # getting string length
    string_len = len(string)

    # creating backspace line
    backspace_line = '\b' * string_len

    # writing string
    stdout.write(string)

    # flushing console
    stdout.flush()

    # resetting cursor to start of the line
    stdout.write(backspace_line)


def print_progress_message(base_string: str,
                           conditional: bool
                           ) -> None:
    """
    Checks whether given conditional is
    True, and prints given string if so.
    :param base_string: String. Represents a progress message.
    :param conditional: Boolean. Represents a conditional to be checked.
    :return: None.
    """
    # checking conditional
    if conditional:

        # printing message
        flush_string(string=base_string)


def get_absolute_path(path_to_file_or_folder: str) -> Path:
    """
    Given a path to a file or folder, returns its absolute path.
    :param path_to_file_or_folder: String. Represents partial path.
    :return: String. Represents absolute system path.
    """
    # getting partial path
    partial_path = Path(path_to_file_or_folder)

    # getting absolute path
    absolute_path = partial_path.absolute()

    # returning absolute path
    return absolute_path


def from_bytes_to_kilobytes(value_in_bytes: int) -> float:
    """
    Given a value in bytes, returns equivalent value in kilobytes.
    :param value_in_bytes: Integer. Represents file size value in bytes.
    :return: Float. Represents size value in kilobytes.
    """
    # getting value in kilobytes
    value_in_kilobytes = value_in_bytes / ONE_KB

    # returning value in kilobytes
    return value_in_kilobytes


def from_bytes_to_megabytes(value_in_bytes: int) -> float:
    """
    Given a value in bytes, returns equivalent value in megabytes.
    :param value_in_bytes: Integer. Represents file size value in bytes.
    :return: Float. Represents size value in megabytes.
    """
    # getting value in megabytes
    value_in_megabytes = value_in_bytes / ONE_MB

    # returning value in megabytes
    return value_in_megabytes


def from_bytes_to_gigabytes(value_in_bytes: int) -> float:
    """
    Given a value in bytes, returns equivalent value in gigabytes.
    :param value_in_bytes: Integer. Represents file size value in bytes.
    :return: Float. Represents size value in gigabytes.
    """
    # getting value in gigabytes
    value_in_gigabytes = value_in_bytes / ONE_GB

    # returning value in gigabytes
    return value_in_gigabytes


def from_bytes_to_terabytes(value_in_bytes: int) -> float:
    """
    Given a value in bytes, returns equivalent value in terabytes.
    :param value_in_bytes: Integer. Represents file size value in bytes.
    :return: Float. Represents size value in terabytes.
    """
    # getting value in gigabytes
    value_in_gigabytes = value_in_bytes / ONE_TB

    # returning value in gigabytes
    return value_in_gigabytes


def get_adjusted_file_size_string(file_size_in_bytes: int) -> str:
    """
    Given file disk size in bytes, returns string containing file size in
    bytes, megabytes, or gigabytes, according to file size.
    :param file_size_in_bytes: String. Represents a path to a file or folder.
    :return: String. Represents file disk size in bytes, megabytes, or gigabytes.
    """
    # if file size is larger than a terabyte
    if file_size_in_bytes >= ONE_TB:

        # getting file size in terabytes
        adjusted_file_size = from_bytes_to_terabytes(value_in_bytes=file_size_in_bytes)
        adjusted_file_size = round(adjusted_file_size, 2)

        # writing size string in gigabytes
        adjusted_size_string = f'{adjusted_file_size} tb'

    # if file size is larger than a gigabyte
    elif file_size_in_bytes >= ONE_GB:

        # getting file size in gigabytes
        adjusted_file_size = from_bytes_to_gigabytes(value_in_bytes=file_size_in_bytes)
        adjusted_file_size = round(adjusted_file_size, 2)

        # writing size string in gigabytes
        adjusted_size_string = f'{adjusted_file_size} gb'

    # if file size is larger than a megabyte (but smaller than a gb)
    elif file_size_in_bytes >= ONE_MB:

        # getting file size in megabytes
        adjusted_file_size = from_bytes_to_megabytes(value_in_bytes=file_size_in_bytes)
        adjusted_file_size = round(adjusted_file_size, 2)

        # writing size string in megabytes
        adjusted_size_string = f'{adjusted_file_size} mb'

    # if file size is larger than a kilobyte (but smaller than a gb or mb)
    elif file_size_in_bytes >= ONE_KB:

        # getting file size in kilobytes
        adjusted_file_size = from_bytes_to_kilobytes(value_in_bytes=file_size_in_bytes)
        adjusted_file_size = round(adjusted_file_size, 2)

        # writing size string in kilobytes
        adjusted_size_string = f'{adjusted_file_size} kb'

    # if file size is smaller than a kilobyte
    else:

        # writing size string in bytes
        adjusted_size_string = f'{file_size_in_bytes} bytes'

    # returning adjusted size string
    return adjusted_size_string


def get_file_size_in_bytes(file_path: Path) -> int:
    """
    Given a path to a file, returns file disk size in bytes.
    :param file_path: Path. Represents a path to a file.
    :return: Integer. Represents file disk size in bytes.
    """
    # getting file size
    file_size = getsize(file_path)

    # returning file size
    return file_size


def get_folder_size_in_bytes(path_to_folder: Path) -> int:
    """
    Given a path to a folder, returns folder disk size in bytes.
    :param path_to_folder: Path. Represents a path to a folder.
    :return: Integer. Represents folder disk size in bytes.
    """
    # defining placeholder variable for full dir size
    full_dir_size = 0

    # getting files and dirs in start folder
    everything_in_folder = walk(path_to_folder)

    # iterating over dirs
    for root, _, files in everything_in_folder:

        # iterating over files
        for file in files:

            # checking if file is cache-related
            if CACHE_STR in root:

                # skipping file
                continue

            # getting file path
            file_path = join(root, file)

            # getting absolute file path
            file_abs_path = get_absolute_path(path_to_file_or_folder=file_path)

            # getting file size
            file_size = get_file_size_in_bytes(file_path=file_abs_path)

            # adding file size to dir size
            full_dir_size += file_size

    # returning full dir size
    return full_dir_size


def get_number_of_files_inside_folder(path_to_folder: Path) -> int:
    """
    Given a path to a folder, returns number of files or folders inside given folder.
    :param path_to_folder: String. Represents a path to a folder.
    :return: Integer. Represents number of files or folders inside given folder.
    """
    # getting all files and folders inside given folder
    all_files_and_folders_inside_folder = listdir(path_to_folder)

    # getting files/folders count
    file_and_folder_count = len(all_files_and_folders_inside_folder)

    # returning count
    return file_and_folder_count


def pytree(start_path: str = '.',
           include_files: bool = True,
           include_sizes: bool = False,
           include_counts: bool = False,
           verbose: bool = True,
           specific_extension: str or None = None,
           keyword: str or None = None,
           subfolder_level: int = 1,
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

        # checking if file is cache-related
        if CACHE_STR in root:

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

        # checking whether to recolor string
        if not windows:

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

        # adding spacer
        f_string = 'showing tree...'
        f_string += ' ' * 50
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

    # checking whether to loop code
    loop = args_dict['loop']

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
               force_absolute_ids=False,
               windows=False)

    # if debug toggle is off
    else:

        # checking whether to run code in loop
        if loop:

            # starting endless loop
            while True:

                # clearing console
                clear_console(windows=windows)

                # getting tree based on parsed parameters
                pytree(start_path=start_path,
                       include_files=include_files_param,
                       include_sizes=include_sizes_param,
                       include_counts=include_counts_param,
                       verbose=False,
                       specific_extension=specific_extension_param,
                       keyword=specific_keyword_param,
                       subfolder_level=level,
                       force_absolute_ids=False,
                       windows=windows)

                # sleeping
                sleep(2)

        # getting tree based on parsed parameters
        pytree(start_path=start_path,
               include_files=include_files_param,
               include_sizes=include_sizes_param,
               include_counts=include_counts_param,
               verbose=verbose,
               specific_extension=specific_extension_param,
               keyword=specific_keyword_param,
               subfolder_level=level,
               force_absolute_ids=False,
               windows=windows)

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
