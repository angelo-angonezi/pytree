# converter module

# Code destined to converting a
# scanned tree dict into a
# treelib.Tree or pandas.DataFrame.

######################################################################
# imports

# importing required libraries
from treelib import Tree
from pandas import concat
from pandas import DataFrame
from pytree.shared.size import get_size_str
from pytree.shared.loc import get_loc_com_str

#####################################################################
# conversion related functions


def get_file_tag(path_dict: dict,
                 include_sizes: bool,
                 loc: bool
                 ) -> str:
    """
    Given a file path dict,
    returns its tag, based on
    specified attributes.
    """
    # getting base path dict info
    path_name = path_dict['name']

    # defining placeholder for file tag
    file_tag = f'{path_name}'

    # checking include sizes toggle
    if include_sizes:

        # getting additional path dict info
        file_size = path_dict['size']

        # getting size string
        size_str = get_size_str(file_size)

        # updating file tag
        file_tag += f' ({size_str})'

    # checking mode
    if loc:

        # getting additional path dict info
        file_loc = path_dict['loc']
        file_com = path_dict['com']

        # getting loc string
        loc_com_str = get_loc_com_str(loc=file_loc,
                                      com=file_com)

        # updating file tag
        file_tag += f' {{{loc_com_str}}}'

    # returning file tag
    return file_tag


def get_folder_tag(path_dict: dict,
                   include_counts: bool,
                   include_sizes: bool
                   ) -> str:
    """
    Given a folder path dict,
    returns its tag, based on
    specified attributes.
    """
    # getting base path dict info
    path_name = path_dict['name']

    # defining placeholder for folder tag
    folder_tag = f'{path_name}'

    # checking include counts toggle
    if include_counts:

        # getting additional path dict info
        items_count = path_dict['count']

        # updating folder tag
        folder_tag += f' [{items_count}]'

    # checking include sizes toggle
    if include_sizes:

        # getting additional path dict info
        folder_size = path_dict['size']

        # getting size string
        size_str = get_size_str(folder_size)

        # updating folder tag
        folder_tag += f' ({size_str})'

    # returning folder tag
    return folder_tag


def get_path_tag(path_dict: dict,
                 path_type: str,
                 include_counts: bool,
                 include_sizes: bool,
                 loc: bool
                 ) -> str:
    """
    Given a path dict, returns
    respective tag, according
    to path type.
    """
    # getting path is dir bool
    path_is_dir = (path_type == 'folder')

    # checking if path is dir
    if path_is_dir:

        # getting folder tag
        path_tag = get_folder_tag(path_dict=path_dict,
                                  include_counts=include_counts,
                                  include_sizes=include_sizes)

    else:

        # getting file tag
        path_tag = get_file_tag(path_dict=path_dict,
                                include_sizes=include_sizes,
                                loc=loc)

    # returning path tag
    return path_tag


def dict_to_tree(tree_dict: dict,
                 start_path: str,
                 dirs_only: bool,
                 include_counts: bool,
                 include_sizes: bool,
                 level: int,
                 loc: bool,
                 apply_level_filter: bool
                 ) -> Tree:
    """
    Converts folder/file description
    dict into a treelib.Tree object.
    """
    # defining base tree
    tree = Tree()

    # getting dict items
    dict_items = tree_dict.items()

    # iterating over dict items
    for item in dict_items:

        # getting current path/dict
        path, path_dict = item

        # getting base path dict info
        path_level = path_dict['level']
        path_type = path_dict['type']

        # getting path is file bool
        path_is_file = (path_type == 'file')

        # checking apply level filter
        if apply_level_filter:

            # checking if current level is above max
            if path_level > level:

                # skipping path
                continue

        # checking dirs only bool
        if dirs_only:

            # checking if path is file
            if path_is_file:

                # skipping current node
                continue

        # getting current path id/parent
        path_id = path_dict['path']
        parent_id = path_dict['parent']

        # getting current path tag
        path_tag = get_path_tag(path_dict=path_dict,
                                path_type=path_type,
                                include_counts=include_counts,
                                include_sizes=include_sizes,
                                loc=loc)

        # getting path is root bool
        path_is_root = (path_id == start_path)

        # checking if current path is root (first item)
        if path_is_root:

            # creating current node without specifying parent node (since it's root)
            tree.create_node(tag=path_tag,
                             identifier=path_id)

        else:

            # creating current node inside parent node
            tree.create_node(tag=path_tag,
                             identifier=path_id,
                             parent=parent_id)

    # returning tree
    return tree


def dict_to_df(tree_dict: dict,
               dirs_only: bool,
               include_counts: bool,
               include_sizes: bool,
               level: int,
               loc: bool,
               apply_level_filter: bool
               ) -> DataFrame:
    """
    Converts folder/file description
    dict into a pandas.DataFrame object.
    """
    # defining placeholder value for dfs list
    dfs_list = []

    # getting dict items
    dict_items = tree_dict.items()

    # iterating over dict items
    for item in dict_items:

        # getting current path/dict
        path, path_dict = item

        # getting base path dict info
        path_level = path_dict['level']
        path_type = path_dict['type']

        # getting path is file bool
        path_is_file = (path_type == 'file')

        # checking apply level filter
        if apply_level_filter:

            # checking if current level is above max
            if path_level > level:

                # skipping path
                continue

        # checking dirs only bool
        if dirs_only:

            # checking if path is file
            if path_is_file:

                # skipping current node
                continue

        # assembling current df
        current_df = DataFrame(path_dict,
                               index=[0])

        # appending current df to dfs list
        dfs_list.append(current_df)

    # concatenating dfs in dfs list
    final_df = concat(dfs_list,
                      ignore_index=True)

    # returning final df
    return final_df

######################################################################
# end of current module
