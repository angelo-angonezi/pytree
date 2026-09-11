# test_golden_master_fixture module

# Code destined to testing PyTree.run() against the real, committed
# test_folder/ fixture referenced by README.md's CLI examples, asserting
# the exact folder/file counts, total size, and loc/comment summary the
# README documents. This doubles as a check that the fixture hasn't
# drifted from what the README claims - only the README's later,
# up-to-date examples (the "Saving tree" and "Lines of code" sections,
# both already accounting for folder/folder_inside_folder/
# another_python_file.py) are asserted here; its earlier "Basic usage"/
# "Using optional arguments"/"Specifying extension/keyword" examples
# still show a stale (pre-another_python_file.py) file count and are
# intentionally left unasserted. Marked slow since it touches real,
# on-disk fixture data rather than an in-memory tmp_path tree.

######################################################################
# imports

# importing required libraries
from pytest import mark
from pathlib import Path
from pytree.core.PyTree import PyTree

######################################################################
# helper for locating the real test_folder/ fixture

# getting real test_folder fixture path (tests/integration/ -> tests/ -> repo root -> test_folder)
TEST_FOLDER_PATH = str(Path(__file__).parent.parent.parent / 'test_folder')

######################################################################
# helper for building a PyTree with common defaults


def build_pytree(fake_progress_tracker,
                 dirs_only: bool = False,
                 include_counts: bool = True,
                 include_sizes: bool = False,
                 extension: str | None = None,
                 keyword: str | None = None,
                 level: int = -1,
                 loc: bool = False,
                 output_path: str | None = None,
                 quiet: bool = False
                 ) -> PyTree:
    """
    Returns a PyTree instance configured against the real
    test_folder/ fixture, using the given fake progress tracker.
    """
    # building and returning PyTree instance
    return PyTree(start_path=TEST_FOLDER_PATH,
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
# defining golden master test cases


@mark.slow
def test_golden_master_counts_and_total_size(fake_progress_tracker) -> None:
    """
    Asserts run(), with counts and sizes enabled, reports the exact
    "5 folders, 7 files, 13 mb" summary the README's "Saving tree"
    section documents for the real test_folder/ fixture.
    """
    # building PyTree with counts and sizes enabled, no filters, no loc
    pytree = build_pytree(fake_progress_tracker=fake_progress_tracker,
                          include_counts=True,
                          include_sizes=True)

    # running full pipeline
    pytree.run()

    # asserting the end string matches the README's documented summary exactly
    assert fake_progress_tracker.end_string == '5 folders, 7 files, 13 mb'


@mark.slow
def test_golden_master_loc_summary_and_file_tags(fake_progress_tracker) -> None:
    """
    Asserts run(), with loc=True (which forces the '.py' extension),
    reports the exact "5 folders, 7 files (2 valid), 6 lines of code
    (38%), 10 comments (62%)" summary the README's "Lines of code"
    section documents, plus each individual .py file's own
    documented loc/comment tag, for the real test_folder/ fixture.
    """
    # building PyTree with counts and loc enabled
    pytree = build_pytree(fake_progress_tracker=fake_progress_tracker,
                          include_counts=True,
                          loc=True)

    # running full pipeline
    pytree.run()

    # asserting the end string matches the README's documented summary exactly
    expected_end_string = '5 folders, 7 files (2 valid), '
    expected_end_string += '6 lines of code (38%), 10 comments (62%)'
    assert fake_progress_tracker.end_string == expected_end_string

    # getting resulting tree
    tree = fake_progress_tracker.tree

    # getting real paths of both .py files in the fixture
    a_python_file_path = str(Path(TEST_FOLDER_PATH) / 'folder' / 'a_python_file.py')
    another_python_file_path = str(Path(TEST_FOLDER_PATH) / 'folder' / 'folder_inside_folder' / 'another_python_file.py')

    # asserting a_python_file.py's tag matches the README's documented loc/comment counts
    a_python_file_tag = tree.get_node(a_python_file_path).tag
    assert a_python_file_tag == 'a_python_file.py {2 lines of code (33%), 4 comments (67%)}'

    # asserting another_python_file.py's tag matches the README's documented loc/comment counts
    another_python_file_tag = tree.get_node(another_python_file_path).tag
    assert another_python_file_tag == 'another_python_file.py {4 lines of code (40%), 6 comments (60%)}'

######################################################################
# end of current module
