# test_path module

# Code destined to testing shared/path.py's
# path splitting/depth/name/normalization
# functions.

######################################################################
# imports

# importing required libraries
from os import sep
from os.path import abspath
from pytree.shared.path import get_path_name
from pytree.shared.path import get_start_path
from pytree.shared.path import get_path_split
from pytree.shared.path import get_path_depth

######################################################################
# defining get_start_path test cases


def test_get_start_path_with_str() -> None:
    """
    Asserts get_start_path normalizes a plain str
    path via abspath.
    """
    # getting start path from a str
    start_path = get_start_path(start_path='.')

    # asserting it matches abspath's own normalization
    assert start_path == abspath('.')


def test_get_start_path_with_single_item_list() -> None:
    """
    Asserts get_start_path unwraps a single-item list
    (as produced by argparse's nargs='*') before normalizing.
    """
    # getting start path from a single-item list
    start_path = get_start_path(start_path=['.'])

    # asserting it matches abspath's own normalization
    assert start_path == abspath('.')


def test_get_start_path_with_multi_item_list_drops_extras() -> None:
    """
    Documents that get_start_path silently drops every item
    beyond the first when given a multi-item list.
    """
    # getting start path from a multi-item list
    start_path = get_start_path(start_path=['.', 'ignored_second_arg'])

    # asserting only the first item was normalized/used
    assert start_path == abspath('.')

######################################################################
# defining get_path_split/get_path_name/get_path_depth test cases


def test_get_path_split() -> None:
    """
    Asserts get_path_split splits a path by the OS
    separator, built portably via os.sep.join.
    """
    # building a path via os.sep.join to stay OS-portable
    path = sep.join(['root', 'sub1', 'sub2'])

    # getting path split
    path_split = get_path_split(path=path)

    # asserting split matches expected segments
    assert path_split == ['root', 'sub1', 'sub2']


def test_get_path_name() -> None:
    """
    Asserts get_path_name returns the final path segment.
    """
    # building a path via os.sep.join to stay OS-portable
    path = sep.join(['root', 'sub1', 'sub2'])

    # getting path name
    path_name = get_path_name(path=path)

    # asserting name matches final segment
    assert path_name == 'sub2'


def test_get_path_depth() -> None:
    """
    Asserts get_path_depth returns the number of
    path segments, including a Windows drive-letter
    segment counting as one.
    """
    # building a path via os.sep.join to stay OS-portable (drive letter
    # segment included, so this test is meaningful on Windows too)
    path = sep.join(['C:', 'root', 'sub1', 'sub2'])

    # getting path depth
    path_depth = get_path_depth(path=path)

    # asserting depth matches expected segment count
    assert path_depth == 4

######################################################################
# end of current module
