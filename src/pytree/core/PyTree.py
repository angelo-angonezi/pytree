# PyTree module

# Code destined to defining
# PyTree class and related
# attributes/methods.

######################################################################
# imports

# importing required libraries
from sys import platform
from pytree.shared.data import save_df
from pytree.shared.filter import is_cache
from pytree.shared.size import get_size_str
from pytree.core.converter import dict_to_df
from pytree.shared.loc import get_loc_com_str
from pytree.shared.path import get_path_depth
from pytree.core.converter import dict_to_tree
from pytree.core.TreeScanner import TreeScanner
from pytree.shared.global_vars import CACHE_FOLDERS
from pytree.progress_tracker.ModuleProgressTracker import ModuleProgressTracker

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
                 extension: str | None,
                 keyword: str | None,
                 level: int,
                 loc: bool,
                 output_path: str | None,
                 quiet: bool,
                 cache_folders: list = CACHE_FOLDERS,
                 progress_tracker: ModuleProgressTracker = type[ModuleProgressTracker]
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
        self.loc = loc
        self.output_path = output_path
        self.quiet = quiet
        self.cache_folders = cache_folders
        self.progress_tracker = progress_tracker

        # checking whether mode is loc
        if self.loc:

            # updating valid extensions
            self.extension = '.py'

        # getting show tree bool
        self.show_tree = (not self.quiet)

        # getting save output bool
        self.save_output = (self.output_path is not None)

        # getting start is cache bool
        self.start_is_cache = is_cache(path=self.start_path,
                                       cache_folders=self.cache_folders)

        # getting start level
        self.start_level = get_path_depth(path=self.start_path)

        # getting apply level filter bool
        self.apply_level_filter = (self.level != -1)

        # defining base tree dict
        self.tree_dict = {}

        # creating scanner instance (walks filesystem and builds tree dict)
        self.scanner = TreeScanner(start_path=self.start_path,
                                   extension=self.extension,
                                   keyword=self.keyword,
                                   loc=self.loc,
                                   include_sizes=self.include_sizes,
                                   include_counts=self.include_counts,
                                   cache_folders=self.cache_folders,
                                   start_is_cache=self.start_is_cache,
                                   start_level=self.start_level,
                                   progress_tracker=self.progress_tracker)

    def update_tree_dict(self) -> None:
        """
        Updates tree dict based on start path.
        """
        # getting updated tree dict
        tree_dict = self.scanner.get_tree_dict()

        # updating attributes
        self.tree_dict = tree_dict

    def update_tree(self) -> None:
        """
        Updates tree based on tree dict.
        """
        # getting updated tree
        tree = dict_to_tree(tree_dict=self.tree_dict,
                            start_path=self.start_path,
                            dirs_only=self.dirs_only,
                            include_counts=self.include_counts,
                            include_sizes=self.include_sizes,
                            level=self.level,
                            loc=self.loc,
                            apply_level_filter=self.apply_level_filter)

        # updating progress tracker attributes
        self.progress_tracker.tree = tree

    def save_tree(self) -> None:
        """
        Saves tree as a table in
        given output folder.
        """
        # getting tree df
        tree_df = dict_to_df(tree_dict=self.tree_dict,
                             dirs_only=self.dirs_only,
                             include_counts=self.include_counts,
                             include_sizes=self.include_sizes,
                             level=self.level,
                             loc=self.loc,
                             apply_level_filter=self.apply_level_filter)

        # saving df
        save_df(save_path=self.output_path,
                df=tree_df)

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
            end_string += f'{self.scanner.total_folders} folders'
            end_string += f', {self.scanner.total_files} files'

            # checking extension toggle
            if self.extension is not None:

                # updating end string
                end_string += f' ({self.scanner.valid_files} valid)'

            # checking keyword toggle
            elif self.keyword is not None:

                # updating end string
                end_string += f' ({self.scanner.valid_files} valid)'

        # checking include sizes toggle
        if self.include_sizes:

            # getting total size string
            total_size_str = get_size_str(size_in_bytes=self.scanner.total_size)

            # updating end string
            end_string += f', {total_size_str}'

        # checking mode
        if self.loc:

            # getting total loc string
            total_loc_str = get_loc_com_str(loc=self.scanner.total_loc,
                                            com=self.scanner.total_com)

            # updating end string
            end_string += f', {total_loc_str}'

        # checking save output toggle
        if self.save_output:

            # updating end string
            end_string += f'\n'
            end_string += f'Saved output table to "{self.output_path}"'

        # updating progress tracker attributes
        self.progress_tracker.end_string = end_string

    def update_print_end_string(self) -> None:
        """
        Updates end string with folder/files
        description summary (counts/sizes).
        """
        # defining placeholder value for new print end string
        print_end_string = ''

        # getting os is linux bool
        os_is_linux = (platform == 'linux')

        # checking if os is linux
        if os_is_linux:

            # updating print end string
            print_end_string = '\n'

        # updating progress tracker attributes
        self.progress_tracker.print_end_string = print_end_string

    def run(self):
        """
        Runs main PyTree methods to
        scan folder/subfolder/files
        with specified parameters.
        """
        # updating tree dict
        self.update_tree_dict()

        # checking whether to show tree
        if self.show_tree:

            # updating tree
            self.update_tree()

        # checking whether to save tree
        if self.save_output:

            # saving tree
            self.save_tree()

        # updating end string
        self.update_end_string()

        # updating print end string
        self.update_print_end_string()

######################################################################
# end of current module
