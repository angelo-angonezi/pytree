# test_progress_tracker module

# Code destined to testing ProgressTracker's isolated helper
# methods. Only pure/isolated methods are ever exercised here -
# run()/force_quit() are never called, since run() drives a real
# background thread and force_quit() calls os._exit(1), which
# would kill the pytest process itself.

######################################################################
# imports

# importing required libraries
from pytree.progress_tracker.ProgressTracker import ProgressTracker

######################################################################
# defining get_progress_percentage test cases


def test_get_progress_percentage_normal_case() -> None:
    """
    Asserts get_progress_percentage returns the rounded percentage
    of current_iteration over iterations_num.
    """
    # creating a fresh progress tracker
    progress_tracker = ProgressTracker()

    # setting iteration attributes
    progress_tracker.iterations_num = 10
    progress_tracker.current_iteration = 5

    # getting progress percentage
    progress_percentage = progress_tracker.get_progress_percentage()

    # asserting percentage matches expected
    assert progress_percentage == 50


def test_get_progress_percentage_zero_total_falls_back_to_zero() -> None:
    """
    Asserts get_progress_percentage falls back to 0 when
    iterations_num is 0 (which would otherwise raise
    ZeroDivisionError).
    """
    # creating a fresh progress tracker (iterations_num defaults to 0)
    progress_tracker = ProgressTracker()

    # getting progress percentage with no iterations set
    progress_percentage = progress_tracker.get_progress_percentage()

    # asserting the ZeroDivisionError-guarded fallback was used
    assert progress_percentage == 0

######################################################################
# defining update_wheel_symbol test cases


def test_update_wheel_symbol_cycles_through_symbols() -> None:
    """
    Asserts update_wheel_symbol cycles through the wheel symbol
    list in order, wrapping back to the start after the last index.
    """
    # creating a fresh progress tracker
    progress_tracker = ProgressTracker()

    # collecting the symbol produced by four consecutive updates
    symbols = []
    for _ in range(4):
        progress_tracker.update_wheel_symbol()
        symbols.append(progress_tracker.wheel_symbol)

    # asserting the full cycle (starting index 0, updated before use)
    assert symbols == ['|', '/', '-', '\\']


def test_update_wheel_symbol_overwrites_when_process_complete() -> None:
    """
    Asserts update_wheel_symbol overwrites the wheel symbol with a
    backspace character once process_complete has been set.
    """
    # creating a fresh progress tracker
    progress_tracker = ProgressTracker()

    # signaling process complete directly (bypassing signal_stop's wait)
    progress_tracker.process_complete.set()

    # updating wheel symbol
    progress_tracker.update_wheel_symbol()

    # asserting wheel symbol was overwritten with a backspace
    assert progress_tracker.wheel_symbol == '\b'

######################################################################
# defining get_progress_string test cases


def test_get_progress_string_before_totals_updated() -> None:
    """
    Asserts get_progress_string returns the "calculating iterations..."
    branch while totals_updated has not been set.
    """
    # creating a fresh progress tracker
    progress_tracker = ProgressTracker()

    # getting progress string before totals are updated
    progress_string = progress_tracker.get_progress_string()

    # asserting the calculating-iterations branch was used
    assert progress_string.startswith('calculating iterations...')


def test_get_progress_string_after_totals_updated() -> None:
    """
    Asserts get_progress_string returns the "running analysis..."
    branch once totals_updated has been set.
    """
    # creating a fresh progress tracker
    progress_tracker = ProgressTracker()

    # signaling totals updated directly
    progress_tracker.totals_updated.set()

    # getting progress string after totals are updated
    progress_string = progress_tracker.get_progress_string()

    # asserting the running-analysis branch was used
    assert progress_string.startswith('running analysis...')

######################################################################
# defining reset_timer test cases


def test_reset_timer_updates_start_time(frozen_time) -> None:
    """
    Asserts reset_timer sets start_time to the current frozen time.
    """
    # freezing time sequence (constructor call, then reset_timer call)
    frozen_time([100, 200])

    # creating a fresh progress tracker (consumes the first frozen time)
    progress_tracker = ProgressTracker()

    # resetting timer (consumes the second frozen time)
    progress_tracker.reset_timer()

    # asserting start time was updated to the new frozen time
    assert progress_tracker.start_time == 200

######################################################################
# defining update_time_attributes test cases


def test_update_time_attributes_computes_elapsed_and_etc_strings(frozen_time) -> None:
    """
    Asserts update_time_attributes updates current_time, elapsed_time,
    and their formatted string counterparts based on frozen time values.
    """
    # freezing time sequence (constructor call, then update_time_attributes call)
    frozen_time([100, 130])

    # creating a fresh progress tracker (start_time becomes 100)
    progress_tracker = ProgressTracker()

    # setting iteration attributes so get_etc computes a real estimate
    progress_tracker.iterations_num = 10
    progress_tracker.current_iteration = 1
    progress_tracker.skipped_iterations = 0

    # updating time attributes (current_time becomes 130)
    progress_tracker.update_time_attributes()

    # asserting elapsed time and its formatted string were updated
    assert progress_tracker.current_time == 130
    assert progress_tracker.elapsed_time == 30
    assert progress_tracker.elapsed_time_str == '30s'

    # asserting etc and its formatted string were updated (non-default values)
    assert progress_tracker.etc != 0
    assert progress_tracker.etc_str != ''

######################################################################
# end of current module
