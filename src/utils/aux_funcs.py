# auxiliary functions module

# Code destined to storing auxiliary
# functions to main module.

######################################################################
# imports

# importing required libraries
import __main__
from os import walk
from os import system
from os import listdir
from sys import stdout
from sys import platform
from os.path import join
from pathlib import Path
from os.path import getsize
from os import get_terminal_size
from src.utils.global_vars import ONE_KB
from src.utils.global_vars import ONE_MB
from src.utils.global_vars import ONE_GB
from src.utils.global_vars import ONE_TB
from src.utils.global_vars import CACHE_FOLDERS

######################################################################
# defining auxiliary functions


def get_console_width() -> int:
    """
    Returns current console width.
    """
    # getting console dimensions
    width, _ = get_terminal_size()

    # returning console width
    return width


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

            # getting cache bool list
            cache_bool_list = [cache_str in root for cache_str in CACHE_FOLDERS]

            # getting cache bool
            cache_bool = any(cache_bool_list)

            # checking if file is cache-related
            if cache_bool:

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


def get_number_string(num: int or float,
                      digits: int = 2
                      ) -> str:
    """
    Given a number, returns formatted
    number with leading zeroes so that
    the number of digits param is preserved.
    """
    # getting is int bool
    num_is_int = isinstance(num, int)

    # checking if number is int
    if num_is_int:

        # formating number string
        number_string = f'{num:0{digits}d}'

    else:

        # formating number string
        number_string = f'{num:4.{digits}f}'

    # returning formatted number string
    return number_string


def get_time_str(time_in_seconds: int) -> str:
    """
    Given a time in seconds, returns time in
    adequate format (seconds, minutes or hours).
    """
    # checking whether seconds > 60
    if time_in_seconds >= 60:

        # converting time to minutes
        time_in_minutes = time_in_seconds / 60

        # checking whether minutes > 60
        if time_in_minutes >= 60:

            # converting time to hours
            time_in_hours = time_in_minutes / 60

            # defining time string based on hours
            defined_time = round(time_in_hours)
            time_string = f'{defined_time}h'

        else:

            # defining time string based on minutes
            defined_time = round(time_in_minutes)
            time_string = f'{defined_time}m'

    else:

        # defining time string based on seconds
        defined_time = round(time_in_seconds)
        time_string = f'{defined_time}s'

    # returning time string
    return time_string

######################################################################
# end of current module
