# test_time_utils module

# Code destined to testing progress_tracker/time_utils.py's
# get_current_time/get_elapsed_time/get_etc functions.

######################################################################
# imports

# importing required libraries
from pytree.progress_tracker.time_utils import get_etc
from pytree.progress_tracker.time_utils import get_current_time
from pytree.progress_tracker.time_utils import get_elapsed_time

######################################################################
# defining get_current_time test cases


def test_get_current_time_returns_frozen_seconds(frozen_time) -> None:
    """
    Asserts get_current_time returns the frozen time.time()
    value truncated to whole seconds.
    """
    # freezing time.time() to a fractional-second value
    frozen_time([100.9])

    # getting current time
    current_time = get_current_time()

    # asserting current time was truncated (not rounded) to whole seconds
    assert current_time == 100

######################################################################
# defining get_elapsed_time test cases


def test_get_elapsed_time_returns_difference() -> None:
    """
    Asserts get_elapsed_time returns the difference between
    current time and start time, in seconds.
    """
    # getting elapsed time
    elapsed_time = get_elapsed_time(start_time=10,
                                    current_time=25)

    # asserting elapsed time matches the expected difference
    assert elapsed_time == 15

######################################################################
# defining get_etc test cases


def test_get_etc_before_first_iteration_returns_base_value() -> None:
    """
    Asserts get_etc returns its base fallback value (3600) when
    current_iteration is still 0 (the "first iteration is running"
    guard has not been crossed yet).
    """
    # getting etc before any iteration has run
    etc = get_etc(iterations_num=10,
                  current_iteration=0,
                  skipped_iterations=0,
                  elapsed_time=5)

    # asserting base fallback value was returned
    assert etc == 3600


def test_get_etc_normal_case_computes_estimate() -> None:
    """
    Asserts get_etc computes a proportional estimate based on
    iterations remaining and elapsed time, once iterations have
    started.
    """
    # getting etc for a normal, in-progress case
    etc = get_etc(iterations_num=10,
                  current_iteration=5,
                  skipped_iterations=0,
                  elapsed_time=10)

    # asserting proportional estimate (5 remaining * 10s elapsed / 5 done)
    assert etc == 10


def test_get_etc_current_equals_skipped_falls_back() -> None:
    """
    Asserts get_etc falls back to 60 when current_iteration equals
    skipped_iterations, which would otherwise raise ZeroDivisionError
    in the denominator (current_iteration - skipped_iterations).
    """
    # getting etc where every completed iteration was skipped
    etc = get_etc(iterations_num=10,
                  current_iteration=3,
                  skipped_iterations=3,
                  elapsed_time=10)

    # asserting the ZeroDivisionError-guarded fallback was used
    assert etc == 60

######################################################################
# end of current module
