'''
Tests for finding courses
'''

import json
import os
import pytest


# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable= broad-except, redefined-outer-name

from courses import find_courses

TEST_DIR = os.path.dirname(__file__)
TEST_FILENAME = os.path.join(TEST_DIR, 'find_courses_tests.json')
TESTS = json.load(open(TEST_FILENAME))

def check_type(actual, err_msg, inputs):
    '''
    Check the type of the actual value.  It should
    be a pair, where the first value is a list of strings
    and the second is a list of lists.
    '''

    if not isinstance(actual, (list, tuple)):
        err_msg += "  Expected list/tuple of length 2.  Got {}"
        pytest.fail(err_msg.format(inputs, type(actual)))

    if len(actual) != 2:
        err_msg += "  Expected list/tuple of length 2. Got value of length {}"
        pytest.fail(err_msg.format(err_msg.format(inputs, len(actual))))

    if not (isinstance(actual[0], (list, tuple)) and
            isinstance(actual[1], (list, tuple))):
        err_msg += "  Expected pair of list/tuples. Got ({}, {})."
        pytest.fail(err_msg.format(inputs, type(actual[0]), type(actual[1])))


    val_types = [isinstance(x, str) for x in actual[0]]
    if not all(val_types):
        err_msg += "  All values in the header must be strings."
        pytest.fail(err_msg.format(inputs))

    val_types = [isinstance(x, (list, tuple)) for x in actual[1]]
    if not all(val_types):
        err_msg += ("  All values in the list of results from the"
                    " query must be tuples or lists.")
        pytest.fail(err_msg.format(inputs))


def check_header(expected, actual, err_msg, inputs):
    '''
    Check the expected header against the actual header.
    '''

    expected_header = [str(x.strip()) for x in expected[0]]
    actual_header = [str(x.strip()) for x in actual[0]]

    if expected_header != actual_header:
        s = err_msg
        s = s + "\n  Actual and expected headers do not match"
        s = s + "\n    actual: {}"
        s = s + "\n    expected: {}"
        s = s.format(inputs, str(actual_header), str(expected_header))

        pytest.fail(s)


def compare_rows(left, right, err_msg, inputs):
    '''
    Compare two sets of rows and identify differences.

    Inputs:
      left (set of tuples): one set of rows
      right (set of tuples): another set of rows
      err_msg (string): error to generate
      n (int): number of tuples to include in error message
    '''

    diff = list(set(left).difference(set(right)))
    if diff:
        row_strs = [", ".join([str(y) for y in x]) for x in diff]
        pytest.fail(err_msg.format(inputs, "    " + "\n    ".join(row_strs)))


def check_rows(expected, actual, err_msg, inputs):
    '''
    Check to see if the tables match:

    Inputs:
        expected: the expected list of tuples
        actual: the actual list of tuples
    '''

    expected_table = set([tuple(x) for x in expected[1]])
    actual_table = set([tuple(x) for x in actual[1]])

    if expected_table == actual_table:
        return

    # Find any rows that are missing from the actual table
    compare_rows(expected_table,
                 actual_table,
                 err_msg + "  Missing expected rows: \n{}",
                 inputs)

    # Find any rows that are extra rows that appear in the
    # actual table
    compare_rows(actual_table,
                 expected_table,
                 err_msg + "  Found unexpected rows: \n{}",
                 inputs)

@pytest.mark.parametrize("t", TESTS)
def test_n(t):
    '''
    Do the Nth test.
    '''

    err_msg = "Test #{}\n".format(t["test_num"])
    err_msg += "Input: {}\n"

    try:
        actual = find_courses(t["input"])
    except Exception as e:
        err_msg += "Hit exception: {}".format(e)
        pytest.fail(err_msg)

    expected = t["expected"]

    check_type(actual, err_msg, t["input"])
    check_header(expected, actual, err_msg, t["input"])
    check_rows(expected, actual, err_msg, t["input"])
