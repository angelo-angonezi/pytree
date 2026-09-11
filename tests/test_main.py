# test_main module

# Code destined to testing main.py's argument parsing (get_args_dict),
# via monkeypatch.setattr(sys, "argv", ...). main() itself is never
# called, since it constructs a real ModuleProgressTracker and drives
# it in a background thread via run() (see progress_tracker tests'
# no-run() rule).

######################################################################
# imports

# importing required libraries
from pytest import MonkeyPatch
from pytree.main import get_args_dict

######################################################################
# defining get_args_dict test cases


def test_get_args_dict_defaults(monkeypatch: MonkeyPatch) -> None:
    """
    Asserts get_args_dict returns the expected default values
    when only a start_path positional argument is given.
    """
    # setting argv to just the program name and a start path
    monkeypatch.setattr('sys.argv', ['pytree', '.'])

    # parsing args
    args_dict = get_args_dict()

    # asserting defaults
    assert args_dict['start_path'] == ['.']
    assert args_dict['dirs_only'] is False
    assert args_dict['show_counts'] is False
    assert args_dict['show_sizes'] is False
    assert args_dict['extension'] is None
    assert args_dict['keyword'] is None
    assert args_dict['level'] == -1
    assert args_dict['loc'] is False
    assert args_dict['output_path'] is None
    assert args_dict['quiet'] is False


def test_get_args_dict_no_start_path_defaults_to_dot(monkeypatch: MonkeyPatch) -> None:
    """
    Asserts get_args_dict falls back to the string default='.' (not a
    list) for start_path when no positional argument is given at all -
    argparse only applies a nargs='*' argument's default when zero
    values are supplied, leaving it as the raw string rather than
    wrapping it in a list.
    """
    # setting argv to just the program name
    monkeypatch.setattr('sys.argv', ['pytree'])

    # parsing args
    args_dict = get_args_dict()

    # asserting start_path falls back to the raw string default
    assert args_dict['start_path'] == '.'


def test_get_args_dict_short_flag_combination(monkeypatch: MonkeyPatch) -> None:
    """
    Asserts get_args_dict correctly parses a combination of short
    flags together with the -x/-k/-l/-o value-taking options.
    """
    # setting argv to a representative flag combination
    monkeypatch.setattr('sys.argv', ['pytree',
                                     'some_folder',
                                     '-dcs',
                                     '-x', '.py',
                                     '-k', 'test',
                                     '-l', '2',
                                     '-o', 'out.csv'])

    # parsing args
    args_dict = get_args_dict()

    # asserting parsed values
    assert args_dict['start_path'] == ['some_folder']
    assert args_dict['dirs_only'] is True
    assert args_dict['show_counts'] is True
    assert args_dict['show_sizes'] is True
    assert args_dict['extension'] == '.py'
    assert args_dict['keyword'] == 'test'
    assert args_dict['level'] == 2
    assert args_dict['output_path'] == 'out.csv'


def test_get_args_dict_loc_and_quiet_flags(monkeypatch: MonkeyPatch) -> None:
    """
    Asserts get_args_dict correctly parses the long forms of the
    -loc/--lines-of-code and -q/--quiet flags.
    """
    # setting argv with long-form loc and quiet flags
    monkeypatch.setattr('sys.argv', ['pytree', '.', '--lines-of-code', '--quiet'])

    # parsing args
    args_dict = get_args_dict()

    # asserting loc and quiet are both True
    assert args_dict['loc'] is True
    assert args_dict['quiet'] is True


def test_get_args_dict_multiple_start_path_args(monkeypatch: MonkeyPatch) -> None:
    """
    Asserts get_args_dict collects multiple positional start_path
    arguments into a list (nargs='*'), documenting that get_start_path
    is responsible for reducing this list down to a single path.
    """
    # setting argv with two positional start_path arguments
    monkeypatch.setattr('sys.argv', ['pytree', 'folder_a', 'folder_b'])

    # parsing args
    args_dict = get_args_dict()

    # asserting both positional args were collected
    assert args_dict['start_path'] == ['folder_a', 'folder_b']

######################################################################
# end of current module
