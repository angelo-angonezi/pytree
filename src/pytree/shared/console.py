# console module

# Code destined to storing console
# formatting related functions.

######################################################################
# imports

# importing required libraries
from sys import stdout
from os import get_terminal_size

######################################################################
# defining console functions


def get_console_width() -> int:
    """
    Returns current console width.
    """
    # getting console dimensions
    width, _ = get_terminal_size()

    # returning console width
    return width


def flush_string(string: str) -> None:
    """
    Given a string, writes and flushes it in the console using
    sys library, and resets cursor to the start of the line.
    (writes N backspaces at the end of line, where N = len(string)).
    """
    # getting console width
    console_width = get_console_width()

    # getting string length
    string_len = len(string)

    # getting size difference
    width_diff = console_width - string_len

    # discounting from width diff to avoid console overflow
    width_diff -= 5

    # getting spacer
    empty_space = ' ' * width_diff

    # updating string
    string += empty_space

    # getting updated string length
    string_len = len(string)

    # creating backspace line
    backspace_line = '\b' * string_len

    # writing string
    stdout.write(string)

    # flushing console
    stdout.flush()

    # resetting cursor to start of the line
    stdout.write(backspace_line)


def get_number_string(num: int | float,
                      digits: int = 2
                      ) -> str:
    """
    Given a number, returns formatted
    number with leading zeroes so that
    the number of digits param is preserved.
    """
    # getting is int bool
    num_is_int = isinstance(num, int)

    # checking if number is int
    if num_is_int:

        # formating number string
        number_string = f'{num:0{digits}d}'

    else:

        # formating number string
        number_string = f'{num:4.{digits}f}'

    # returning formatted number string
    return number_string


def get_time_str(time_in_seconds: int) -> str:
    """
    Given a time in seconds, returns time in
    adequate format (seconds, minutes or hours).
    """
    # checking whether seconds > 60
    if time_in_seconds >= 60:

        # converting time to minutes
        time_in_minutes = time_in_seconds / 60

        # checking whether minutes > 60
        if time_in_minutes >= 60:

            # converting time to hours
            time_in_hours = time_in_minutes / 60

            # defining time string based on hours
            defined_time = round(time_in_hours)
            time_string = f'{defined_time}h'

        else:

            # defining time string based on minutes
            defined_time = round(time_in_minutes)
            time_string = f'{defined_time}m'

    else:

        # defining time string based on seconds
        defined_time = round(time_in_seconds)
        time_string = f'{defined_time}s'

    # returning time string
    return time_string

######################################################################
# end of current module
