# test_loc module

# Code destined to testing shared/loc.py's
# lines-of-code/comment counting functions.

######################################################################
# imports

# importing required libraries
from pathlib import Path
from pytree.shared.loc import get_loc
from pytree.shared.loc import get_loc_com_str
from pytree.shared.loc import collapse_brackets

######################################################################
# defining collapse_brackets test cases


def test_collapse_brackets_triple_double_quote_docstring() -> None:
    """
    Asserts collapse_brackets collapses a multi-line
    triple-double-quote docstring onto a single line.
    """
    # defining text with a multi-line docstring
    text = '"""\nline1\nline2\n"""\nx = 1'

    # collapsing text
    collapsed = collapse_brackets(text=text)

    # asserting the docstring's internal newlines were collapsed away
    assert '\nline1\n' not in collapsed
    assert collapsed.count('\n') == 1


def test_collapse_brackets_triple_single_quote_docstring_not_handled() -> None:
    """
    Documents the known gap: collapse_brackets does not
    handle '''-triple-single-quote docstrings, only \"\"\",
    so a multi-line ''' docstring is left untouched.
    """
    # defining text with a multi-line '''-docstring
    text = "'''\nline1\nline2\n'''\nx = 1"

    # collapsing text
    collapsed = collapse_brackets(text=text)

    # asserting the triple-single-quote docstring was left as-is (not collapsed)
    assert collapsed == text


def test_collapse_brackets_nested_same_type_confuses_regex() -> None:
    """
    Documents that nested same-type brackets confuse
    collapse_brackets's non-greedy regex, matching only
    up to the FIRST closing bracket and leaving a stray
    closing bracket behind.
    """
    # defining text with nested parentheses
    text = '(a(b)c)'

    # collapsing text
    collapsed = collapse_brackets(text=text)

    # asserting only the inner pair was consumed by the non-greedy match,
    # leaving the outer closing paren stray
    assert collapsed == '()c)'


def test_collapse_brackets_multi_line_span_collapses_to_one_line() -> None:
    """
    Asserts a multi-line bracket span (parentheses spanning
    several physical lines) collapses to a single logical line.
    """
    # defining text with a multi-line function call
    text = 'func(\n    arg1,\n    arg2,\n)'

    # collapsing text
    collapsed = collapse_brackets(text=text)

    # asserting the parenthesized span was collapsed to a single line
    assert collapsed == 'func()'

######################################################################
# defining get_loc test cases


def test_get_loc_blank_only(tmp_path: Path) -> None:
    """
    Asserts get_loc returns (0, 0) for a blank-only file.
    """
    # writing a blank-only file
    file_path = tmp_path / 'blank.py'
    file_path.write_text('\n\n   \n')

    # getting loc/com tuple
    loc_com = get_loc(file_path=str(file_path))

    # asserting both counts are zero
    assert loc_com == (0, 0)


def test_get_loc_pure_comment(tmp_path: Path) -> None:
    """
    Asserts get_loc counts a pure-comment file entirely
    as comments, with zero lines of code.
    """
    # writing a pure-comment file
    file_path = tmp_path / 'comments.py'
    file_path.write_text('# comment one\n# comment two\n')

    # getting loc/com tuple
    loc_com = get_loc(file_path=str(file_path))

    # asserting all lines were counted as comments
    assert loc_com == (0, 2)


def test_get_loc_pure_code(tmp_path: Path) -> None:
    """
    Asserts get_loc counts a pure-code file entirely
    as lines of code, with zero comments.
    """
    # writing a pure-code file
    file_path = tmp_path / 'code.py'
    file_path.write_text('x = 1\ny = 2\n')

    # getting loc/com tuple
    loc_com = get_loc(file_path=str(file_path))

    # asserting all lines were counted as code
    assert loc_com == (2, 0)


def test_get_loc_code_line_with_trailing_comment_counts_as_both(tmp_path: Path) -> None:
    """
    Asserts a code line with a trailing inline '#' comment
    counts as BOTH a line of code and a comment (no continue
    after the inline-comment branch in get_loc).
    """
    # writing a file with a code line carrying an inline comment
    file_path = tmp_path / 'inline.py'
    file_path.write_text('z = 3  # inline comment\n')

    # getting loc/com tuple
    loc_com = get_loc(file_path=str(file_path))

    # asserting the line was double-counted as both code and comment
    assert loc_com == (1, 1)


def test_get_loc_multi_line_docstring_counts_once(tmp_path: Path) -> None:
    """
    Asserts a multi-line docstring, once collapsed by
    collapse_brackets, counts once as a comment rather
    than once per physical line.
    """
    # writing a file with a multi-line docstring followed by one code line
    file_path = tmp_path / 'docstring.py'
    file_path.write_text('"""\nfirst line\nsecond line\n"""\nx = 1\n')

    # getting loc/com tuple
    loc_com = get_loc(file_path=str(file_path))

    # asserting the docstring counted once as a comment, plus one code line
    assert loc_com == (1, 1)

######################################################################
# defining get_loc_com_str test cases


def test_get_loc_com_str_zero_division_guard() -> None:
    """
    Asserts get_loc_com_str does not raise ZeroDivisionError
    when both loc and com are zero, falling back to 0% each.
    """
    # getting loc/com string for the zero/zero case
    loc_com_str = get_loc_com_str(loc=0,
                                  com=0)

    # asserting the fallback string was produced without raising
    assert loc_com_str == '0 lines of code (0%), 0 comments (0%)'


def test_get_loc_com_str_normal_case_matches_readme() -> None:
    """
    Asserts get_loc_com_str's normal-case output matches
    the exact numbers documented in README.md's CLI example.
    """
    # getting loc/com string for the README's documented case
    loc_com_str = get_loc_com_str(loc=6,
                                  com=10)

    # asserting string matches README's "6 lines of code (38%), 10 comments (62%)"
    assert loc_com_str == '6 lines of code (38%), 10 comments (62%)'

######################################################################
# end of current module
