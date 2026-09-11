# test_pytree module

# Code destined to testing PyTree's constructor and orchestration
# methods (update_tree_dict/update_tree/save_tree/update_end_string/
# update_print_end_string/run), always injecting a FakeProgressTracker
# via the progress_tracker= constructor parameter, so no real,
# thread-driving ModuleProgressTracker is ever constructed.

######################################################################
# imports

# importing required libraries
from treelib import Tree
from pathlib import Path
from pandas import read_csv
from pytest import MonkeyPatch
from pytree.core.PyTree import PyTree
from pytree.shared.size import get_size_str
from pytree.shared.loc import get_loc_com_str
from pytree.shared.global_vars import CACHE_FOLDERS

######################################################################
# helper for building a PyTree with common defaults


def build_pytree(root: str,
                 fake_progress_tracker,
                 dirs_only: bool = False,
                 include_counts: bool = True,
                 include_sizes: bool = True,
                 extension: str | None = None,
                 keyword: str | None = None,
                 level: int = -1,
                 loc: bool = False,
                 output_path: str | None = None,
                 quiet: bool = False
                 ) -> PyTree:
    """
    Returns a PyTree instance configured against the given
    small_tree root path, using the given fake progress tracker.
    """
    # building and returning PyTree instance
    return PyTree(start_path=root,
                  dirs_only=dirs_only,
                  include_counts=include_counts,
                  include_sizes=include_sizes,
                  extension=extension,
                  keyword=keyword,
                  level=level,
                  loc=loc,
                  output_path=output_path,
                  quiet=quiet,
                  progress_tracker=fake_progress_tracker)

######################################################################
# defining constructor test cases


def test_constructor_defaults_cache_folders_and_progress_tracker(small_tree, fake_progress_tracker) -> None:
    """
    Asserts the constructor defaults cache_folders to the global
    CACHE_FOLDERS list, and stores the injected progress tracker
    (rather than constructing a real one).
    """
    # unpacking small tree root path
    root, _ = small_tree

    # building PyTree with defaults
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker)

    # asserting cache folders default and progress tracker wiring
    assert pytree.cache_folders == CACHE_FOLDERS
    assert pytree.progress_tracker is fake_progress_tracker


def test_constructor_loc_mode_forces_python_extension(small_tree, fake_progress_tracker) -> None:
    """
    Asserts the constructor forces extension to '.py' whenever
    loc=True, regardless of the extension passed in.
    """
    # unpacking small tree root path
    root, _ = small_tree

    # building PyTree with loc enabled and a different extension given
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker,
                          extension='.txt',
                          loc=True)

    # asserting extension was overridden to '.py'
    assert pytree.extension == '.py'

######################################################################
# defining update_tree_dict test cases


def test_update_tree_dict_matches_small_tree_totals(small_tree, fake_progress_tracker) -> None:
    """
    Asserts update_tree_dict populates self.tree_dict and drives the
    underlying scanner to small_tree's known, cache-exclusive totals.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with counts and sizes enabled
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker)

    # updating tree dict
    pytree.update_tree_dict()

    # asserting tree dict is non-empty and scanner totals match expectations
    assert pytree.tree_dict != {}
    assert pytree.scanner.total_folders == expected['total_folders']
    assert pytree.scanner.total_files == expected['total_files']
    assert pytree.scanner.total_size == expected['total_size']

######################################################################
# defining update_tree test cases


def test_update_tree_writes_tree_onto_progress_tracker(small_tree, fake_progress_tracker) -> None:
    """
    Asserts update_tree converts self.tree_dict into a treelib.Tree
    and stores it on the injected progress tracker, with one node per
    non-cache folder/file in small_tree.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with counts and sizes enabled
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker)

    # updating tree dict then tree
    pytree.update_tree_dict()
    pytree.update_tree()

    # asserting a tree was stored on the progress tracker
    assert isinstance(fake_progress_tracker.tree, Tree)

    # asserting node count matches folders + files (cache excluded)
    expected_node_count = (expected['total_folders'] + expected['total_files'])
    assert fake_progress_tracker.tree.size() == expected_node_count

######################################################################
# defining save_tree test cases


