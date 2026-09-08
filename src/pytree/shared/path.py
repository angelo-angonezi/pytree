# path module

# Code destined to storing path
# parsing related functions.

######################################################################
# imports

# importing required libraries
from os.path import sep
from os.path import abspath

######################################################################
# defining path functions


def get_start_path(start_path: str | list) -> str:
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
    start_path = abspath(path=start_path)  # noqa

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


def get_path_name(path: str) -> str:
    """
    Given a full path, returns its
    name (final split item).
    """
    # getting path split
    path_split = get_path_split(path=path)

    # getting path name
    path_name = path_split[-1]

    # returning path name
    return path_name


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

######################################################################
# end of current module
