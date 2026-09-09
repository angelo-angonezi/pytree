# TreeScanner module

# Code destined to defining
# TreeScanner class and related
# attributes/methods.

######################################################################
# imports

# importing required libraries
from os import walk
from os.path import join
from os.path import abspath
from os.path import dirname
from os.path import getsize
from pytree.shared.loc import get_loc
from pytree.shared.data import reverse_dict
from pytree.shared.path import get_path_name
from pytree.shared.path import get_path_depth
from pytree.shared.filter import get_skip_file
from pytree.shared.filter import get_skip_folder
from pytree.progress_tracker.ModuleProgressTracker import ModuleProgressTracker

#####################################################################
# TreeScanner definition


class TreeScanner:
    """
    Defines TreeScanner class.
    """
    def __init__(self,
                 start_path: str,
                 extension: str | None,
                 keyword: str | None,
                 loc: bool,
                 include_sizes: bool,
                 include_counts: bool,
                 cache_folders: list,
                 start_is_cache: bool,
                 start_level: int,
                 progress_tracker: ModuleProgressTracker
                 ) -> None:
        """
        Initializes a TreeScanner instance
        and defines class attributes.
        """
        # creating attributes from input
        self.start_path = start_path
        self.extension = extension
        self.keyword = keyword
        self.loc = loc
        self.include_sizes = include_sizes
        self.include_counts = include_counts
        self.cache_folders = cache_folders
        self.start_is_cache = start_is_cache
        self.start_level = start_level
        self.progress_tracker = progress_tracker

        # defining base tree dict
        self.tree_dict = {}

        # totals (keeping separate from ProgressTracker since it counts per subfolder)
        self.total_folders = 0
        self.total_files = 0
        self.total_size = 0
        self.total_loc = 0
        self.total_com = 0

        # defining placeholder values for current folder size/count
        self.current_folder_size = 0
        self.current_items_count = 0
        self.current_folder_loc = 0
        self.current_folder_com = 0

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

        # checking mode
        if self.loc:

            # getting lines of code
            loc, com = get_loc(file_path=file_path)

            # updating base dict
            base_dict['loc'] = loc
            base_dict['com'] = com

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

        # checking mode
        if self.loc:

            # updating base dict
            base_dict['loc'] = self.current_folder_loc
            base_dict['com'] = self.current_folder_com

        # returning base dict
        return base_dict

    def scan_file(self,
                  file_name: str,
                  file_path: str
                  ) -> None:
        """
        Given a file name/path updates tree
        dict accordingly.
        """
        # getting current file dict (may raise OSError, e.g. PermissionError, if the file was
        # listed by os.walk's scandir but can't actually be opened/stat'd - permission denied,
        # a locked/access-controlled system file, or one that vanished mid-scan)
        try:

            # getting current file dict
            file_dict = self.get_file_dict(file_name=file_name,
                                           file_path=file_path)

        except OSError:

            # skipping current file's contribution to folder/tree totals
            return

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
            self.valid_files += 1

        # checking mode
        if self.loc:

            # getting file loc/com
            file_loc = file_dict['loc']
            file_com = file_dict['com']

            # updating folder loc
            self.current_folder_loc += file_loc
            self.current_folder_com += file_com

            # updating total loc
            self.total_loc += file_loc
            self.total_com += file_com

    def scan_subfolder(self,
                       subfolder_path: str
                       ) -> None:
        """
        Given a folder path and respective
        subfolder/files lists, updates tree
        dict accordingly.
        """
        # getting current subfolder dict
        subfolder_dict = self.tree_dict.get(subfolder_path)  # under topdown=False, the subfolder is normally
                                                             # already in tree_dict from a previous iteration,
                                                             # but os.walk silently drops directories it cannot
                                                             # enter (e.g. permission denied, or one that
                                                             # vanished mid-scan) without ever yielding them,
                                                             # while still listing their name in the parent's
                                                             # dirnames - so this can be None; skip contributing
                                                             # to parent totals in that case instead of crashing

        # checking if subfolder was never scanned (inaccessible/vanished mid-scan)
        if subfolder_dict is None:

            # skipping current subfolder's contribution to parent totals
            return

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

        # checking mode
        if self.loc:

            # getting file loc/com
            subfolder_loc = subfolder_dict['loc']
            subfolder_com = subfolder_dict['com']

            # updating folder loc/com
            self.current_folder_loc += subfolder_loc
            self.current_folder_com += subfolder_com

    def scan_folder(self,
                    folder_path: str,
                    subfolders: list,
                    files: list
                    ) -> None:
        """
        Given a folder path and respective
        subfolder/files lists, updates tree
        dict accordingly.
        """
        # sorting subfolders/files alphabetically
        subfolders = sorted(subfolders)
        files = sorted(files)

        # getting current folder name
        folder_name = get_path_name(path=folder_path)

        # getting current files num
        files_num = len(files)

        # updating progress tracker attributes
        self.progress_tracker.files_num = files_num

        # resetting progress tracker attributes
        self.progress_tracker.current_file = 0
        self.current_folder_size = 0
        self.current_items_count = 0

        # iterating over current files
        for file_name in files:

            # updating progress tracker attributes
            self.progress_tracker.current_iteration += 1
            self.progress_tracker.current_file += 1

            # updating totals
            self.total_files += 1

            # getting skip file bool
            skip_file = get_skip_file(file_name=file_name,
                                      extension=self.extension,
                                      keyword=self.keyword)

            # checking whether to skip current file
            if skip_file:

                # skipping current file
                continue

            # getting current file path
            file_path = join(folder_path,
                             file_name)

            # scanning current file
            self.scan_file(file_name=file_name,
                           file_path=file_path)

        # iterating over current subfolders
        for subfolder_name in subfolders:

            # getting current subfolder path
            subfolder_path = join(folder_path,
                                  subfolder_name)

            # getting skip folder bool
            skip_folder = get_skip_folder(folder_path=subfolder_path,
                                          start_path=self.start_path,
                                          start_is_cache=self.start_is_cache,
                                          cache_folders=self.cache_folders)

            # checking whether to skip current folder
            if skip_folder:

                # skipping current folder
                continue

            # scanning current subfolder
            self.scan_subfolder(subfolder_path=subfolder_path)

        # getting current folder dict
        folder_dict = self.get_folder_dict(folder_name=folder_name,
                                           folder_path=folder_path)

        # assembling path dict
        path_dict = {folder_path: folder_dict}

        # updating tree dict
        self.tree_dict.update(path_dict)

    def get_tree_dict(self) -> dict:
        """
        Scans start path for subfolders/files
        and returns dictionary of tree structure,
        containing sizes/counts/loc info, according
        to specified parameters.
        """
        # getting folders/subfolders/files in start path
        folders_subfolders_files = walk(self.start_path,
                                        topdown=False)

        # iterating over folders/subfolders/files
        for item in folders_subfolders_files:

            # getting current folder path/subfolders/files
            folder_path, subfolders, files = item

            # getting skip folder bool
            skip_folder = get_skip_folder(folder_path=folder_path,
                                          start_path=self.start_path,
                                          start_is_cache=self.start_is_cache,
                                          cache_folders=self.cache_folders)

            # checking whether to skip current folder
            if skip_folder:

                # skipping current folder
                continue

            # updating progress tracker attributes
            self.progress_tracker.current_folder += 1

            # updating totals
            self.total_folders += 1

            # scanning current folder
            self.scan_folder(folder_path=folder_path,
                             subfolders=subfolders,
                             files=files)

        # reversing dict (required since topdown was set to False in os.walk to enable size obtaining optimization)
        tree_dict = reverse_dict(a_dict=self.tree_dict)

        # returning tree dict
        return tree_dict

######################################################################
# end of current module
