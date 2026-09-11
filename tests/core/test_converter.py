# test_converter module

# Code destined to testing get_file_tag/get_folder_tag/get_path_tag
# formatting and dict_to_tree/dict_to_df conversion, using small,
# hand-built tree dicts (converter functions never touch the
# filesystem, so plain string identifiers are enough).

######################################################################
# imports

# importing required libraries
from pytest import raises
from pytree.core.converter import dict_to_df
from pytree.core.converter import dict_to_tree
from pytree.core.converter import get_path_tag
from pytree.core.converter import get_file_tag
from pytree.core.converter import get_folder_tag

######################################################################
# defining get_file_tag test cases


def test_get_file_tag_name_only() -> None:
    """
    Asserts get_file_tag returns just the name when both
    include_sizes and loc are disabled.
    """
    # defining minimal file path dict
    path_dict = {'name': 'file_a.py'}

    # getting file tag with both toggles disabled
    file_tag = get_file_tag(path_dict=path_dict,
                            include_sizes=False,
                            loc=False)

    # asserting tag is the bare name
    assert file_tag == 'file_a.py'


def test_get_file_tag_with_size_and_loc() -> None:
    """
    Asserts get_file_tag appends a size suffix and a loc/comment
    suffix when both toggles are enabled.
    """
    # defining file path dict with size/loc/com fields
    path_dict = {'name': 'file_a.py',
                'size': 1024,
                'loc': 2,
                'com': 2}

    # getting file tag with both toggles enabled
    file_tag = get_file_tag(path_dict=path_dict,
                            include_sizes=True,
                            loc=True)

    # asserting size and loc/com suffixes are present
    assert file_tag.startswith('file_a.py (1 kb)')
    assert '2 lines of code (50%), 2 comments (50%)' in file_tag

######################################################################
# defining get_folder_tag test cases


def test_get_folder_tag_name_only() -> None:
    """
    Asserts get_folder_tag returns just the name when both
    include_counts and include_sizes are disabled.
    """
    # defining minimal folder path dict
    path_dict = {'name': 'sub1'}

    # getting folder tag with both toggles disabled
    folder_tag = get_folder_tag(path_dict=path_dict,
                                include_counts=False,
                                include_sizes=False)

    # asserting tag is the bare name
    assert folder_tag == 'sub1'


def test_get_folder_tag_with_counts_and_size() -> None:
    """
    Asserts get_folder_tag appends a count suffix and a size suffix
    when both toggles are enabled.
    """
    # defining folder path dict with count/size fields
    path_dict = {'name': 'sub1',
                'count': 2,
                'size': 2048}

    # getting folder tag with both toggles enabled
    folder_tag = get_folder_tag(path_dict=path_dict,
                                include_counts=True,
                                include_sizes=True)

    # asserting count and size suffixes are present, in order
    assert folder_tag == 'sub1 [2] (2 kb)'

######################################################################
# defining get_path_tag test cases


def test_get_path_tag_dispatches_by_type() -> None:
    """
    Asserts get_path_tag dispatches to get_folder_tag for a folder
    path dict and to get_file_tag for a file path dict.
    """
    # defining folder and file path dicts
    folder_path_dict = {'name': 'sub1', 'count': 1}
    file_path_dict = {'name': 'file_a.py'}

    # getting folder tag via get_path_tag
    folder_tag = get_path_tag(path_dict=folder_path_dict,
                              path_type='folder',
                              include_counts=True,
                              include_sizes=False,
                              loc=False)

    # getting file tag via get_path_tag
    file_tag = get_path_tag(path_dict=file_path_dict,
                            path_type='file',
                            include_counts=False,
                            include_sizes=False,
                            loc=False)

    # asserting each dispatched to the correct formatting
    assert folder_tag == 'sub1 [1]'
    assert file_tag == 'file_a.py'

######################################################################
# shared tree dict fixture for dict_to_tree/dict_to_df tests


def build_tree_dict() -> dict:
    """
    Returns a small, hand-built tree dict (root folder, one
    subfolder, one file inside it, and one file directly under
    root), in parent-before-child key order, with size/count/loc/com
    fields on every entry so it can drive any flag combination.
    """
    # assembling and returning tree dict, in parent-before-child order
    return {'root': {'name': 'root', 'path': 'root', 'level': 0, 'parent': '',
                     'type': 'folder', 'size': 30, 'count': 2, 'loc': 1, 'com': 0},
           'root/sub': {'name': 'sub', 'path': 'root/sub', 'level': 1, 'parent': 'root',
                       'type': 'folder', 'size': 10, 'count': 1, 'loc': 1, 'com': 0},
           'root/sub/file.py': {'name': 'file.py', 'path': 'root/sub/file.py', 'level': 2,
                                'parent': 'root/sub', 'type': 'file', 'size': 10,
                                'loc': 1, 'com': 0},
           'root/file2.txt': {'name': 'file2.txt', 'path': 'root/file2.txt', 'level': 1,
                             'parent': 'root', 'type': 'file', 'size': 20,
                             'loc': 0, 'com': 0}}

