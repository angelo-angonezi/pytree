# auxiliary functions module

# Code destined to storing auxiliary
# functions to main module.

######################################################################
# imports

# importing required libraries
from sys import stdout
from os.path import sep
from os.path import abspath
from os import get_terminal_size
from utils.global_vars import ONE_KB
from utils.global_vars import ONE_MB
from utils.global_vars import ONE_GB
from utils.global_vars import ONE_TB

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
    """
    # getting console width
    console_width = get_console_width()

    # getting string length
    string_len = len(string)

    # getting size difference
    width_diff = console_width - string_len

    # discounting from width diff to avoid console overflow
    width_diff -= 5

    # getting spacer
    empty_space = ' ' * width_diff

    # updating string
    string += empty_space

    # getting updated string length
    string_len = len(string)

    # creating backspace line
    backspace_line = '\b' * string_len

    # writing string
    stdout.write(string)

    # flushing console
    stdout.flush()

    # resetting cursor to start of the line
    stdout.write(backspace_line)


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


def is_cache(path: str,
             cache_folders: list
             ) -> bool:
    """
    Given a path to a folder/file,
    returns True if path contains
    cache keywords, else False.
    """
    # getting cache bool list
    cache_bool_list = [cache_str in path for cache_str in cache_folders]

    # getting cache bool
    cache_bool = any(cache_bool_list)

    # returning cache bool
    return cache_bool


def get_start_path(start_path: str or list) -> str:
    """
    Given a parsed start path,
    returns formatted start path.
    """
    # getting path is list bool
    path_is_list = isinstance(start_path, list)

    # checking if path is list
    if path_is_list:

        # updating start path
        start_path = start_path[0]

    # normalizing path
    start_path = abspath(path=start_path)

    # returning start path
    return start_path


def get_path_split(path: str) -> list:
    """
    Given a path, returns its split
    by os separator.
    """
    # getting path split
    path_split = path.split(sep)

    # returning path split
    return path_split


def get_path_depth(path: str) -> int:
    """
    Given a path, returns its depth.
    """
    # getting current path split
    path_split = get_path_split(path=path)

    # getting path depth
    path_depth = len(path_split)

    # returning path depth
    return path_depth


def get_size_str(size_in_bytes: int) -> str:
    """
    Given a file/folder size in bytes,
    returns a string in human readable
    format.
    """
    # defining placeholder value for unit str/normalizer
    unit_str = 'bytes'
    normalizer = 1

    # checking if size in bytes exceeds a terabyte
    if size_in_bytes >= ONE_TB:

        # updating unit str/normalizer
        unit_str = 'tb'
        normalizer *= ONE_TB

    # checking if size in bytes exceeds a gigabyte
    elif size_in_bytes >= ONE_GB:

        # updating unit str/normalizer
        unit_str = 'gb'
        normalizer *= ONE_GB

    # checking if size in bytes exceeds a megabyte
    elif size_in_bytes >= ONE_MB:

        # updating unit str/normalizer
        unit_str = 'mb'
        normalizer *= ONE_MB

    # checking if size in bytes exceeds a kilobyte
    elif size_in_bytes >= ONE_KB:

        # updating unit str/normalizer
        unit_str = 'kb'
        normalizer *= ONE_KB

    # getting adjusted size
    adjusted_size = size_in_bytes / normalizer

    # rounding value
    adjusted_size = round(adjusted_size)

    # assembling size str
    size_str = f'{adjusted_size} {unit_str}'

    # returning size str
    return size_str

######################################################################
# end of current module
