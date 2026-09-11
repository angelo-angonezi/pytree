# test_filter module

# Code destined to testing shared/filter.py's
# cache-folder detection and extension/keyword
# filtering functions.

######################################################################
# imports

# importing required libraries
from pytest import mark
from pathlib import Path
from pytree.shared.filter import is_cache
from pytree.shared.filter import get_skip_file
from pytree.shared.filter import get_skip_folder
from pytree.shared.filter import is_reparse_point
from pytree.shared.global_vars import CACHE_FOLDERS

######################################################################
# defining is_cache test cases


def test_is_cache_substring_false_positive() -> None:
    """
    Documents that is_cache matches on a plain substring
    check, so a folder merely containing a cache keyword
    as part of a longer, unrelated name is still flagged.
    """
    # getting cache bool for a path that only coincidentally
    # contains the ".cache" substring inside a longer name
    cache_bool = is_cache(path='/home/user/my.cache_backup',
                          cache_folders=CACHE_FOLDERS)

    # asserting the substring match still triggers True (false positive)
    assert cache_bool is True


@mark.parametrize('cache_folder_name', CACHE_FOLDERS)
def test_is_cache_matches_each_cache_folder(cache_folder_name: str) -> None:
    """
    Asserts is_cache returns True for a path containing
    each entry of CACHE_FOLDERS.
    """
    # building a path containing the current cache folder name
    path = f'/home/user/project/{cache_folder_name}'

    # getting cache bool
    cache_bool = is_cache(path=path,
                          cache_folders=CACHE_FOLDERS)

    # asserting path was flagged as cache
    assert cache_bool is True


def test_is_cache_no_match() -> None:
    """
    Asserts is_cache returns False for a path containing
    none of the cache keywords.
    """
    # getting cache bool for an unrelated path
    cache_bool = is_cache(path='/home/user/project/src',
                          cache_folders=CACHE_FOLDERS)

    # asserting path was not flagged as cache
    assert cache_bool is False

######################################################################
# defining is_reparse_point test cases


def test_is_reparse_point_normal_dir(tmp_path: Path) -> None:
    """
    Asserts is_reparse_point returns False for a normal,
    non-junction directory.
    """
    # building a normal directory
    normal_dir = tmp_path / 'normal_dir'
    normal_dir.mkdir()

    # getting reparse point bool
    reparse_point_bool = is_reparse_point(path=str(normal_dir))

    # asserting normal directory is not flagged as a reparse point
    assert reparse_point_bool is False


def test_is_reparse_point_junction_flagged(tmp_path: Path,
                                           monkeypatch
                                           ) -> None:
    """
    Asserts is_reparse_point returns True when the path's
    stat result carries the FILE_ATTRIBUTE_REPARSE_POINT flag,
    mocking os.stat rather than creating a real junction.
    """
    # building a placeholder directory (content irrelevant, stat is mocked)
    junction_dir = tmp_path / 'junction_dir'
    junction_dir.mkdir()

    # defining a fake stat result carrying the reparse point attribute
    class FakeStatResult:
        """
        Minimal stand-in for os.stat_result, exposing only
        the attribute is_reparse_point actually reads.
        """
        st_file_attributes = 0x400  # FILE_ATTRIBUTE_REPARSE_POINT

    # defining a fake stat function returning the fake result
    def fake_stat(path, follow_symlinks=True) -> FakeStatResult:
        """
        Returns the fake stat result regardless of input.
        """
        return FakeStatResult()

    # patching stat as imported into pytree.shared.filter
    monkeypatch.setattr('pytree.shared.filter.stat', fake_stat)

    # getting reparse point bool
    reparse_point_bool = is_reparse_point(path=str(junction_dir))

    # asserting junction-flagged path is detected as a reparse point
    assert reparse_point_bool is True

######################################################################
# defining get_skip_folder test cases


def test_get_skip_folder_root_never_skipped(tmp_path: Path) -> None:
    """
    Asserts get_skip_folder never skips the root path,
    regardless of the other skip conditions.
    """
    # getting skip bool for the root path itself
    skip_bool = get_skip_folder(folder_path=str(tmp_path),
                                start_path=str(tmp_path),
                                start_is_cache=False,
                                cache_folders=CACHE_FOLDERS)

    # asserting root is never skipped
    assert skip_bool is False


def test_get_skip_folder_cache_bypassed_when_start_is_cache(tmp_path: Path) -> None:
    """
    Asserts get_skip_folder does not skip a cache-named
    folder when start_is_cache=True (the scan explicitly
    started inside a cache folder).
    """
    # building a cache-named subfolder
    cache_subfolder = tmp_path / '__pycache__'
    cache_subfolder.mkdir()

    # getting skip bool with start_is_cache=True
    skip_bool = get_skip_folder(folder_path=str(cache_subfolder),
                                start_path=str(tmp_path),
                                start_is_cache=True,
                                cache_folders=CACHE_FOLDERS)

    # asserting cache check was bypassed
    assert skip_bool is False


