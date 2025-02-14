'''
PA1: Test code for the Mini Crawler/Indexer.
'''
# pylint: skip-file

import csv
import json
import sys
import crawler 
import pytest 

TEST_DATA = [(7, 'academically', 'Basic course: word from description', True),
             (7, 'british', 'Basic course: capitalized word from description', True),
             (7, 'British', 'Basic course: capitalized word from description', False),
             (7, 'classical', 'Basic course: word from title ', True),
             (7, 'Classical', 'Basic course: capialized word from title ', False),
             (7, "with", "Basic course: word from ignore list", False),
             (7, "terms", "Basic course: word from course details", False),
             (40, 'introduction', 'Sequence word from sequence title', True),
             (40, 'history', 'Sequence word from sequence description ', True),
             (40, 'portuguese', 'Sequence word from subsequence course descripton', True),
             (40, "evolution", 'Sequence word from the course description of another subsequence in the sequence', False),
             (40, "twentieth", 'Sequence word from the course description of another subsequence in the sequence', False),
             (40, "I", 'Word from ignore list in subsequence title', False),
             (41, 'introduction', 'Sequence word from sequence title', True),
             (41, 'history', 'Sequence word from sequence description ', True),
             (41, 'evolution', 'Sequence word from subsequence course descripton', True),
             (41, "twentieth", 'Sequence word from the course descripton of another subsequence in the sequence', False),
             (41, "portuguese", 'Sequence word from the course descripton of another subsequence in the sequence', False),
             (42, 'introduction', 'Sequence word from sequence title', True),
             (42, 'history', 'Sequence word from sequence description ', True),
             (42, 'twentieth', 'Sequence word from subsequence course descripton', True),
             (42, "evolution", 'Sequence word from the course descripton of another subsequence in the sequence', False),
             (42, "portuguese", 'Sequence word from the course descripton another subsequence in the sequence', False),
             (106, 'essay', 'Basic course: last one on anthro page.  Title only.', True),
             (2616, 'language', 'Basic course: word from title of first course on Visual Arts page', True),
             (2616, 'conventions', 'Basic course: word from description of first course in Visual arts page', True),
             (2616, 'basic', 'First word in a sentence', True),
             (2616, 'Basic', 'First word in a sentence.  Should be in lowercase.', False),
             (2622, "drawing", 'First word in description', True),
             (2657, "honors", "Last course on the Visual Arts page", True),
             (0, "anth", "Course code from title should be a word", True),
             (91, "language", "Word that appears in more than one course", True),
             (92, "language", "Word that appears in more than one course, but not this one", False)
            ]

DATA_DIR = "./data/"


def load_and_invert(filename):
    rv = {}
    with open(filename) as f:
        cn_to_ci = json.load(f)
        for cn, ci in cn_to_ci.items():
            rv[ci] = cn
    return rv

def load_csv(filename, ci_to_cn, points_available, delimiter="|"):

    d = {}
    for row in csv.reader(open(filename), delimiter=delimiter):
        if len(row) != 2:
            continue
        try:
            ci = int(row[0])
        except:
            continue

        if ci not in d:
            d[ci] = []

        d[ci].append(row[1])

    rv = {}
    failed_intersection = False
    dups_found = False
    failed_str = "" 
    for ci, words in d.items():
        if (not dups_found) and (len(words) != len(set(words))):
            failed_str = ("{:} includes duplicates for at least one course: {:} {:}\n"
                          "    expected:{:}"
                          "    found:{:}")
            pytest.fail(failed_str.format(filename,ci, ci_to_cn.get(ci, "UNKNOWN"), len(set(words)),len(words)))
            dups_found = True

        if (not failed_intersection) and (set(words).intersection(crawler.INDEX_IGNORE) != set([])):
            failed_str = "{:} includes words that should have been ignored in at least one course:: {:} {:}\n"
            pytest.fail(failed_str.format(filename,ci, ci_to_cn.get(ci, "UNKNOWN")))
            failed_intersection = True

        rv[ci] = set(words)

    return rv

def run_tests(ci, word, reason, expected, ci_to_cn, actual_index):

    failed_message = "" 
    failed = False 
    if ci not in actual_index:
        failed_message = "TEST FAILED: Course missing"
        failed = True 
    elif word not in actual_index[ci] and expected:
        failed_message = "TEST FAILED: word missing"
        failed = True 
    elif word in actual_index[ci] and not expected:
        failed_message = "TEST FAILED: word found when not expected"
        failed = True 

    if failed:
        pytest.fail("{}: {} ({}): {}\n  {}\n  {}".format(
                failed_message, 
                ci_to_cn.get(ci, "UNKNOWN"),
                ci, 
                word, 
                reason, 
                "Should appear" if expected else "Should not appear"))


ci_to_cn = load_and_invert("course_map.json")
num_pages_to_crawl = 100

def test_crawler_csv_1(): 
     ''' 
        TEST: Checking whether crawler stops after 1 page...
     ''' 
     crawler.go(1, "course_map.json", "catalog-index-empty.csv")
     load_csv("catalog-index-empty.csv", ci_to_cn, 0)

def test_crawler_csv_2(): 
    ''' 
        TEST: Loading crawler result and testing contents.
    ''' 
    crawler.go(num_pages_to_crawl, "course_map.json", "catalog-index.csv")
    d = load_csv("catalog-index.csv", ci_to_cn, 3)

@pytest.fixture(scope="module")
def gen_dict():
    crawler.go(num_pages_to_crawl, "course_map.json", "catalog-index-actual.csv")
    return load_csv("catalog-index-actual.csv", ci_to_cn, 3)

@pytest.mark.parametrize("ci, word, reason, expected", TEST_DATA)
def test_crawler_results(ci, word, reason, expected, gen_dict):
    ''' 
        Test harness. This test checks words from the dictionary generated by
        the previous test_crawler_csv_2 test.
    '''
    run_tests(ci, word, reason, expected, ci_to_cn, gen_dict)
