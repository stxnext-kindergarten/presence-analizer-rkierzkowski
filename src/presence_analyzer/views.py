# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, render_template

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    get_users,
    mean,
    group_by_weekday,
    mean_start_and_end,
)

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/presence_weekday')


@app.route('/presence_weekday')
def presence_weekday_page():
    """
    Renders to presence weekday page.
    """
    return render_template('presence_weekday.jinja2')


@app.route('/mean_time_weekday')
def mean_time_weekday_page():
    """
    Renders mean time weekday page.
    """
    return render_template('mean_time_weekday.jinja2')


@app.route('/mean_start_end_time')
def mean_start_end_page():
    """
    Renders mean start and end page.
    """
    return render_template('presence_start_end.jinja2')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    return get_users()


@app.route('/api/v1/mean_time_weekday/', methods=['GET'])
@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id=0):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/', methods=['GET'])
@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id=0):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/mean_start_end_time/', methods=['GET'])
@app.route('/api/v1/mean_start_end_time/<int:user_id>', methods=['GET'])
@jsonify
def mean_start_end_time_view(user_id=0):
    """
    Returns mean start & end time of of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = mean_start_and_end(data[user_id])
    result = [(calendar.day_abbr[weekday],
               mean(data['start']),
               mean(data['end']))
              for weekday, data in weekdays.items()]

    return result
