# size module

# Code destined to storing byte size
# formatting related functions.

######################################################################
# imports

# importing required libraries
from pytree.shared.global_vars import ONE_KB
from pytree.shared.global_vars import ONE_MB
from pytree.shared.global_vars import ONE_GB
from pytree.shared.global_vars import ONE_TB

######################################################################
# defining size functions


def get_size_str(size_in_bytes: int) -> str:
    """
    Given a file/folder size in bytes,
    returns a string in human readable
    format.
    """
    # defining placeholder value for unit str/normalizer
    unit_str = 'bytes'
    normalizer = 1

    # checking if size in bytes exceeds a terabyte
    if size_in_bytes >= ONE_TB:

        # updating unit str/normalizer
        unit_str = 'tb'
        normalizer *= ONE_TB

    # checking if size in bytes exceeds a gigabyte
    elif size_in_bytes >= ONE_GB:

        # updating unit str/normalizer
        unit_str = 'gb'
        normalizer *= ONE_GB

    # checking if size in bytes exceeds a megabyte
    elif size_in_bytes >= ONE_MB:

        # updating unit str/normalizer
        unit_str = 'mb'
        normalizer *= ONE_MB

    # checking if size in bytes exceeds a kilobyte
    elif size_in_bytes >= ONE_KB:

        # updating unit str/normalizer
        unit_str = 'kb'
        normalizer *= ONE_KB

    # getting adjusted size
    adjusted_size = size_in_bytes / normalizer

    # rounding value
    adjusted_size = round(adjusted_size)

    # assembling size str
    size_str = f'{adjusted_size} {unit_str}'

    # returning size str
    return size_str

######################################################################
# end of current module
