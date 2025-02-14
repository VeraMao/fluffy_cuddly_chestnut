'''
Course search engine: search

Vera Mao, Yixin Ding
'''

from math import radians, cos, sin, asin, sqrt, ceil
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course_information.sqlite3')

conn = sqlite3.connect(DATABASE_FILENAME)
cur = conn.cursor()

def list_of_variable(table):
    """
    Retrieve a list of column names for a given database table.
    """
    query = f"PRAGMA table_info({table})"
    return [row[1] for row in cur.execute(query).fetchall()]

def find_common_variable(table1, table2):
    """
    Finds the common variable between two tables.
    """
    columns_table1 = set(list_of_variable(table1))
    columns_table2 = set(list_of_variable(table2))
    common_columns = columns_table1.intersection(columns_table2)
    return common_columns.pop() if len(common_columns) == 1 else None

def find_courses(args_from_ui):
    """
    Finds courses matching the specified search criteria.
    """
    if not args_from_ui:
        return ([], [])
    
    column_map = {
        "terms": "catalog_index.word",
        "dept": "courses.dept",
        "course_num": "courses.course_num",
        "title": "courses.title",
        "section_num": "sections.section_num",
        "day": "meeting_patterns.day",
        "time_start": "meeting_patterns.time_start",
        "time_end": "meeting_patterns.time_end",
        "enrollment": "sections.enrollment",
        "building_code": "b.building_code",
        "walking_time": "walking_time"
    }
    
    base_columns = ["dept", "course_num", "title"]
    section_columns = ["section_num", "day", "time_start", "time_end", "enrollment"]
    location_columns = ["building_code", "walking_time"]
    selected_columns = base_columns[:]
    
    joins = ["courses"]
    if "building_code" in args_from_ui:
        selected_columns.extend(section_columns + location_columns)
        joins.extend(["sections", "meeting_patterns"])
    elif any(k in args_from_ui for k in ["day", "enrollment", "time_start", "time_end"]):
        selected_columns.extend(section_columns)
        joins.extend(["sections", "meeting_patterns"])
    
    selected_columns = [column_map[col] for col in selected_columns]
    conditions = []
    join_conditions = []
    
    for i in range(len(joins) - 1):
        common_col = find_common_variable(joins[i], joins[i + 1])
        if common_col:
            join_conditions.append(f"{joins[i]}.{common_col} = {joins[i + 1]}.{common_col}")
    
    if "terms" in args_from_ui:
        joins.append("catalog_index")
        join_conditions.append("courses.course_id = catalog_index.course_id")
    
    if "building_code" in args_from_ui:
        conn.create_function("time_between", 4, compute_time_between)
        joins.append("gps AS a JOIN (SELECT lon, lat, building_code FROM gps) AS b")
        join_conditions.append("sections.building_code = a.building_code")
        selected_columns[-2] = "a.building_code"
        selected_columns[-1] = "time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time"
    
    filter_conditions = []
    filter_values = []
    where_clauses = {
        "terms": f"IN ({', '.join(['?'] * len(args_from_ui['terms']))})" if "terms" in args_from_ui else "",
        "dept": "= ?",
        "day": f"IN ({', '.join(['?'] * len(args_from_ui['day']))})" if "day" in args_from_ui else "",
        "enrollment": "BETWEEN ? AND ?",
        "time_start": ">= ?",
        "time_end": "<= ?",
        "building_code": "= ?",
        "walking_time": "<= ?"
    }
    
    for key in args_from_ui:
        filter_conditions.append(f"{column_map[key]} {where_clauses[key]}")
        filter_values.extend(args_from_ui[key] if isinstance(args_from_ui[key], (list, tuple)) else [args_from_ui[key]])
    
    group_clause = None
    if "terms" in args_from_ui:
        group_clause = f"GROUP BY catalog_index.course_id HAVING COUNT(DISTINCT word) = {len(args_from_ui['terms'])}"
        if "sections" in joins:
            group_clause = f"GROUP BY catalog_index.course_id, sections.section_num HAVING COUNT(DISTINCT word) = {len(args_from_ui['terms'])}"
    
    query = " ".join(filter(None, [
        f"SELECT {', '.join(selected_columns)}",
        f"FROM {' JOIN '.join(joins)}",
        f"ON {' AND '.join(join_conditions)}" if join_conditions else None,
        "WHERE " + " AND ".join(filter_conditions) if filter_conditions else None,
        group_clause
    ]))
    
    results = cur.execute(query, filter_values).fetchall()
    return (get_header(cur), results)



########### auxiliary functions #################
########### do not change this code #############

def assert_valid_input(args_from_ui):
    '''
    Verify that the input conforms to the standards set in the
    assignment.
    '''

    assert isinstance(args_from_ui, dict)

    acceptable_keys = set(['time_start', 'time_end', 'enrollment', 'dept',
                           'terms', 'day', 'building_code', 'walking_time'])
    assert set(args_from_ui.keys()).issubset(acceptable_keys)

    # get both buiding_code and walking_time or neither
    has_building = ("building_code" in args_from_ui and
                    "walking_time" in args_from_ui)
    does_not_have_building = ("building_code" not in args_from_ui and
                              "walking_time" not in args_from_ui)

    assert has_building or does_not_have_building

    assert isinstance(args_from_ui.get("building_code", ""), str)
    assert isinstance(args_from_ui.get("walking_time", 0), int)

    # day is a list of strings, if it exists
    assert isinstance(args_from_ui.get("day", []), (list, tuple))
    assert all([isinstance(s, str) for s in args_from_ui.get("day", [])])

    assert isinstance(args_from_ui.get("dept", ""), str)

    # terms is a non-empty list of strings, if it exists
    terms = args_from_ui.get("terms", [""])
    assert terms
    assert isinstance(terms, (list, tuple))
    assert all([isinstance(s, str) for s in terms])

    assert isinstance(args_from_ui.get("time_start", 0), int)
    assert args_from_ui.get("time_start", 0) >= 0

    assert isinstance(args_from_ui.get("time_end", 0), int)
    assert args_from_ui.get("time_end", 0) < 2400

    # enrollment is a pair of integers, if it exists
    enrollment_val = args_from_ui.get("enrollment", [0, 0])
    assert isinstance(enrollment_val, (list, tuple))
    assert len(enrollment_val) == 2
    assert all([isinstance(i, int) for i in enrollment_val])
    assert enrollment_val[0] <= enrollment_val[1]


def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return int(ceil(mins))


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    header = []

    for i in cursor.description:
        s = i[0]
        if "." in s:
            s = s[s.find(".")+1:]
        header.append(s)

    return header
