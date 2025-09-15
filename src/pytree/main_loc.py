# pytree main loc module

print('initializing...')  # noqa

# Code destined to scanning python files lines of
# code count in given input folder, and creating
# tree structure to print on console.

######################################################################
# imports

# importing required libraries
print('importing required libraries...')  # noqa
from argparse import ArgumentParser
from pytree.classes.PyTree import PyTree
from pytree.utils.aux_funcs import get_start_path
from pytree.classes.PyTree import ModuleProgressTracker
print('all required libraries successfully imported.')  # noqa

#####################################################################
# argument parsing related functions


def get_args_dict() -> dict:
    """
    Parses the arguments and returns a dictionary of the arguments.
    :return: Dictionary. Represents the parsed arguments.
    """
    # defining program description
    description = "pytree-loc - a python cli utility for counting lines of code in python projects"

    # creating a parser instance
    parser = ArgumentParser(description=description)

    # start path param
    parser.add_argument('start_path',
                        nargs='*',
                        type=str or list,
                        help='defines path to directory to start building the tree',
                        default='.')

    # dirs only param
    parser.add_argument('-d', '--dirs-only',
                        dest='dirs_only',
                        required=False,
                        action='store_true',
                        help='tree displays directories only, and does not show files inside folders',
                        default=False)

    # show sizes param
    parser.add_argument('-s', '--show-sizes',
                        dest='show_sizes',
                        required=False,
                        action='store_true',
                        help='tree displays files and folder sizes, in mega or gigabytes',
                        default=False)

    # show counts param
    parser.add_argument('-c', '--show-counts',
                        dest='show_counts',
                        required=False,
                        action='store_true',
                        help='tree displays the number of files or folders inside each directory',
                        default=False)

    # keyword param
    parser.add_argument('-k', '--keyword',
                        dest='keyword',
                        required=False,
                        type=str or None,
                        help='tree will include only files that contain specific keyword on file name',
                        default=None)

    # level param
    parser.add_argument('-l', '--level',
                        dest='level',
                        required=False,
                        type=int or None,
                        help="defines tree's depth (until which subfolder tree will be created) [0=start_path, -1=all]",
                        default=-1)

    # creating arguments dictionary
    args_dict = vars(parser.parse_args())

    # returning the arguments dictionary
    return args_dict

######################################################################
# defining auxiliary functions


def pytree(start_path: str,
           dirs_only: bool,
           include_counts: bool,
           include_sizes: bool,
           extension: str,
           keyword: str,
           level: int,
           mode: str,
           progress_tracker: ModuleProgressTracker
           ) -> None:
    """
    Prints folder structure tree
    on the console.
    """
    # initializing PyTree object
    tree = PyTree(start_path=start_path,
                  dirs_only=dirs_only,
                  include_counts=include_counts,
                  include_sizes=include_sizes,
                  extension=extension,
                  keyword=keyword,
                  level=level,
                  mode=mode,
                  progress_tracker=progress_tracker)

    # running pytree main
    tree.run()


def parse_and_run(args_dict: dict,
                  progress_tracker: ModuleProgressTracker
                  ) -> None:
    """
    Extracts args from args_dict
    and runs module function.
    """
    # getting start path
    start_path = args_dict['start_path']
    start_path = get_start_path(start_path)

    # getting dirs only bool
    dirs_only = args_dict['dirs_only']

    # getting include counts bool
    include_counts = args_dict['show_counts']

    # getting include sizes bool
    include_sizes = args_dict['show_sizes']

    # getting extension
    extension = '.py'

    # getting keyword
    keyword = args_dict['keyword']

    # getting level
    level = args_dict['level']

    # getting mode
    mode = 'loc'

    # running pytree function
    pytree(start_path=start_path,
           dirs_only=dirs_only,
           include_counts=include_counts,
           include_sizes=include_sizes,
           extension=extension,
           keyword=keyword,
           level=level,
           mode=mode,
           progress_tracker=progress_tracker)

######################################################################
# defining main function


def main():
    """Runs main code."""
    # initializing current module progress tracker instance
    progress_tracker = ModuleProgressTracker()

    # running code in separate thread
    progress_tracker.run(function=parse_and_run,
                         args_parser=get_args_dict)

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
