# conftest module

# Code destined to defining shared
# pytest fixtures used across the
# whole test suite.

######################################################################
# imports

# importing required libraries
from pathlib import Path
from pytest import fixture
from os import terminal_size

######################################################################
# fake progress tracker


class FakeProgressTracker:
    """
    Defines a lightweight stand-in for ModuleProgressTracker, exposing only the
    attributes that TreeScanner/PyTree actually read or mutate, so core/ tests
    never construct a real progress tracker (which would start a background
    thread and could reach os._exit via force_quit).
    """
    def __init__(self) -> None:
        """
        Initializes a FakeProgressTracker instance
        and defines placeholder attributes.
        """
        # folders
        self.current_folder = 0

        # files
        self.files_num = 0
        self.current_file = 0

        # iteration (read by TreeScanner.scan_folder)
        self.current_iteration = 0

        # tree/end string (written by PyTree.update_tree/update_end_string/update_print_end_string)
        self.tree = None
        self.end_string = ''
        self.print_end_string = ''


@fixture
def fake_progress_tracker() -> FakeProgressTracker:
    """
    Returns a fresh FakeProgressTracker instance,
    to be passed via the progress_tracker= constructor
    parameter of TreeScanner/PyTree.
    """
    # returning a fresh fake progress tracker
    return FakeProgressTracker()

######################################################################
# small tree fixture


@fixture
def small_tree(tmp_path: Path) -> tuple:
    """
    Builds a tiny deterministic folder tree under tmp_path (nested folders, two
    .py files with hand-computed LOC/comment counts, one .txt file with a known
    size, and one __pycache__ folder to exercise cache exclusion), returning
    the root path plus a dict of expected counts/sizes/LOC - the shared oracle
    for core/ and integration/ tests.
    """
    # defining root folder
    root = tmp_path / 'root'
    root.mkdir()

    # defining sub1 folder (holds the .py/.txt files)
    sub1 = root / 'sub1'
    sub1.mkdir()

    # defining sub2 folder (holds the __pycache__ folder)
    sub2 = root / 'sub2'
    sub2.mkdir()

    # defining cache folder (must be excluded from every total)
    cache_folder = sub2 / '__pycache__'
    cache_folder.mkdir()

    # defining file_a content (1 comment-only line, 1 code line, 1 code+inline-comment line)
    file_a_content = '# comment line\n'
    file_a_content += 'x = 1\n'
    file_a_content += 'y = 2  # inline comment\n'

    # hand-computed loc/com for file_a (a line with a trailing "#" comment counts as both)
    file_a_loc = 2
    file_a_com = 2

    # writing file_a
    file_a = sub1 / 'file_a.py'
    file_a.write_text(file_a_content)

    # defining file_b content (plain, non-python, fixed-size file)
    file_b_content = '0123456789'
    file_b_size = len(file_b_content.encode())

    # writing file_b
    file_b = sub1 / 'file_b.txt'
    file_b.write_text(file_b_content)

    # writing a file inside the cache folder (must never be counted)
    cache_file = cache_folder / 'cache_file.pyc'
    cache_file.write_bytes(b'\x00' * 4)

    # getting file_a size (computed from the same content written above)
    file_a_size = len(file_a_content.encode())

    # assembling expected totals dict (root/sub1/sub2 folders; file_a/file_b files;
    # cache_folder and its contents excluded entirely)
    expected = {'root': str(root),
               'sub1': str(sub1),
               'sub2': str(sub2),
               'cache_folder': str(cache_folder),
               'file_a': str(file_a),
               'file_b': str(file_b),
               'file_a_loc': file_a_loc,
               'file_a_com': file_a_com,
               'file_a_size': file_a_size,
               'file_b_size': file_b_size,
               'total_folders': 3,
               'total_files': 2,
               'total_size': (file_a_size + file_b_size),
               'total_loc': file_a_loc,
               'total_com': file_a_com,
               'valid_py_files': 1}

    # returning root path and expected totals dict
    return str(root), expected

######################################################################
# terminal size mocking fixture


@fixture
def mock_terminal_size(monkeypatch) -> callable:
    """
    Returns a setter function that monkeypatches os.get_terminal_size (as
    imported into pytree.shared.console) to either raise OSError (the real
    behavior under pytest's default capture) or return a fixed terminal_size,
    for shared/console.py tests.
    """
    def _set_terminal_size(raise_error: bool = False,
                           width: int = 80,
                           height: int = 24
                           ) -> None:
        """
        Sets the mocked os.get_terminal_size behavior.
        """
        # checking whether to raise OSError
        if raise_error:

            # defining a fake terminal size getter that raises OSError
            def fake_get_terminal_size() -> terminal_size:
                raise OSError('mocked terminal size error')

        else:

            # defining fixed terminal size
            fixed_size = terminal_size((width, height))

            # defining a fake terminal size getter that returns the fixed size
            def fake_get_terminal_size() -> terminal_size:
                return fixed_size

        # patching get_terminal_size as imported into pytree.shared.console
        monkeypatch.setattr('pytree.shared.console.get_terminal_size',
                            fake_get_terminal_size)

    # returning the setter function
    return _set_terminal_size

######################################################################
# frozen time fixture


@fixture
def frozen_time(monkeypatch) -> callable:
    """
    Returns a setter function that monkeypatches time.time (as imported into
    pytree.progress_tracker.time_utils) to a controllable sequence of values,
    for deterministic elapsed-time/ETC tests. Once the sequence is exhausted,
    the last value keeps being returned.
    """
    def _set_time_sequence(times: list) -> None:
        """
        Sets the sequence of values time.time() will return.
        """
        # creating an iterator over the given times
        times_iterator = iter(times)

        # defining a fake time function drawing from the sequence
        def fake_time() -> float:
            """
            Returns the next value in the sequence, or the last
            value forever once the sequence is exhausted.
            """
            # attempting to get next scheduled time
            try:

                # getting next time
                current = next(times_iterator)

            except StopIteration:

                # falling back to the last given time
                current = times[-1]

            # returning current fake time
            return current

        # patching time as imported into pytree.progress_tracker.time_utils
        monkeypatch.setattr('pytree.progress_tracker.time_utils.time',
                            fake_time)

    # returning the setter function
    return _set_time_sequence

######################################################################
# end of current module
