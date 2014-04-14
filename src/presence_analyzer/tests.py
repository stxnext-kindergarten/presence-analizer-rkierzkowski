# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_USERS_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_users.xml'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'USERS_XML': TEST_USERS_XML})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 3)
        user = {
            u'user_id': 2,
            u'name': u'User 2',
            u'avatar': u'http://example.com:80/api/2'
        }
        self.assertDictEqual(data[0], user)

    def test_mean_time_weeday(self):
        """
        Test mean time per day.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        all_days = [u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat', u'Sun']
        self.assertEqual(all_days, [record[0] for record in data])

    def test_presence_weekday(self):
        """
        Test summary - seconds worked per day.
        """
        resp = self.client.get('/api/v1/presence_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        all_days = [u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat', u'Sun']
        self.assertEqual(all_days, [record[0] for record in data[1:]])

    def test_mean_start_end_time(self):
        """
        Test average start and end of a day.
        """
        resp = self.client.get('/api/v1/mean_start_end_time/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        all_days = [u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat', u'Sun']
        self.assertEqual(all_days, [record[0] for record in data])
        starts = [record[1] for record in data]
        ends = [record[2] for record in data]
        for start, end in zip(starts, ends):
            self.assertLessEqual(start, end)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_mean(self):
        data = [1, 2, 3]
        mean = utils.mean(data)
        self.assertAlmostEqual(mean, 2.0)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
