# loc module

# Code destined to storing lines-of-code/
# comment counting related functions.

######################################################################
# imports

# importing required libraries
from re import sub
from re import escape
from re import DOTALL

######################################################################
# defining loc functions


def collapse_brackets(text: str) -> str:
    """
    Given a text, returns text clear
    of bracket-like line breaks.
    """
    # defining placeholder for bracket-likes list
    bracket_likes = [('(', ')'),
                     ('[', ']'),
                     ('{', '}'),
                     ('"""', '"""')]

    # iterating over bracket-likes list
    for bracket_like in bracket_likes:

        # getting bracket start/end
        bracket_start, bracket_end = bracket_like

        # assembling current pattern string
        pattern = f'({escape(bracket_start)}).*?({escape(bracket_end)})'

        # clearing text of current bracket like
        text = sub(pattern=pattern,
                   repl=r'\1\2',
                   string=text,
                   flags=DOTALL)

    # returning clean text
    return text


def get_loc(file_path: str) -> tuple:
    """
    Given a path to a python file,
    returns number of lines of code
    (disconsidering comments and enters)
    """
    # defining placeholder value for lines of code (loc) and comments (com)
    loc = 0
    com = 0

    # defining docstring symbol
    docstring_symbol = '"""'

    # defining comment symbol
    comment_symbol = '#'

    # defining read mode
    read_mode = 'r'

    # reading file
    with open(file_path, read_mode) as open_file:

        # getting text
        text = open_file.read()

        # cleaning text
        text = collapse_brackets(text=text)

        # getting file lines
        lines = text.split('\n')

        # iterating over lines
        for line in lines:

            # cleaning line
            line = line.strip()

            # getting line is empty bool
            line_is_empty = (line == '')

            # checking whether line is empty
            if line_is_empty:

                # skipping current line
                continue

            # getting line is comment bool
            line_is_comment = line.startswith(comment_symbol)

            # checking whether line is comment
            if line_is_comment:

                # updating comments count
                com += 1

                # skipping current line
                continue

            # getting line has inline comment bool
            line_has_comment = (comment_symbol in line)

            # checking whether line has comment
            if line_has_comment:

                # updating comments count
                com += 1

            # getting line is docstring bool
            line_is_docstring = line.startswith(docstring_symbol)

            # checking whether line is docstring
            if line_is_docstring:

                # updating comments count
                com += 1

                # skipping current line
                continue

            # updating lines of code count
            loc += 1

    # assembling lines of code/comments tuple
    loc_com = (loc, com)

    # returning lines of code/comments tuple
    return loc_com


def get_loc_com_str(loc: int,
                    com: int
                    ) -> str:
    """
    Given a file/folder lines of code and
    comments counts, returns its formatted
    string.
    """
    # getting lines total
    lines_total = (loc + com)

    # calculating loc ratio
    try:
        loc_ratio = (loc / lines_total)
    except ZeroDivisionError:
        loc_ratio = 0.0

    # calculating com ratio
    try:
        com_ratio = (com / lines_total)
    except ZeroDivisionError:
        com_ratio = 0.0

    # calculating percentages
    loc_percent = (loc_ratio * 100)
    com_percent = (com_ratio * 100)

    # rounding percentages
    loc_percent = round(loc_percent)
    com_percent = round(com_percent)

    # assembling loc string
    loc_com_str = f'{loc} lines of code ({loc_percent}%), {com} comments ({com_percent}%)'

    # returning loc/com string
    return loc_com_str

######################################################################
# end of current module