def test_save_tree_writes_csv_to_output_path(small_tree, fake_progress_tracker, tmp_path: Path) -> None:
    """
    Asserts save_tree writes a CSV file to output_path containing one
    row per non-cache folder/file in small_tree.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # defining output csv path
    output_path = str(tmp_path / 'tree_output.csv')

    # building PyTree with an output path set
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker,
                          output_path=output_path)

    # updating tree dict then saving tree
    pytree.update_tree_dict()
    pytree.save_tree()

    # reading back the saved csv
    saved_df = read_csv(output_path)

    # asserting one row per folder + file (cache excluded)
    expected_row_count = (expected['total_folders'] + expected['total_files'])
    assert len(saved_df) == expected_row_count

######################################################################
# defining update_end_string test cases


def test_update_end_string_without_loc(small_tree, fake_progress_tracker) -> None:
    """
    Asserts update_end_string, without loc mode, assembles a
    "folders, files, size" summary matching small_tree's known
    totals, with no "(valid)" parenthetical since no extension/
    keyword filter was given.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with counts and sizes enabled, no filters, no loc
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker)

    # running the scan then updating end string
    pytree.update_tree_dict()
    pytree.update_end_string()

    # computing expected size string
    expected_size_str = get_size_str(size_in_bytes=expected['total_size'])

    # assembling expected end string
    expected_end_string = f"{expected['total_folders']} folders, "
    expected_end_string += f"{expected['total_files']} files, {expected_size_str}"

    # asserting end string matches expectations
    assert fake_progress_tracker.end_string == expected_end_string


def test_update_end_string_with_loc_reports_valid_files_and_loc(small_tree, fake_progress_tracker) -> None:
    """
    Asserts update_end_string, with loc mode (which forces the '.py'
    extension), reports the "(N valid)" parenthetical and a loc/
    comment summary based only on the .py file's own contribution.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with counts/sizes/loc all enabled
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker,
                          loc=True)

    # running the scan then updating end string
    pytree.update_tree_dict()
    pytree.update_end_string()

    # computing expected size string (only file_a contributes, since file_b.txt
    # is skipped once loc mode forces the '.py' extension filter)
    expected_size_str = get_size_str(size_in_bytes=expected['file_a_size'])

    # computing expected loc/comment string
    expected_loc_com_str = get_loc_com_str(loc=expected['file_a_loc'],
                                           com=expected['file_a_com'])

    # assembling expected end string
    expected_end_string = f"{expected['total_folders']} folders, "
    expected_end_string += f"{expected['total_files']} files ({expected['valid_py_files']} valid), "
    expected_end_string += f"{expected_size_str}, {expected_loc_com_str}"

    # asserting end string matches expectations
    assert fake_progress_tracker.end_string == expected_end_string

######################################################################
# defining update_print_end_string test cases


def test_update_print_end_string_on_linux_adds_newline(small_tree,
                                                        fake_progress_tracker,
                                                        monkeypatch: MonkeyPatch
                                                        ) -> None:
    """
    Asserts update_print_end_string sets a leading newline when
    sys.platform is 'linux'.
    """
    # unpacking small tree root path
    root, _ = small_tree

    # building PyTree with defaults
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker)

    # forcing platform to linux
    monkeypatch.setattr('pytree.core.PyTree.platform', 'linux')

    # updating print end string
    pytree.update_print_end_string()

    # asserting a leading newline was set
    assert fake_progress_tracker.print_end_string == '\n'


def test_update_print_end_string_on_non_linux_is_empty(small_tree,
                                                        fake_progress_tracker,
                                                        monkeypatch: MonkeyPatch
                                                        ) -> None:
    """
    Asserts update_print_end_string leaves the print end string empty
    when sys.platform is not 'linux'.
    """
    # unpacking small tree root path
    root, _ = small_tree

    # building PyTree with defaults
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker)

    # forcing platform to win32
    monkeypatch.setattr('pytree.core.PyTree.platform', 'win32')

    # updating print end string
    pytree.update_print_end_string()

    # asserting print end string stayed empty
    assert fake_progress_tracker.print_end_string == ''

######################################################################
# defining run test cases


def test_run_end_to_end_populates_progress_tracker(small_tree, fake_progress_tracker) -> None:
    """
    Asserts run() drives the full scan/tree/end-string flow against
    small_tree, using only the injected fake progress tracker (never
    a real ModuleProgressTracker).
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with counts and sizes enabled, no output path (not saving)
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker)

    # running full pipeline
    pytree.run()

    # asserting tree dict was populated
    assert pytree.tree_dict != {}

    # asserting a tree was stored on the progress tracker
    assert isinstance(fake_progress_tracker.tree, Tree)

    # asserting end string reports the expected folder/file counts
    assert f"{expected['total_folders']} folders" in fake_progress_tracker.end_string
    assert f"{expected['total_files']} files" in fake_progress_tracker.end_string

    # asserting print end string was set (empty or newline, depending on platform)
    assert fake_progress_tracker.print_end_string in ('', '\n')

######################################################################
# end of current module