def test_get_skip_folder_cache_match_skipped(tmp_path: Path) -> None:
    """
    Asserts get_skip_folder skips a cache-named folder
    when start_is_cache=False.
    """
    # building a cache-named subfolder
    cache_subfolder = tmp_path / '__pycache__'
    cache_subfolder.mkdir()

    # getting skip bool with start_is_cache=False
    skip_bool = get_skip_folder(folder_path=str(cache_subfolder),
                                start_path=str(tmp_path),
                                start_is_cache=False,
                                cache_folders=CACHE_FOLDERS)

    # asserting cache folder was skipped
    assert skip_bool is True


def test_get_skip_folder_normal_subfolder_not_skipped(tmp_path: Path) -> None:
    """
    Asserts get_skip_folder does not skip a normal,
    non-cache, accessible, non-symlink subfolder.
    """
    # building a normal subfolder
    normal_subfolder = tmp_path / 'src'
    normal_subfolder.mkdir()

    # getting skip bool
    skip_bool = get_skip_folder(folder_path=str(normal_subfolder),
                                start_path=str(tmp_path),
                                start_is_cache=False,
                                cache_folders=CACHE_FOLDERS)

    # asserting normal subfolder is not skipped
    assert skip_bool is False


def test_get_skip_folder_oserror_forces_skip(tmp_path: Path,
                                             monkeypatch
                                             ) -> None:
    """
    Asserts get_skip_folder forces a skip when any
    OSError is raised during its accessibility probes.
    """
    # building a normal subfolder
    normal_subfolder = tmp_path / 'src'
    normal_subfolder.mkdir()

    # defining a fake islink that raises OSError
    def fake_islink(path) -> bool:
        """
        Always raises OSError, simulating an unprobeable path.
        """
        raise OSError('mocked probe error')

    # patching islink as imported into pytree.shared.filter
    monkeypatch.setattr('pytree.shared.filter.islink', fake_islink)

    # getting skip bool
    skip_bool = get_skip_folder(folder_path=str(normal_subfolder),
                                start_path=str(tmp_path),
                                start_is_cache=False,
                                cache_folders=CACHE_FOLDERS)

    # asserting the unprobeable folder was forced to skip
    assert skip_bool is True

######################################################################
# defining get_skip_file test cases


def test_get_skip_file_neither_given_never_skips() -> None:
    """
    Asserts get_skip_file never skips a file when neither
    extension nor keyword is given.
    """
    # getting skip bool with no filters given
    skip_bool = get_skip_file(file_name='module.py',
                              extension=None,
                              keyword=None)

    # asserting file is never skipped
    assert skip_bool is False


@mark.parametrize('file_name, expected_skip',
                  [('module.py', False),
                   ('module.txt', True)])
def test_get_skip_file_only_extension(file_name: str,
                                      expected_skip: bool
                                      ) -> None:
    """
    Asserts get_skip_file filters purely on extension
    when only extension is given.
    """
    # getting skip bool with only extension given
    skip_bool = get_skip_file(file_name=file_name,
                              extension='.py',
                              keyword=None)

    # asserting skip bool matches expectation
    assert skip_bool is expected_skip


@mark.parametrize('file_name, expected_skip',
                  [('my_module.py', False),
                   ('other.py', True)])
def test_get_skip_file_only_keyword(file_name: str,
                                    expected_skip: bool
                                    ) -> None:
    """
    Asserts get_skip_file filters purely on keyword
    when only keyword is given.
    """
    # getting skip bool with only keyword given
    skip_bool = get_skip_file(file_name=file_name,
                              extension=None,
                              keyword='my_module')

    # asserting skip bool matches expectation
    assert skip_bool is expected_skip


@mark.parametrize('file_name, extension, keyword, expected_skip',
                  [('my_module.py', '.py', 'my_module', False),
                   ('my_module.txt', '.py', 'my_module', True),
                   ('other.py', '.py', 'my_module', True),
                   ('other.txt', '.py', 'my_module', True)])
def test_get_skip_file_both_given_match_both_to_keep(file_name: str,
                                                      extension: str,
                                                      keyword: str,
                                                      expected_skip: bool
                                                      ) -> None:
    """
    Asserts get_skip_file requires a file to match BOTH
    extension and keyword to be kept when both are given -
    any single mismatch is enough to skip it.
    """
    # getting skip bool with both extension and keyword given
    skip_bool = get_skip_file(file_name=file_name,
                              extension=extension,
                              keyword=keyword)

    # asserting skip bool matches expectation
    assert skip_bool is expected_skip

######################################################################
# end of current module
