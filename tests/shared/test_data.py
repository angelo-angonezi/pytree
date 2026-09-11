# test_data module

# Code destined to testing shared/data.py's
# dict reversal and DataFrame saving functions.

######################################################################
# imports

# importing required libraries
from pathlib import Path
from pandas import read_csv
from pandas import DataFrame
from pytree.shared.data import save_df
from pytree.shared.data import reverse_dict

######################################################################
# defining reverse_dict test cases


def test_reverse_dict_empty() -> None:
    """
    Asserts reverse_dict returns an empty dict
    when given an empty dict.
    """
    # reversing an empty dict
    reversed_result = reverse_dict(a_dict={})

    # asserting result is still empty
    assert reversed_result == {}


def test_reverse_dict_single_item() -> None:
    """
    Asserts reverse_dict returns an equivalent
    single-item dict when given one item.
    """
    # reversing a single-item dict
    reversed_result = reverse_dict(a_dict={'a': 1})

    # asserting result is unchanged
    assert reversed_result == {'a': 1}


def test_reverse_dict_multi_item() -> None:
    """
    Asserts reverse_dict reverses the insertion
    order of a multi-item dict.
    """
    # reversing a multi-item dict
    reversed_result = reverse_dict(a_dict={'a': 1, 'b': 2, 'c': 3})

    # asserting keys came back in reverse insertion order
    assert list(reversed_result.keys()) == ['c', 'b', 'a']

    # asserting values are still correctly paired with their keys
    assert reversed_result == {'c': 3, 'b': 2, 'a': 1}

######################################################################
# defining save_df test cases


def test_save_df_round_trip(tmp_path: Path) -> None:
    """
    Asserts save_df writes a DataFrame to a CSV file
    that reads back with the same content.
    """
    # building a small dataframe
    df = DataFrame({'name': ['file_a', 'file_b'],
                    'size': [10, 20]})

    # defining save path
    save_path = str(tmp_path / 'output.csv')

    # saving dataframe
    save_df(save_path=save_path,
            df=df)

    # reading dataframe back
    read_back_df = read_csv(save_path)

    # asserting round-tripped content matches original
    assert read_back_df['name'].tolist() == ['file_a', 'file_b']
    assert read_back_df['size'].tolist() == [10, 20]

######################################################################
# end of current module
