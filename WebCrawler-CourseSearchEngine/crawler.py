"""
PA1: Course Search Engine Part 1
Yixin Ding, Jiaming (Vera) Mao
"""
# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg=invalid-name, redefined-outer-name, unused-argument, unused-variable

import queue
import json
import sys
import csv
import re
from bs4 import BeautifulSoup
import util
from collections import deque

INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 's', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet']) 


def extract_words(text):
    '''
    Extract valid words from the given text.
    
    Inputs:
        text: A string containing the text.
    
    Returns:
        List of valid words (lowercase, without stop words).
    '''
    # First convert text to lowercase
    text = text.lower()
    
    # Use regex to find words (letters followed by letters, numbers, or underscores)
    words = re.findall(r'\b([a-zA-Z][\w\-]*)\b', text)
    
    # Filter out stop words and ensure unique words
    valid_words = []
    for word in words:
        if word not in INDEX_IGNORE and word not in valid_words:
            valid_words.append(word)
    
    return valid_words

def extract_course_code(text):
    '''
    Extract the course code (e.g., CMSC 12200) from a title string and standardize format.
    
    Inputs:
        text: A string containing the course title.
    
    Returns:
        The course code as a string, or None if not found.
    '''
    match = re.search(r'([A-Z]{4})\s*(\d{5})', text)
    if match:
        # Standardize format to have exactly one space between dept and number
        return f"{match.group(1)} {match.group(2)}"
    return None

def write_to_csv(index, filename):
    '''
    Write the index to a CSV file.
    '''
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        for word, course_ids in index.items():
            # Convert set to sorted list for consistent output
            for course_id in sorted(course_ids):
                writer.writerow([course_id, word])

def process_course_page(soup, course_map, index):
    '''
    Extract course data from a page and update the index.
    '''
    for course_block in soup.find_all('div', class_="courseblock main"):
        title_tag = course_block.find('p', class_="courseblocktitle")
        desc_tag = course_block.find('p', class_="courseblockdesc")
        
        if title_tag:
            title = title_tag.text.strip()
        else:
            continue
            
        if desc_tag:
            description = desc_tag.text.strip()
        else:
            description = ""

        # Process any sequence courses first
        subsequences = util.find_sequence(course_block)
        if subsequences:
            # Get the main sequence description which applies to all courses in sequence
            sequence_desc = description

            for subsequence in subsequences:
                sub_title = subsequence.find('p', class_="courseblocktitle").text.strip()
                sub_desc = subsequence.find('p', class_="courseblockdesc")
                
                # Combine sequence description with individual description if it exists
                if sub_desc:
                    full_desc = sequence_desc + " " + sub_desc.text.strip()
                else:
                    full_desc = sequence_desc
                
                sub_course_code = extract_course_code(sub_title)
                if sub_course_code and sub_course_code in course_map:
                    sub_course_id = course_map[sub_course_code]
                    sub_words = extract_words(sub_title + " " + full_desc)
                    for word in sub_words:
                        if word not in index:
                            index[word] = set()
                        index[word].add(sub_course_id)

        # Get the primary course code
        course_code = extract_course_code(title)
        if course_code and course_code in course_map:
            course_id = course_map[course_code]
            # Extract words from title and description
            words = extract_words(title + " " + description)
            # Add words to index
            for word in words:
                if word not in index:
                    index[word] = set()
                index[word].add(course_id)
        
        # Process cross-listed courses if present
        cross_listed = title.split('/')
        if len(cross_listed) > 1:
            for cross_code in cross_listed[1:]:
                course_code = extract_course_code(cross_code)
                if course_code and course_code in course_map:
                    course_id = course_map[course_code]
                    words = extract_words(title + " " + description)
                    for word in words:
                        if word not in index:
                            index[word] = set()
                        index[word].add(course_id)

def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index.
    '''
    starting_url = "http://www.classes.cs.uchicago.edu/archive/2015/winter/12200-1/new.collegecatalog.uchicago.edu/index.html"
    limiting_domain = "classes.cs.uchicago.edu"

    # Read course map
    with open(course_map_filename, 'r') as f:
        course_map = json.load(f)

    # Initialize crawling data structures
    urls_to_visit = deque([starting_url])
    already_visited = set()
    index = {}  # word -> set of course identifiers
    
    pages_processed = 0
    total_courses_found = 0
    matched_courses = 0

    while urls_to_visit and pages_processed < num_pages_to_crawl:
        current_url = urls_to_visit.popleft()
        
        # Skip if already visited
        if current_url in already_visited:
            continue
        
        # Get and parse the page
        request = util.get_request(current_url)
        if not request:
            continue
            
        html = util.read_request(request)
        soup = BeautifulSoup(html, "html5lib")

        # Count courses before processing
        courses_before = sum(len(ids) for ids in index.values() if isinstance(ids, set))
        
        # Process the page
        process_course_page(soup, course_map, index)
        
        # Count courses after processing
        courses_after = sum(len(ids) for ids in index.values() if isinstance(ids, set))
        new_courses = courses_after - courses_before
        total_courses_found += len(soup.find_all('div', class_="courseblock main"))
        matched_courses += new_courses

        # Queue additional URLs
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = util.convert_if_relative_url(current_url, href)
            if full_url and util.is_url_ok_to_follow(full_url, limiting_domain):
                if full_url not in already_visited and full_url not in urls_to_visit:
                    urls_to_visit.append(full_url)

        # Mark page as visited and update counter
        already_visited.add(current_url)
        pages_processed += 1
    
    # Write the final index to CSV
    write_to_csv(index, index_filename)

if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    go(num_pages_to_crawl, course_map_filename, index_filename)
