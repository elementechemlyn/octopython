"""Module of tests for utils module"""
from datetime import datetime, timezone
import unittest
import octopys.utils as utils

class TestUtils(unittest.TestCase):
    """Class to test utils module functions
    """

    def test_from_iso(self):
        """Test of util function to convert iso string to datetime 
        """
        test_dt = datetime(year=2010,month=10,day=8,hour=1,minute=2,second=0,tzinfo=timezone.utc)
        dt_str = utils.to_iso(test_dt)
        self.assertEqual(dt_str,'2010-10-08T01:02Z')

    def test_to_iso(self):
        """Test of util function to convert datetime to iso string 
        """
        dt_str = '2010-10-08T01:02Z'
        from_t = utils.from_iso(dt_str)
        test_dt = datetime(year=2010,month=10,day=8,hour=1,minute=2,second=0,tzinfo=timezone.utc)
        self.assertEqual(from_t.year,test_dt.year)
        self.assertEqual(from_t.month,test_dt.month)
        self.assertEqual(from_t.day,test_dt.day)
        self.assertEqual(from_t.hour,test_dt.hour)
        self.assertEqual(from_t.minute,test_dt.minute)
        self.assertEqual(from_t.second,test_dt.second)
        self.assertEqual(from_t.tzinfo,test_dt.tzinfo)