######################################################################
# defining dict_to_tree test cases


def test_dict_to_tree_builds_full_structure() -> None:
    """
    Asserts dict_to_tree builds all four nodes, with the root node
    created without a parent and the others attached under their
    correct parent identifiers.
    """
    # getting tree dict
    tree_dict = build_tree_dict()

    # converting to tree, with no filters active
    tree = dict_to_tree(tree_dict=tree_dict,
                        start_path='root',
                        dirs_only=False,
                        include_counts=True,
                        include_sizes=True,
                        level=-1,
                        loc=True,
                        apply_level_filter=False)

    # asserting all four nodes were created
    assert tree.size() == 4

    # asserting parent/child wiring is correct
    assert tree.parent('root/sub').identifier == 'root'
    assert tree.parent('root/sub/file.py').identifier == 'root/sub'
    assert tree.parent('root/file2.txt').identifier == 'root'


def test_dict_to_tree_dirs_only_excludes_files() -> None:
    """
    Asserts dict_to_tree, with dirs_only=True, includes only folder
    nodes.
    """
    # getting tree dict
    tree_dict = build_tree_dict()

    # converting to tree with dirs_only enabled
    tree = dict_to_tree(tree_dict=tree_dict,
                        start_path='root',
                        dirs_only=True,
                        include_counts=False,
                        include_sizes=False,
                        level=-1,
                        loc=False,
                        apply_level_filter=False)

    # asserting only the two folder nodes were created
    assert tree.size() == 2
    assert tree.contains('root')
    assert tree.contains('root/sub')
    assert not tree.contains('root/sub/file.py')


def test_dict_to_tree_level_filter_excludes_deeper_nodes() -> None:
    """
    Asserts dict_to_tree, with apply_level_filter=True and level=1,
    excludes nodes above the given level (root/sub/file.py, at
    level 2).
    """
    # getting tree dict
    tree_dict = build_tree_dict()

    # converting to tree with a level filter of 1
    tree = dict_to_tree(tree_dict=tree_dict,
                        start_path='root',
                        dirs_only=False,
                        include_counts=False,
                        include_sizes=False,
                        level=1,
                        loc=False,
                        apply_level_filter=True)

    # asserting the level-2 file was excluded, others kept
    assert tree.size() == 3
    assert not tree.contains('root/sub/file.py')
    assert tree.contains('root/file2.txt')

######################################################################
# defining dict_to_df test cases


def test_dict_to_df_normal_case_includes_all_rows() -> None:
    """
    Asserts dict_to_df, with no filters active, returns a DataFrame
    with one row per tree dict entry.
    """
    # getting tree dict
    tree_dict = build_tree_dict()

    # converting to df with no filters active
    tree_df = dict_to_df(tree_dict=tree_dict,
                         dirs_only=False,
                         include_counts=True,
                         include_sizes=True,
                         level=-1,
                         loc=True,
                         apply_level_filter=False)

    # asserting one row per tree dict entry
    assert len(tree_df) == len(tree_dict)
    assert set(tree_df['name']) == {'root', 'sub', 'file.py', 'file2.txt'}


def test_dict_to_df_dirs_only_filters_files_out() -> None:
    """
    Asserts dict_to_df, with dirs_only=True, returns only folder
    rows.
    """
    # getting tree dict
    tree_dict = build_tree_dict()

    # converting to df with dirs_only enabled
    tree_df = dict_to_df(tree_dict=tree_dict,
                         dirs_only=True,
                         include_counts=True,
                         include_sizes=True,
                         level=-1,
                         loc=True,
                         apply_level_filter=False)

    # asserting only the two folder rows remain
    assert len(tree_df) == 2
    assert set(tree_df['type']) == {'folder'}


def test_dict_to_df_empty_result_raises_value_error() -> None:
    """
    Asserts dict_to_df raises ValueError (via pandas.concat([])) when
    the active filters exclude every entry - documenting the known,
    unguarded gap for an all-excluding level filter.
    """
    # getting tree dict
    tree_dict = build_tree_dict()

    # converting to df with a level filter excluding even the root (level 0)
    with raises(ValueError):

        # calling dict_to_df, expected to raise
        dict_to_df(tree_dict=tree_dict,
                  dirs_only=False,
                  include_counts=False,
                  include_sizes=False,
                  level=-1,
                  loc=False,
                  apply_level_filter=True)

######################################################################
# end of current module
