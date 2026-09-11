# test_size module

# Code destined to testing shared/size.py's
# byte size formatting function.

######################################################################
# imports

# importing required libraries
from pytest import mark
from pytree.shared.size import get_size_str
from pytree.shared.global_vars import ONE_KB
from pytree.shared.global_vars import ONE_MB
from pytree.shared.global_vars import ONE_GB
from pytree.shared.global_vars import ONE_TB

######################################################################
# defining test cases


@mark.parametrize('size_in_bytes, expected_size_str',
                  [(0, '0 bytes'),
                   (1, '1 bytes'),
                   ((ONE_KB - 1), '1023 bytes'),
                   (ONE_KB, '1 kb'),
                   ((ONE_MB - 1), '1024 kb'),
                   (ONE_MB, '1 mb'),
                   ((ONE_GB - 1), '1024 mb'),
                   (ONE_GB, '1 gb'),
                   ((ONE_TB - 1), '1024 gb'),
                   (ONE_TB, '1 tb')])
def test_get_size_str_boundaries(size_in_bytes: int,
                                 expected_size_str: str
                                 ) -> None:
    """
    Asserts get_size_str returns the expected unit/value at
    each just-below/exact ONE_KB/ONE_MB/ONE_GB/ONE_TB boundary.
    """
    # getting size str
    size_str = get_size_str(size_in_bytes=size_in_bytes)

    # asserting size str matches expected
    assert size_str == expected_size_str


def test_get_size_str_negative_input() -> None:
    """
    Documents current (unguarded) behavior of get_size_str
    when given a negative size in bytes - falls through every
    threshold check and is reported in raw bytes.
    """
    # getting size str for a negative input
    size_str = get_size_str(size_in_bytes=-10)

    # asserting negative size falls back to raw "bytes" formatting
    assert size_str == '-10 bytes'

######################################################################
# end of current module
