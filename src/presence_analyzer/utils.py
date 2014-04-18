# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
from json import dumps
from functools import wraps
from datetime import datetime

from flask import Response

from presence_analyzer.main import app
from collections import defaultdict
from cache import cache

import requests

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103

from lxml import etree


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


def download_file(url, destination):
    r = requests.get(url, stream=True)
    with open(destination, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()


def get_users():
    """
    Extracts user data from XML file.
    """
    result = []
    with open(app.config['USERS_XML'], 'r') as xmlfile:
        tree = etree.parse(xmlfile)
        for node in tree.getroot():
            if node.tag == 'users':
                users = node
            elif node.tag == 'server':
                server = node

        s = {}
        for record in server:
            s[record.tag] = record.text

        address = s['protocol'] + "://" + s['host'] + ":" + s['port']

        for record in users:
            user = {}
            user['user_id'] = record.get('id')
            for field in record:
                user[field.tag] = field.text
            if 'avatar' in user:
                user['avatar'] = address + user['avatar']
            user['user_id'] = int(user['user_id'])
            result.append(user)

    return result

@cache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def mean_start_and_end(items):
    """
    Groups starts and ends by weekday.
    """
    result = {i: defaultdict(lambda: []) for i in range(7)}
    for date in items:
        day = result[date.weekday()]
        day['start'].append(seconds_since_midnight(items[date]['start']))
        day['end'].append(seconds_since_midnight(items[date]['end']))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
