# PyTree module

# Code destined to defining
# PyTree class and related
# attributes/methods.

######################################################################
# imports

# importing required libraries
from os import walk
from treelib import Tree
from os.path import join
from os.path import split
from os.path import abspath
from os.path import dirname
from os.path import getsize
from os import _exit  # noqa
from pytree.utils.aux_funcs import is_cache
from pytree.utils.aux_funcs import reverse_dict
from pytree.utils.aux_funcs import get_size_str
from pytree.utils.aux_funcs import get_skip_bool
from pytree.utils.aux_funcs import get_path_depth
from pytree.utils.aux_funcs import get_start_path
from pytree.utils.global_vars import CACHE_FOLDERS
from pytree.classes.ProgressTracker import ProgressTracker

#####################################################################
# progress tracking related functions


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
        self.tree = None

        # end string
        self.end_string = ''

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

        # getting folders/subfolders/files in start path
        folders_subfolders_files = walk(start_path,
                                        topdown=False)

        # iterating over folders/subfolders/files
        for item in folders_subfolders_files:

            # getting current folder path/subfolders/files
            folder_path, _, files = item

            # getting skip folder bool
            skip_folder = get_skip_bool(folder_path=folder_path,
                                        start_path=start_path,
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

        # showing tree
        self.tree.show()

        # printing end string
        print(self.end_string,
              end='')

#####################################################################
# PyTree definition


class PyTree:
    """
    Defines PyTree class.
    """
    def __init__(self,
                 start_path: str,
                 dirs_only: bool,
                 include_counts: bool,
                 include_sizes: bool,
                 extension: str or None,
                 keyword: str or None,
                 level: int,
                 cache_folders: list = CACHE_FOLDERS,
                 progress_tracker: ModuleProgressTracker = ModuleProgressTracker
                 ) -> None:
        """
        Initializes a PyTree instance
        and defines class attributes.
        """
        # creating attributes from input
        self.start_path = start_path
        self.dirs_only = dirs_only
        self.include_counts = include_counts
        self.include_sizes = include_sizes
        self.extension = extension
        self.keyword = keyword
        self.level = level
        self.cache_folders = cache_folders
        self.progress_tracker = progress_tracker

        # getting start level
        self.start_level = get_path_depth(path=self.start_path)

        # getting apply level filter bool
        self.apply_level_filter = (self.level != -1)

        # defining base tree dict
        self.tree_dict = {}

        # totals (keeping separate from ProgressTracker since it counts per subfolder)
        self.total_folders = 0
        self.total_files = 0
        self.total_size = 0

        # defining placeholder values for current folder size/count
        self.current_folder_size = 0
        self.current_items_count = 0

        # valid files
        self.valid_files = 0

    def get_path_level(self,
                       path: str
                       ) -> int:
        """
        Given a path, returns its
        depth normalized by start
        path depth.
        """
        # getting current path depth
        path_depth = get_path_depth(path=path)

        # getting path level
        path_level = path_depth - self.start_level

        # returning path level
        return path_level

    def get_path_dict(self,
                      name: str,
                      path: str
                      ) -> dict:
        """
        Given a path, returns its
        base description dict.
        """
        # getting base path info
        path_level = self.get_path_level(path=path)
        path_id = abspath(path=path)
        parent_folder = dirname(p=path)
        parent_id = abspath(path=parent_folder)

        # assembling base path dict
        path_dict = {'name': name,
                     'path': path_id,
                     'level': path_level,
                     'parent': parent_id}

        # returning base path dict
        return path_dict

    def get_file_dict(self,
                      file_name: str,
                      file_path: str
                      ) -> dict:
        """
        Given a file path, returns
        its description dict.
        """
        # getting base path dict
        base_dict = self.get_path_dict(name=file_name,
                                       path=file_path)

        # updating base dict
        base_dict['type'] = 'file'

        # checking include sizes toggle
        if self.include_sizes:

            # getting file size
            file_size = getsize(filename=file_path)

            # updating base dict
            base_dict['size'] = file_size

        # returning base dict
        return base_dict

    def get_folder_dict(self,
                        folder_name: str,
                        folder_path: str
                        ) -> dict:
        """
        Given a folder path, returns
        its description dict.
        """
        # getting base path dict
        base_dict = self.get_path_dict(name=folder_name,
                                       path=folder_path)

        # updating base dict
        base_dict['type'] = 'folder'

        # checking include sizes toggle
        if self.include_sizes:

            # updating base dict
            base_dict['size'] = self.current_folder_size

        # checking include counts toggle
        if self.include_counts:

            # updating base dict
            base_dict['count'] = self.current_items_count

        # returning base dict
        return base_dict

    def scan_file(self,
                  file_path: str
                  ) -> None:
        pass

    def scan_folder(self,
                    folder_path: str
                    ) -> None:
        pass

    def get_tree_dict(self) -> dict:
        """
        Docstring.
        """
        # getting folders/subfolders/files in start path
        folders_subfolders_files = walk(self.start_path,
                                        topdown=False)

        # iterating over folders/subfolders/files
        for item in folders_subfolders_files:

            # getting current folder path/subfolders/files
            folder_path, subfolders, files = item

            # getting skip folder bool
            skip_folder = get_skip_bool(folder_path=folder_path,
                                        start_path=self.start_path,
                                        cache_folders=self.cache_folders)

            # checking whether to skip current folder
            if skip_folder:

                # skipping current folder
                continue

            # updating progress tracker attributes
            self.progress_tracker.current_folder += 1

            # updating totals
            self.total_folders += 1

            # sorting subfolders/files alphabetically
            subfolders = sorted(subfolders)
            files = sorted(files)

            # getting current folder split
            folder_split = split(p=folder_path)

            # getting current folder name
            folder_name = folder_split[-1]

            # getting current files num
            files_num = len(files)

            # updating progress tracker attributes
            self.progress_tracker.files_num = files_num

            # resetting progress tracker attributes
            self.progress_tracker.current_file = 0
            self.current_folder_size = 0
            self.current_items_count = 0

            # iterating over current files
            for file in files:

                # updating progress tracker attributes
                self.progress_tracker.current_iteration += 1
                self.progress_tracker.current_file += 1

                # updating totals
                self.total_files += 1

                # checking extension toggle
                if self.extension is not None:

                    # getting file matches extension bool
                    file_matches_extension = file.endswith(self.extension)

                    # checking if current file matches extension
                    if not file_matches_extension:

                        # skipping file
                        continue

                    # checking include counts toggle
                    if self.include_counts:

                        # updating valid files count
                        self.valid_files += 1

                # checking keyword toggle
                if self.keyword is not None:

                    # getting file matches keyword bool
                    file_matches_keyword = (self.keyword in file)

                    # checking if current file matches keyword
                    if not file_matches_keyword:

                        # skipping file
                        continue

                    # checking include counts toggle
                    if self.include_counts:

                        # updating valid files count
                        self.valid_files += 1

                # getting current file path
                file_path = join(folder_path,
                                 file)

                # getting current file dict
                file_dict = self.get_file_dict(file_name=file,
                                               file_path=file_path)

                # assembling path dict
                path_dict = {file_path: file_dict}

                # updating tree dict
                self.tree_dict.update(path_dict)

                # checking include sizes toggle
                if self.include_sizes:

                    # getting file size
                    file_size = file_dict['size']

                    # updating folder size
                    self.current_folder_size += file_size

                    # updating total size
                    self.total_size += file_size

                # checking include counts toggle
                if self.include_counts:

                    # updating items count
                    self.current_items_count += 1

            # iterating over current subfolders
            for subfolder in subfolders:

                # getting current subfolder path
                subfolder_path = join(folder_path,
                                      subfolder)

                # getting skip folder bool
                skip_folder = get_skip_bool(folder_path=subfolder_path,
                                            start_path=self.start_path,
                                            cache_folders=self.cache_folders)

                # checking whether to skip current folder
                if skip_folder:

                    # skipping current folder
                    continue

                # getting current subfolder dict
                subfolder_dict = self.tree_dict.get(subfolder_path)  # this will never be None due to topdown=False!
                                                                     # The subfolder will always have already been a
                                                                     # folder in a previous iteration!

                # checking include sizes toggle
                if self.include_sizes:

                    # getting file size
                    subfolder_size = subfolder_dict['size']

                    # updating folder size
                    self.current_folder_size += subfolder_size

                # checking include counts toggle
                if self.include_counts:

                    # updating items count
                    self.current_items_count += 1

            # getting current folder dict
            folder_dict = self.get_folder_dict(folder_name=folder_name,
                                               folder_path=folder_path)

            # assembling path dict
            path_dict = {folder_path: folder_dict}

            # updating tree dict
            self.tree_dict.update(path_dict)

        # reversing dict (required since topdown was set to False in os.walk to enable size obtaining optimization)
        tree_dict = reverse_dict(a_dict=self.tree_dict)

        # returning tree dict
        return tree_dict

    def get_file_tag(self,
                     path_dict: dict
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
        if self.include_sizes:

            # getting additional path dict info
            file_size = path_dict['size']

            # getting size string
            size_str = get_size_str(file_size)

            # updating file tag
            file_tag += f' ({size_str})'

        # returning file tag
        return file_tag

    def get_folder_tag(self,
                       path_dict: dict
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
        if self.include_counts:

            # getting additional path dict info
            items_count = path_dict['count']

            # updating folder tag
            folder_tag += f' [{items_count}]'

        # checking include sizes toggle
        if self.include_sizes:

            # getting additional path dict info
            folder_size = path_dict['size']

            # getting size string
            size_str = get_size_str(folder_size)

            # updating folder tag
            folder_tag += f' ({size_str})'

        # returning folder tag
        return folder_tag

    def get_path_tag(self,
                     path_dict: dict,
                     path_type: str
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
            path_tag = self.get_folder_tag(path_dict=path_dict)

        else:

            # getting file tag
            path_tag = self.get_file_tag(path_dict=path_dict)

        # returning path tag
        return path_tag

    def dict_to_tree(self,
                     tree_dict: dict,
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
            if self.apply_level_filter:

                # checking if current level is above max
                if path_level > self.level:

                    # skipping path
                    continue

            # checking dirs only bool
            if self.dirs_only:

                # checking if path is file
                if path_is_file:

                    # skipping current node
                    continue

            # getting current path id/parent
            path_id = path_dict['path']
            parent_id = path_dict['parent']

            # getting current path tag
            path_tag = self.get_path_tag(path_dict=path_dict,
                                         path_type=path_type)

            # getting path is root bool
            path_is_root = (path_id == self.start_path)

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

    def update_tree_dict(self) -> None:
        """
        Updates tree dict based on start path.
        """
        # getting updated tree dict
        tree_dict = self.get_tree_dict()

        # updating attributes
        self.tree_dict = tree_dict

    def update_tree(self) -> None:
        """
        Updates tree based on tree dict.
        """
        # getting updated tree
        tree = self.dict_to_tree(tree_dict=self.tree_dict)

        # updating attributes
        self.progress_tracker.tree = tree

    def update_end_string(self) -> None:
        """
        Updates end string with folder/files
        description summary (counts/sizes).
        """
        # defining placeholder value for new end string
        end_string = ''

        # checking include counts toggle
        if self.include_counts:

            # updating end string
            end_string += f'{self.total_folders} folders'
            end_string += f', {self.total_files} files'

            # checking extension toggle
            if self.extension is not None:

                # updating end string
                end_string += f' ({self.valid_files} valid)'

            # checking keyword toggle
            elif self.keyword is not None:

                # updating end string
                end_string += f' ({self.valid_files} valid)'

        # checking include sizes toggle
        if self.include_sizes:

            # getting total size string
            total_size_str = get_size_str(size_in_bytes=self.total_size)

            # updating end string
            end_string += f', {total_size_str}'

        # updating progress tracker attributes
        self.progress_tracker.end_string = end_string

    def run(self):
        """
        Runs main PyTree methods to
        scan folder/subfolder/files
        with specified parameters.
        """
        # updating tree dict
        self.update_tree_dict()

        # updating tree
        self.update_tree()

        # updating end string
        self.update_end_string()

######################################################################
# end of current module
