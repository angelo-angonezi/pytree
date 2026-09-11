# test_treescanner module

# Code destined to testing TreeScanner's path-dict helpers and
# scan_file/scan_subfolder/scan_folder/get_tree_dict methods, using
# the small_tree fixture and a FakeProgressTracker (never a real,
# thread-driving ModuleProgressTracker).

######################################################################
# imports

# importing required libraries
from os.path import join
from pytest import MonkeyPatch
from pytree.core.TreeScanner import TreeScanner
from pytree.shared.global_vars import CACHE_FOLDERS

######################################################################
# helper for building a scanner against small_tree


def build_scanner(root: str,
                  fake_progress_tracker,
                  extension: str | None = None,
                  keyword: str | None = None,
                  loc: bool = False,
                  include_sizes: bool = True,
                  include_counts: bool = True
                  ) -> TreeScanner:
    """
    Returns a TreeScanner instance configured against the given
    small_tree root path, using the given fake progress tracker.
    """
    # getting root depth (mirrors PyTree's start_level derivation)
    root_depth = len(root.split('\\')) if '\\' in root else len(root.split('/'))

    # building and returning scanner instance
    return TreeScanner(start_path=root,
                       extension=extension,
                       keyword=keyword,
                       loc=loc,
                       include_sizes=include_sizes,
                       include_counts=include_counts,
                       cache_folders=CACHE_FOLDERS,
                       start_is_cache=False,
                       start_level=root_depth,
                       progress_tracker=fake_progress_tracker)

######################################################################
# defining get_path_level/get_path_dict test cases


def test_get_path_level_root_is_zero_and_child_is_one(small_tree, fake_progress_tracker) -> None:
    """
    Asserts get_path_level returns 0 for the start path itself and
    1 for a direct child folder.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building scanner against small tree root
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker)

    # asserting root level is 0
    assert scanner.get_path_level(path=root) == 0

    # asserting sub1 (direct child) level is 1
    assert scanner.get_path_level(path=expected['sub1']) == 1


def test_get_path_dict_matches_known_file(small_tree, fake_progress_tracker) -> None:
    """
    Asserts get_path_dict returns the expected name/path/level/parent
    for a known small_tree file path.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building scanner against small tree root
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker)

    # getting path dict for file_a
    path_dict = scanner.get_path_dict(name='file_a.py',
                                      path=expected['file_a'])

    # asserting expected fields
    assert path_dict['name'] == 'file_a.py'
    assert path_dict['path'] == expected['file_a']
    assert path_dict['level'] == 2
    assert path_dict['parent'] == expected['sub1']

######################################################################
# defining get_file_dict/get_folder_dict test cases


