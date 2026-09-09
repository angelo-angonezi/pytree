# filter module

# Code destined to storing filesystem
# skip/filtering related functions.

######################################################################
# imports

# importing required libraries
from os import R_OK
from os import X_OK
from os import stat
from os import access
from os.path import islink
from stat import FILE_ATTRIBUTE_REPARSE_POINT

######################################################################
# defining filter functions


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


def is_reparse_point(path: str) -> bool:
    """
    Given a path, returns True if it is a Windows
    reparse point (e.g. a junction created via
    "mklink /J"), which os.path.islink does not
    detect, and False otherwise (including on
    platforms without this file attribute).
    """
    # getting path stat result (not following symlinks, to inspect the path itself)
    path_stat = stat(path, follow_symlinks=False)

    # getting file attributes (Windows-only; absent on other platforms)
    file_attributes = getattr(path_stat, 'st_file_attributes', 0)

    # getting reparse point bool
    reparse_point_bool = bool(file_attributes & FILE_ATTRIBUTE_REPARSE_POINT)

    # returning reparse point bool
    return reparse_point_bool


def get_skip_folder(folder_path: str,
                    start_path: str,
                    start_is_cache: bool,
                    cache_folders: list
                    ) -> bool:
    """
    Given a path to a folder, returns
    True if folder should be skipped,
    and False otherwise.
    """
    # defining placeholder value for skip conditions list
    skip_conditions = []

    # getting path is root bool
    path_is_root = (folder_path == start_path)

    # checking if current path is root
    if not path_is_root:

        # running skip probes in a try/except, since a path that can't even be stat'd/accessed
        # (permission denied, an exotic/overlong path, a corrupted directory entry, etc.) should
        # be treated as skip rather than let the probe's OSError crash the whole scan
        try:

            # getting folder is symlink bool
            folder_is_symlink = islink(path=folder_path)

            # appending current condition to skip conditions list
            skip_conditions.append(folder_is_symlink)

            # getting folder is reparse point bool (junctions, which islink misses on Windows;
            # left unskipped, a junction pointing back at an ancestor/itself would make os.walk
            # recurse into it forever, since that's a hang rather than something to catch)
            folder_is_reparse_point = is_reparse_point(path=folder_path)

            # appending current condition to skip conditions list
            skip_conditions.append(folder_is_reparse_point)

            # getting folder is inaccessible bool (permission denied, vanished mid-scan, etc.)
            folder_is_inaccessible = not access(folder_path, R_OK | X_OK)

            # appending current condition to skip conditions list
            skip_conditions.append(folder_is_inaccessible)

            # checking if start path is cache
            if not start_is_cache:

                # getting folder is cache bool
                folder_is_cache = is_cache(path=folder_path,
                                           cache_folders=cache_folders)

                # appending current condition to skip conditions list
                skip_conditions.append(folder_is_cache)

        except OSError:

            # forcing skip bool, since the folder couldn't even be probed
            skip_conditions = [True]

    # getting skip bool
    skip_bool = any(skip_conditions)

    # returning skip bool
    return skip_bool


def get_skip_file(file_name: str,
                  extension: str | None,
                  keyword: str | None
                  ) -> bool:
    """
    Given a file name, returns True
    if file should be skipped, and
    False otherwise.
    """
    # defining placeholder value for skip conditions list
    skip_conditions = []

    # checking extension toggle
    if extension is not None:

        # getting file matches extension bool
        file_matches_extension = file_name.endswith(extension)

        # appending current condition to skip conditions list
        skip_conditions.append(file_matches_extension)

    # checking keyword toggle
    if keyword is not None:

        # getting file matches keyword bool
        file_matches_keyword = (keyword in file_name)

        # appending current condition to skip conditions list
        skip_conditions.append(file_matches_keyword)

    # reversing condition bools (skip should happen if they DON'T match)
    skip_conditions = [(not condition) for condition in skip_conditions]

    # getting skip bool
    skip_bool = any(skip_conditions)

    # returning skip bool
    return skip_bool

######################################################################
# end of current module
