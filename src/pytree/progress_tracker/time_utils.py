# time_utils module

# Code destined to defining
# time related functions.

######################################################################
# imports

from time import time

#####################################################################
# functions


def get_current_time() -> int:
    """
    Gets current UTC time, in seconds.

    Returns:
        int: The current UTC time, in seconds.
    """
    # getting current time
    current_time = time()

    # getting seconds
    current_seconds = int(current_time)

    # returning current time in seconds
    return current_seconds


def get_elapsed_time(start_time: int,
                     current_time: int
                     ) -> int:
    """
    Returns time difference
    between start time and
    current time, in seconds.

    Args:
        start_time (int): The start time, in seconds.
        current_time (int): The current time, in seconds.

    Returns:
        int: The elapsed time, in seconds.
    """
    # getting elapsed time (time difference)
    elapsed_time = current_time - start_time

    # returning elapsed time
    return elapsed_time


def get_etc(iterations_num: int,
            current_iteration: int,
            skipped_iterations: int,
            elapsed_time: int
            ) -> int:
    """
    Based on iteration and time
    attributes, returns estimated
    time of completion (ETC).

    Args:
        iterations_num (int): The total number of iterations.
        current_iteration (int): The current iteration number.
        skipped_iterations (int): The number of skipped iterations.
        elapsed_time (int): The elapsed time, in seconds.

    Returns:
        int: The estimated time of completion, in seconds.
    """
    # defining base value for etc
    etc = 3600

    # getting iterations to go
    iterations_to_go = iterations_num - current_iteration

    # checking if first iteration is running
    if current_iteration >= 1:

        # calculating estimated time of completion
        numerator = (iterations_to_go * elapsed_time)
        denominator = (current_iteration - skipped_iterations)
        try:
            etc = numerator / denominator
        except ZeroDivisionError:
            etc = 60

        # rounding time
        etc = round(etc)

        # converting estimated time of completion to int
        etc = int(etc)

    # returning estimated time of completion
    return etc

######################################################################
# end of current module