def test_get_file_dict_includes_size_and_loc(small_tree, fake_progress_tracker) -> None:
    """
    Asserts get_file_dict includes size/loc/com fields when the
    respective toggles are enabled, matching hand-computed values.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building scanner with sizes and loc enabled
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker,
                            loc=True,
                            include_sizes=True,
                            include_counts=False)

    # getting file dict for file_a
    file_dict = scanner.get_file_dict(file_name='file_a.py',
                                      file_path=expected['file_a'])

    # asserting type and size/loc/com fields
    assert file_dict['type'] == 'file'
    assert file_dict['size'] == expected['file_a_size']
    assert file_dict['loc'] == expected['file_a_loc']
    assert file_dict['com'] == expected['file_a_com']


def test_get_file_dict_omits_size_and_loc_when_disabled(small_tree, fake_progress_tracker) -> None:
    """
    Asserts get_file_dict omits size/loc/com fields when their
    respective toggles are disabled.
    """
    # unpacking small tree root path
    root, expected = small_tree

    # building scanner with sizes and loc disabled
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker,
                            loc=False,
                            include_sizes=False,
                            include_counts=False)

    # getting file dict for file_a
    file_dict = scanner.get_file_dict(file_name='file_a.py',
                                      file_path=expected['file_a'])

    # asserting size/loc/com fields are absent
    assert 'size' not in file_dict
    assert 'loc' not in file_dict
    assert 'com' not in file_dict


def test_get_folder_dict_uses_current_running_totals(small_tree, fake_progress_tracker) -> None:
    """
    Asserts get_folder_dict pulls size/count/loc/com from the
    scanner's current_folder_* running totals, not from a fresh
    computation.
    """
    # unpacking small tree root path
    root, expected = small_tree

    # building scanner with all toggles enabled
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker,
                            loc=True,
                            include_sizes=True,
                            include_counts=True)

    # seeding running totals as if a folder had just been scanned
    scanner.current_folder_size = 123
    scanner.current_items_count = 4
    scanner.current_folder_loc = 5
    scanner.current_folder_com = 6

    # getting folder dict for sub1
    folder_dict = scanner.get_folder_dict(folder_name='sub1',
                                          folder_path=expected['sub1'])

    # asserting type and running-totals fields
    assert folder_dict['type'] == 'folder'
    assert folder_dict['size'] == 123
    assert folder_dict['count'] == 4
    assert folder_dict['loc'] == 5
    assert folder_dict['com'] == 6

######################################################################
# defining scan_file test cases


def test_scan_file_swallows_oserror_and_skips_totals(small_tree,
                                                      fake_progress_tracker,
                                                      monkeypatch: MonkeyPatch
                                                      ) -> None:
    """
    Asserts scan_file swallows an OSError raised while building the
    file dict (e.g. getsize failing), never adding the file to
    tree_dict nor updating any running totals.
    """
    # unpacking small tree root path
    root, expected = small_tree

    # building scanner with sizes enabled (so getsize gets called)
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker,
                            include_sizes=True,
                            include_counts=True)

    # defining a getsize replacement that always raises OSError
    def raising_getsize(filename: str) -> int:
        raise OSError('mocked getsize failure')

    # patching getsize as imported into pytree.core.TreeScanner
    monkeypatch.setattr('pytree.core.TreeScanner.getsize',
                        raising_getsize)

    # scanning file_a, which should swallow the mocked OSError
    scanner.scan_file(file_name='file_a.py',
                      file_path=expected['file_a'])

    # asserting file was never added to tree dict
    assert expected['file_a'] not in scanner.tree_dict

    # asserting no totals were updated
    assert scanner.current_folder_size == 0
    assert scanner.total_size == 0
    assert scanner.current_items_count == 0

######################################################################
# defining scan_subfolder test cases


def test_scan_subfolder_returns_early_for_missing_subfolder(small_tree, fake_progress_tracker) -> None:
    """
    Asserts scan_subfolder returns without error and without
    touching running totals when the given subfolder path was never
    scanned (inaccessible/vanished mid-scan), i.e. is absent from
    tree_dict.
    """
    # unpacking small tree root path
    root, expected = small_tree

    # building scanner with all toggles enabled
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker,
                            loc=True,
                            include_sizes=True,
                            include_counts=True)

    # getting a subfolder path never scanned/added to tree_dict
    missing_subfolder_path = join(root, 'never_scanned')

    # scanning the missing subfolder, which should return early
    scanner.scan_subfolder(subfolder_path=missing_subfolder_path)

    # asserting no running totals were touched
    assert scanner.current_folder_size == 0
    assert scanner.current_items_count == 0
    assert scanner.current_folder_loc == 0
    assert scanner.current_folder_com == 0

######################################################################
# defining scan_folder test cases


def test_scan_folder_excludes_cache_subfolder(small_tree, fake_progress_tracker) -> None:
    """
    Asserts scan_folder skips a __pycache__ subfolder (via
    get_skip_folder), never calling scan_subfolder on it and never
    adding it to tree_dict.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building scanner with sizes/counts enabled
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker,
                            include_sizes=True,
                            include_counts=True)

    # pre-seeding tree_dict with sub2's __pycache__ folder, as if it had already
    # been scanned in a prior (bottom-up) os.walk iteration
    scanner.tree_dict[expected['cache_folder']] = {'name': '__pycache__',
                                                   'path': expected['cache_folder'],
                                                   'level': 2,
                                                   'parent': expected['sub2'],
                                                   'type': 'folder',
                                                   'size': 4,
                                                   'count': 1}

    # scanning sub2, whose only subfolder is the cache folder
    scanner.scan_folder(folder_path=expected['sub2'],
                        subfolders=['__pycache__'],
                        files=[])

    # asserting sub2's running totals were never incremented by the cache folder
    assert scanner.current_folder_size == 0
    assert scanner.current_items_count == 0

    # asserting sub2 itself was recorded in tree dict
    assert expected['sub2'] in scanner.tree_dict

######################################################################
# defining get_tree_dict test cases


def test_get_tree_dict_matches_small_tree_totals_and_excludes_cache(small_tree, fake_progress_tracker) -> None:
    """
    Asserts get_tree_dict's full scan over small_tree matches the
    fixture's expected totals and never includes the __pycache__
    folder or its contents.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building scanner with all toggles enabled - extension is set to '.py' to
    # mirror how PyTree itself forces it whenever loc=True, so only file_a.py
    # (not file_b.txt) contributes to the loc/comment totals
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker,
                            extension='.py',
                            loc=True,
                            include_sizes=True,
                            include_counts=True)

    # running full scan
    tree_dict = scanner.get_tree_dict()

    # asserting totals match expected values (total_size reflects only file_a,
    # since the '.py' extension filter above skips file_b.txt entirely)
    assert scanner.total_folders == expected['total_folders']
    assert scanner.total_files == expected['total_files']
    assert scanner.total_size == expected['file_a_size']
    assert scanner.total_loc == expected['total_loc']
    assert scanner.total_com == expected['total_com']

    # asserting cache folder and its contents are excluded from tree dict
    assert expected['cache_folder'] not in tree_dict

    # asserting every recorded path lies outside the cache folder
    cache_folder_paths = [path for path in tree_dict if expected['cache_folder'] in path]
    assert cache_folder_paths == []


def test_get_tree_dict_orders_parents_before_children(small_tree, fake_progress_tracker) -> None:
    """
    Asserts get_tree_dict's reverse_dict step restores parent-before-
    child key order (root, then sub1, then file_a), which
    core/converter.py's tree/df building relies on.
    """
    # unpacking small tree root path and expected totals
    root, expected = small_tree

    # building scanner with default toggles
    scanner = build_scanner(root=root,
                            fake_progress_tracker=fake_progress_tracker)

    # running full scan
    tree_dict = scanner.get_tree_dict()

    # getting ordered list of tree dict keys
    ordered_paths = list(tree_dict.keys())

    # getting index positions of root, sub1 and file_a
    root_index = ordered_paths.index(root)
    sub1_index = ordered_paths.index(expected['sub1'])
    file_a_index = ordered_paths.index(expected['file_a'])

    # asserting parent-before-child ordering
    assert root_index < sub1_index < file_a_index

######################################################################
# end of current module
