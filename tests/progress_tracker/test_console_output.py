# test_console_output module

# Code destined to testing progress_tracker/console_output.py's
# get_percentage_string/clear_progress/print_totals functions.

######################################################################
# imports

# importing required libraries
from pytest import mark
from pytree.progress_tracker.console_output import print_totals
from pytree.progress_tracker.console_output import clear_progress
from pytree.progress_tracker.console_output import get_percentage_string

######################################################################
# defining get_percentage_string test cases


@mark.parametrize('percentage, expected_percentage_string',
                  [(0, '00%'),
                   (50, '50%'),
                   (100, '100%')])
def test_get_percentage_string_at_key_values(percentage: int,
                                             expected_percentage_string: str
                                             ) -> None:
    """
    Asserts get_percentage_string formats 0/50/100 percentages
    correctly, including the special-cased 100% (which bypasses
    the 2-digit leading-zero padding used for every other value).
    """
    # getting percentage string
    percentage_string = get_percentage_string(percentage=percentage)

    # asserting percentage string matches expected
    assert percentage_string == expected_percentage_string

######################################################################
# defining a fake stdout helper (shared by clear_progress/print_totals)


class FakeStdout:
    """
    Minimal stand-in for sys.stdout, collecting every write() call
    into a list; flush() is a no-op. Needed because console_output.py's
    "from sys import stdout" binds a direct object reference at import
    time, so a later sys.stdout swap or fd-level capture (capsys) is
    unreliable depending on when the module was first imported.
    """
    def __init__(self) -> None:
        self.writes = []

    def write(self, text: str) -> None:
        self.writes.append(text)

    def flush(self) -> None:
        pass

######################################################################
# defining clear_progress test cases


def test_clear_progress_writes_spaces_then_backspaces(monkeypatch) -> None:
    """
    Asserts clear_progress writes a run of spaces matching the given
    progress string's length, followed by that many backspace chars.
    """
    # instantiating fake stdout
    fake_stdout = FakeStdout()

    # patching stdout as imported into pytree.progress_tracker.console_output
    monkeypatch.setattr('pytree.progress_tracker.console_output.stdout', fake_stdout)

    # clearing progress for a known-length string
    clear_progress(progress_string='abcde')

    # asserting spaces then backspaces were written, matching string length
    assert fake_stdout.writes == [' ' * 5, '\b' * 5]

######################################################################
# defining print_totals test cases


def test_print_totals_clears_then_prints_totals_string(monkeypatch, capsys) -> None:
    """
    Asserts print_totals clears the current progress string from the
    console before printing the totals string on its own line.
    """
    # instantiating fake stdout (captures only the clear_progress writes)
    fake_stdout = FakeStdout()

    # patching stdout as imported into pytree.progress_tracker.console_output
    monkeypatch.setattr('pytree.progress_tracker.console_output.stdout', fake_stdout)

    # printing totals given a progress string to clear
    print_totals(totals_string='totals... | iterations: 1',
                 progress_string='abc')

    # asserting the clear (space + backspace pair) was written to the fake stdout
    assert fake_stdout.writes == [' ' * 3, '\b' * 3]

    # capturing console output (print() still goes through the real, captured stdout)
    captured = capsys.readouterr()

    # asserting the totals string was printed on its own line
    assert captured.out == 'totals... | iterations: 1\n'

######################################################################
# end of current module
