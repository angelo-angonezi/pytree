# test_end_to_end_tmp module

# Code destined to testing PyTree.run() end-to-end against the fast,
# in-memory small_tree fixture, across several flag combinations
# (dirs_only/extension/keyword/include_sizes+include_counts/loc), always
# injecting a FakeProgressTracker so no real, thread-driving
# ModuleProgressTracker is ever constructed. These tests are always run
# (not marked slow); the real test_folder/ golden-master checks live in
# test_golden_master_fixture.py instead.

######################################################################
# imports

# importing required libraries
from pytree.core.PyTree import PyTree
from pytree.shared.size import get_size_str
from pytree.shared.loc import get_loc_com_str

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
# defining dirs_only test cases


def test_run_dirs_only_excludes_files_from_tree(small_tree, fake_progress_tracker) -> None:
    """
    Asserts run(), with dirs_only=True, builds a tree containing only
    folder nodes (root/sub1/sub2), with both small_tree files excluded.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with dirs_only enabled
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker,
                          dirs_only=True)

    # running full pipeline
    pytree.run()

    # getting resulting tree
    tree = fake_progress_tracker.tree

    # asserting only the 3 non-cache folders were added as nodes
    assert tree.size() == expected['total_folders']

    # asserting neither file was added as a node
    assert tree.get_node(expected['file_a']) is None
    assert tree.get_node(expected['file_b']) is None

    # asserting both non-cache folders were added as nodes
    assert tree.get_node(expected['sub1']) is not None
    assert tree.get_node(expected['sub2']) is not None

######################################################################
# defining extension filter test cases


def test_run_extension_filter_limits_valid_files_and_tree_contents(small_tree, fake_progress_tracker) -> None:
    """
    Asserts run(), with extension='.py', walks both files (total_files
    unaffected) but only counts/adds file_a (the .py file) as valid,
    excluding file_b.txt from the resulting tree.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with a .py extension filter
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker,
                          extension='.py')

    # running full pipeline
    pytree.run()

    # asserting total_files still counts every walked file, regardless of the filter
    assert pytree.scanner.total_files == expected['total_files']

    # asserting only file_a was counted as valid
    assert pytree.scanner.valid_files == expected['valid_py_files']

    # asserting file_a was added to the tree, but file_b.txt was excluded
    tree = fake_progress_tracker.tree
    assert tree.get_node(expected['file_a']) is not None
    assert tree.get_node(expected['file_b']) is None

    # asserting the "(N valid)" parenthetical appears in the end string
    assert f"({expected['valid_py_files']} valid)" in fake_progress_tracker.end_string

######################################################################
# defining keyword filter test cases


def test_run_keyword_filter_limits_valid_files_and_tree_contents(small_tree, fake_progress_tracker) -> None:
    """
    Asserts run(), with keyword='file_b', includes only file_b.txt
    (matching the keyword) and excludes file_a.py from the tree.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with a "file_b" keyword filter
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker,
                          keyword='file_b')

    # running full pipeline
    pytree.run()

    # asserting only file_b was counted as valid
    assert pytree.scanner.valid_files == 1

    # asserting file_b was added to the tree, but file_a.py was excluded
    tree = fake_progress_tracker.tree
    assert tree.get_node(expected['file_b']) is not None
    assert tree.get_node(expected['file_a']) is None

######################################################################
# defining include_sizes/include_counts tag test cases


def test_run_with_sizes_and_counts_produces_expected_folder_tags(small_tree, fake_progress_tracker) -> None:
    """
    Asserts run(), with both include_counts and include_sizes enabled,
    produces folder tags carrying the expected "[count] (size)"
    parentheticals for each of small_tree's non-cache folders.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with counts and sizes enabled (the defaults)
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker)

    # running full pipeline
    pytree.run()

    # getting resulting tree
    tree = fake_progress_tracker.tree

    # computing expected total size string (root holds every non-cache file)
    total_size_str = get_size_str(size_in_bytes=expected['total_size'])

    # asserting root's tag shows 2 items (sub1/sub2) and the full tree size
    root_tag = tree.get_node(expected['root']).tag
    assert root_tag == f'root [2] ({total_size_str})'

    # computing expected sub1 size string (holds file_a and file_b)
    sub1_size_str = get_size_str(size_in_bytes=(expected['file_a_size'] + expected['file_b_size']))

    # asserting sub1's tag shows 2 items (file_a/file_b) and their combined size
    sub1_tag = tree.get_node(expected['sub1']).tag
    assert sub1_tag == f'sub1 [2] ({sub1_size_str})'

    # asserting sub2's tag shows 0 items (its only child, __pycache__, is excluded)
    sub2_tag = tree.get_node(expected['sub2']).tag
    assert sub2_tag == f'sub2 [0] (0 bytes)'

######################################################################
# defining loc mode test cases


def test_run_loc_mode_reports_loc_com_on_file_and_aggregated_in_end_string(small_tree, fake_progress_tracker) -> None:
    """
    Asserts run(), with loc=True (which forces the '.py' extension),
    reports file_a's own loc/comment counts on its file tag (folder
    tags never carry loc info, per get_folder_tag), rolls its count up
    onto sub1/root's folder counts (since file_a is the only .py file
    in small_tree), and reports the same aggregated loc/comment totals
    in the final end string.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building PyTree with loc mode enabled, without sizes (isolating the loc/count checks)
    pytree = build_pytree(root=root,
                          fake_progress_tracker=fake_progress_tracker,
                          include_sizes=False,
                          loc=True)

    # running full pipeline
    pytree.run()

    # getting resulting tree
    tree = fake_progress_tracker.tree

    # computing expected loc/comment string (file_a's own contribution)
    expected_loc_com_str = get_loc_com_str(loc=expected['file_a_loc'],
                                           com=expected['file_a_com'])

    # asserting file_a's tag carries its own loc/comment counts
    file_a_tag = tree.get_node(expected['file_a']).tag
    assert file_a_tag == f'file_a.py {{{expected_loc_com_str}}}'

    # asserting sub1's tag counts only file_a (file_b.txt was excluded by the '.py' filter),
    # with no loc info of its own (folder tags never carry loc/comment parentheticals)
    sub1_tag = tree.get_node(expected['sub1']).tag
    assert sub1_tag == 'sub1 [1]'

    # asserting root's tag counts both sub1 and sub2 (folders always count as items,
    # regardless of the file-level extension filter), again with no loc info
    root_tag = tree.get_node(expected['root']).tag
    assert root_tag == 'root [2]'

    # asserting the end string reports the aggregated loc/comment summary
    assert expected_loc_com_str in fake_progress_tracker.end_string

######################################################################
# end of current module
