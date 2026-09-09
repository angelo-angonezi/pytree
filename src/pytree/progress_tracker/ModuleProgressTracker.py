# ModuleProgressTracker module

# Code destined to defining
# ModuleProgressTracker class and
# related attributes/methods.

######################################################################
# imports

# importing required libraries
from os import walk
from treelib import Tree
from pytree.shared.filter import is_cache
from pytree.shared.path import get_start_path
from pytree.shared.filter import get_skip_folder
from pytree.shared.global_vars import CACHE_FOLDERS
from pytree.progress_tracker.ProgressTracker import ProgressTracker

#####################################################################
# ModuleProgressTracker definition


class ModuleProgressTracker(ProgressTracker):
    """
    Defines ModuleProgressTracker class.
    """
    # defining ProgressTracker init
    def __init__(self) -> None:
        """
        Initializes a ModuleProgressTracker instance
        and defines class attributes.
        """
        # inheriting attributes and methods from ProgressTracker
        super().__init__()

        # defining current module specific attributes

        # folders
        self.folders_num = 0
        self.current_folder = 0

        # files
        self.files_num = 0
        self.current_file = 0

        # tree
        self.tree = Tree()
        self.show_tree = False

        # end string
        self.end_string = ''
        self.print_end_string = ''

    # overwriting class methods (using current module specific attributes)

    def get_progress_string(self) -> str:
        """
        Returns a formated progress
        string, based on current progress
        attributes.
        """
        # assembling current progress string
        progress_string = f''

        # checking if iterations total has already been obtained

        # if totals are still being updated
        if not self.totals_updated.is_set():

            # updating progress string based on attributes
            progress_string += f'scanning paths...'
            progress_string += f' {self.wheel_symbol}'
            progress_string += f' | folders: {self.folders_num}'
            progress_string += f' | files: {self.files_num}'
            progress_string += f' | scanned: {self.iterations_num}'
            progress_string += f' | elapsed time: {self.elapsed_time_str}'

        # if total iterations already obtained
        else:

            # updating progress string based on attributes
            progress_string += f'creating tree...'
            progress_string += f' {self.wheel_symbol}'
            progress_string += f' | folder: {self.current_folder}/{self.folders_num}'
            progress_string += f' | file: {self.current_file}/{self.files_num}'
            progress_string += f' | progress: {self.progress_percentage_str}'
            progress_string += f' | elapsed time: {self.elapsed_time_str}'
            progress_string += f' | ETC: {self.etc_str}'

        # returning progress string
        return progress_string

    def update_totals(self,
                      args_dict: dict
                      ) -> None:
        """
        Implements module specific method
        to update total iterations num.
        """
        # getting start path
        start_path = args_dict['start_path']
        start_path = get_start_path(start_path)

        # getting quiet bool
        quiet = args_dict['quiet']

        # getting show tree bool
        show_tree = (not quiet)

        # updating progress tracker attributes
        self.show_tree = show_tree

        # getting start is cache bool
        start_is_cache = is_cache(path=start_path,
                                  cache_folders=CACHE_FOLDERS)

        # getting folders/subfolders/files in start path
        folders_subfolders_files = walk(start_path,
                                        topdown=False)

        # iterating over folders/subfolders/files
        for item in folders_subfolders_files:

            # getting current folder path/subfolders/files
            folder_path, _, files = item

            # getting skip folder bool
            skip_folder = get_skip_folder(folder_path=folder_path,
                                          start_path=start_path,
                                          start_is_cache=start_is_cache,
                                          cache_folders=CACHE_FOLDERS)

            # checking whether to skip current folder
            if skip_folder:

                # skipping current folder
                continue

            # updating progress tracker attributes
            self.folders_num += 1

            # iterating over files in folder
            for _ in files:

                # updating progress tracker attributes
                self.files_num += 1
                self.iterations_num += 1

        # updating totals string
        totals_string = f'totals...'
        totals_string += f' | folders: {self.folders_num}'
        totals_string += f' | files: {self.files_num}'
        totals_string += f' | scanned: {self.iterations_num}'
        self.totals_string = totals_string

        # signaling totals updated
        self.signal_totals_updated()

    def normal_exit(self) -> None:
        """
        Implements module specific method
        to define what to print before
        terminating execution.
        """
        # printing spacer
        print('\n')

        # checking whether to show tree
        if self.show_tree:

            # showing tree
            self.tree.show()

        # printing end string
        print(self.end_string,
              end=self.print_end_string)

######################################################################
# end of current module
