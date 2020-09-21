# pytree module
# Code destined to simulating 'tree' command from Linux, but running on python

######################################################################
# imports

from os import walk
from sys import argv
from treelib import Tree
from pathlib import Path

######################################################################
# defining auxiliary functions


def get_fs_tree(start_path: str = '.',
                include_files: bool = True,
                force_absolute_ids: bool = True
                ):
    """
    Returns a `treelib.Tree` representing the filesystem under `start_path`.
    You can then print the `Tree` object using `tree.show()`
    :param start_path: a string representing an absolute or relative path.
    :param include_files: a boolean (default `True`) indicating whether to also
    include the files in the tree.
    :param force_absolute_ids: a boolean (default `True`) indicating of tree node
    ids should be absolute. Otherwise they will be relative if start_path is relative,
    and absolute otherwise.
    """
    # creating tree instance
    tree = Tree()
    first = True

    # getting dirs and files
    all_files_and_folders = walk(start_path)

    # iterating over dirs and files
    for root, _, files in all_files_and_folders:
        p_root = Path(root)
        if first:
            parent_id = None
            first = False
        else:
            parent = p_root.parent
            parent_id = parent.absolute() if force_absolute_ids else parent

        # getting root id
        p_root_id = p_root.absolute() if force_absolute_ids else p_root
        tree.create_node(tag="%s/" % (p_root.name if p_root.name != "" else "."),
                         identifier=p_root_id, parent=parent_id)
        if include_files:
            # iterating over files
            for f in files:
                f_id = p_root_id / f
                tree.create_node(tag=f_id.name, identifier=f_id, parent=p_root_id)

    # returning tree
    return tree

######################################################################
# defining main function


def main():
    # trying to get argument
    try:
        directory = argv[1]

    # defining directory if user has not given any
    except IndexError:
        directory = '.'

    # getting tree
    tree = get_fs_tree(start_path=directory,
                       include_files=True,
                       force_absolute_ids=False)

    # getting tree size
    size = tree.size()

    # checking if tree is empty
    if size == 0:
        # printing message
        print('Invalid input directory.\nPlease check input and try again.\b')
    else:
        # displaying tree
        print(tree, end='\b')

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
