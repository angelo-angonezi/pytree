# test_console module

# Code destined to testing shared/console.py's
# console width/flush and progress-bar number/
# time formatting functions.

######################################################################
# imports

# importing required libraries
from pytest import mark
from pytree.shared.console import flush_string
from pytree.shared.console import get_time_str
from pytree.shared.console import get_console_width
from pytree.shared.console import get_number_string

######################################################################
# defining get_console_width test cases


def test_get_console_width_raises_falls_through(mock_terminal_size) -> None:
    """
    Asserts get_console_width lets OSError from
    os.get_terminal_size (the real behavior under
    pytest's default capture) propagate uncaught.
    """
    # setting mocked terminal size to raise OSError
    mock_terminal_size(raise_error=True)

    # attempting to get console width, expecting OSError to propagate
    try:
        get_console_width()
        raised = False
    except OSError:
        raised = True

    # asserting OSError was indeed raised
    assert raised is True


def test_get_console_width_fixed_size(mock_terminal_size) -> None:
    """
    Asserts get_console_width returns the mocked
    fixed terminal width.
    """
    # setting mocked terminal size to a fixed width/height
    mock_terminal_size(raise_error=False,
                       width=100,
                       height=30)

    # getting console width
    console_width = get_console_width()

    # asserting width matches the mocked value
    assert console_width == 100

######################################################################
# defining flush_string test cases


def test_flush_string_writes_padding_and_backspaces(mock_terminal_size,
                                                     monkeypatch
                                                     ) -> None:
    """
    Asserts flush_string writes the given string padded
    out to the console width (minus 5), followed by that
    many backspace characters. Patches stdout as imported
    into pytree.shared.console directly (a fake write-collecting
    object), rather than relying on capsys/capfd - console.py's
    "from sys import stdout" binds a direct object reference at
    import time, so a later sys.stdout swap or fd-level capture
    is unreliable depending on when the module was first imported.
    """
    # setting mocked terminal size to a fixed, small width
    mock_terminal_size(raise_error=False,
                       width=20,
                       height=24)

    # defining a fake stdout that just collects every write() call
    class FakeStdout:
        """
        Minimal stand-in for sys.stdout, collecting every
        write() call into a list; flush() is a no-op.
        """
        def __init__(self) -> None:
            self.writes = []

        def write(self, text: str) -> None:
            self.writes.append(text)

        def flush(self) -> None:
            pass

    # instantiating fake stdout
    fake_stdout = FakeStdout()

    # patching stdout as imported into pytree.shared.console
    monkeypatch.setattr('pytree.shared.console.stdout', fake_stdout)

    # flushing a short string
    flush_string('hi')

    # computing expected padded string (width - len - 5 spaces)
    expected_padding = ' ' * (20 - 2 - 5)
    expected_string = f'hi{expected_padding}'

    # computing expected backspace line
    expected_backspaces = '\b' * len(expected_string)

    # asserting the padded string then the backspace line were each written
    assert fake_stdout.writes == [expected_string, expected_backspaces]

######################################################################
# defining get_number_string test cases


def test_get_number_string_int_pads_with_leading_zeroes() -> None:
    """
    Asserts get_number_string formats an int with
    leading zeroes to the given digit count.
    """
    # getting number string for an int
    number_string = get_number_string(num=5,
                                      digits=2)

    # asserting leading-zero padded format
    assert number_string == '05'


def test_get_number_string_float_uses_decimal_precision() -> None:
    """
    Asserts get_number_string formats a float with
    fixed decimal precision (not leading-zero padding).
    """
    # getting number string for a float
    number_string = get_number_string(num=5.0,
                                      digits=2)

    # asserting fixed-point decimal format
    assert number_string == '5.00'

######################################################################
# defining get_time_str test cases


@mark.parametrize('time_in_seconds, expected_time_str',
                  [(0, '0s'),
                   (59, '59s'),
                   (60, '1m'),
                   (3599, '60m'),
                   (3600, '1h')])
def test_get_time_str_boundaries(time_in_seconds: int,
                                 expected_time_str: str
                                 ) -> None:
    """
    Asserts get_time_str returns the expected unit at
    the 59s/60s/3599s/3600s/0s boundaries, including the
    3599s edge case that rounds up to "60m" rather than
    crossing into hours.
    """
    # getting time str
    time_str = get_time_str(time_in_seconds=time_in_seconds)

    # asserting time str matches expected
    assert time_str == expected_time_str

######################################################################
# end of current module
