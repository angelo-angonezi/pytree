# test_module_progress_tracker module

# Code destined to testing ModuleProgressTracker's update_totals/
# get_progress_string/normal_exit methods. Only these methods are
# ever exercised directly here - run() is never called, since it
# drives a real background thread.

######################################################################
# imports

# importing required libraries
from pytree.progress_tracker.ModuleProgressTracker import ModuleProgressTracker

######################################################################
# defining update_totals test cases


def test_update_totals_matches_small_tree_counts(small_tree, capsys) -> None:
    """
    Asserts update_totals walks the given start path and populates
    folders_num/files_num/iterations_num matching small_tree's known,
    cache-exclusive totals.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # creating a fresh module progress tracker
    module_progress_tracker = ModuleProgressTracker()

    # updating totals against the small tree fixture
    module_progress_tracker.update_totals(args_dict={'start_path': root,
                                                      'quiet': False})

    # asserting folder/file counters match the fixture's expected totals
    assert module_progress_tracker.folders_num == expected['total_folders']
    assert module_progress_tracker.files_num == expected['total_files']
    assert module_progress_tracker.iterations_num == expected['total_files']

    # asserting show_tree was derived from the (falsy) quiet flag
    assert module_progress_tracker.show_tree is True

    # asserting totals_updated event was signaled
    assert module_progress_tracker.totals_updated.is_set() is True


def test_update_totals_show_tree_false_when_quiet(small_tree) -> None:
    """
    Asserts update_totals derives show_tree as False when the
    quiet flag is set.
    """
    # unpacking small tree root path (expected totals unused here)
    root, _ = small_tree

    # creating a fresh module progress tracker
    module_progress_tracker = ModuleProgressTracker()

    # updating totals with quiet=True
    module_progress_tracker.update_totals(args_dict={'start_path': root,
                                                      'quiet': True})

    # asserting show_tree was derived as False
    assert module_progress_tracker.show_tree is False

######################################################################
# defining get_progress_string test cases


def test_get_progress_string_before_totals_updated_shows_scanning() -> None:
    """
    Asserts get_progress_string returns the "scanning paths..."
    branch while totals_updated has not been set.
    """
    # creating a fresh module progress tracker
    module_progress_tracker = ModuleProgressTracker()

    # setting known counters
    module_progress_tracker.folders_num = 3
    module_progress_tracker.files_num = 2
    module_progress_tracker.iterations_num = 2

    # getting progress string before totals are updated
    progress_string = module_progress_tracker.get_progress_string()

    # asserting the scanning-paths branch was used, with counters included
    assert progress_string.startswith('scanning paths...')
    assert 'folders: 3' in progress_string
    assert 'files: 2' in progress_string


def test_get_progress_string_after_totals_updated_shows_creating_tree() -> None:
    """
    Asserts get_progress_string returns the "creating tree..."
    branch once totals_updated has been set.
    """
    # creating a fresh module progress tracker
    module_progress_tracker = ModuleProgressTracker()

    # signaling totals updated directly
    module_progress_tracker.totals_updated.set()

    # setting known counters
    module_progress_tracker.folders_num = 3
    module_progress_tracker.current_folder = 1
    module_progress_tracker.files_num = 2
    module_progress_tracker.current_file = 1

    # getting progress string after totals are updated
    progress_string = module_progress_tracker.get_progress_string()

    # asserting the creating-tree branch was used, with counters included
    assert progress_string.startswith('creating tree...')
    assert 'folder: 1/3' in progress_string
    assert 'file: 1/2' in progress_string

######################################################################
# defining normal_exit test cases


def test_normal_exit_without_tree_prints_end_string(capsys) -> None:
    """
    Asserts normal_exit prints only the spacer and end string when
    show_tree is False (never touching self.tree).
    """
    # creating a fresh module progress tracker
    module_progress_tracker = ModuleProgressTracker()

    # setting show_tree to False and a known end string
    module_progress_tracker.show_tree = False
    module_progress_tracker.end_string = 'analysis complete!'
    module_progress_tracker.print_end_string = ''

    # calling normal exit
    module_progress_tracker.normal_exit()

    # capturing console output
    captured = capsys.readouterr()

    # asserting spacer and end string were printed, with no tree output
    assert captured.out == '\n\nanalysis complete!'

######################################################################
# end of current module
