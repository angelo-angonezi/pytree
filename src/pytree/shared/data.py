# data module

# Code destined to storing dict/
# DataFrame utility functions.

######################################################################
# imports

# importing required libraries
from pandas import DataFrame

######################################################################
# defining data functions


def reverse_dict(a_dict: dict) -> dict:
    """
    Given a dictionary, returns
    reversed dict.
    """
    # getting dict items
    dict_items = a_dict.items()

    # reversing items
    reversed_items = reversed(dict_items)

    # reassembling dict
    reversed_dict = dict(reversed_items)

    # returning reversed dict
    return reversed_dict


def save_df(save_path: str,
            df: DataFrame
            ) -> None:
    """
    Given a dataframe, saves it
    to given save path.
    """
    # saving df
    df.to_csv(path_or_buf=save_path,
              index=False)

######################################################################
# end of current module
