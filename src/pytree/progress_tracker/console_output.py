# console_output module

# Code destined to defining
# progress tracker console
# output related functions.

######################################################################
# imports

from sys import stdout
from pytree.shared.console import get_number_string

#####################################################################
# functions


def get_percentage_string(percentage: int) -> str:
    """
    Given a value in percentage,
    returns value as a string,
    adding '%' to the right side.

    Args:
        percentage (int): The percentage value to convert.

    Returns:
        str: The formatted percentage string.
    """
    # updating value to be in range of 2 digits
    percentage_str = get_number_string(num=percentage,
                                       digits=2)

    # assembling percentage string
    percentage_string = f'{percentage_str}%'

    # checking if percentage is 100%
    if percentage == 100:

        # updating percentage string
        percentage_string = '100%'

    # returning percentage string
    return percentage_string


def clear_progress(progress_string: str) -> None:
    """
    Writes empty space to cover current
    progress string's size in console.

    Args:
        progress_string (str): The current progress string, whose size defines the space to clear.

    Returns:
        None.
    """
    # getting current progress string length
    string_len = len(progress_string)

    # creating empty line
    empty_line = ' ' * string_len

    # creating backspace line
    backspace_line = '\b' * string_len

    # writing string
    stdout.write(empty_line)

    # flushing console
    stdout.flush()

    # resetting cursor to start of the line
    stdout.write(backspace_line)


def print_totals(totals_string: str,
                 progress_string: str
                 ) -> None:
    """
    Prints iterations totals.

    Args:
        totals_string (str): The totals string to print.
        progress_string (str): The current progress string, used to clear the console.

    Returns:
        None.
    """
    # clearing console
    clear_progress(progress_string=progress_string)

    # printing totals string
    print(totals_string)

######################################################################
# end of current module
