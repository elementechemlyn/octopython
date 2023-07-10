import unittest
import octopys.utils as utils
from datetime import datetime
from datetime import timezone

class TestUtils(unittest.TestCase):

    def test_from_iso(self):
        dt = datetime(year=2010,month=10,day=8,hour=1,minute=2,second=0,tzinfo=timezone.utc)
        dt_str = utils.to_iso(dt)
        self.assertEqual(dt_str,'2010-10-08T01:02Z')

    def test_to_iso(self):
        dt_str = '2010-10-08T01:02Z'
        t = utils.from_iso(dt_str)
        dt = datetime(year=2010,month=10,day=8,hour=1,minute=2,second=0,tzinfo=timezone.utc)
        self.assertEqual(t.year,dt.year)
        self.assertEqual(t.month,dt.month)
        self.assertEqual(t.day,dt.day)
        self.assertEqual(t.hour,dt.hour)
        self.assertEqual(t.minute,dt.minute)
        self.assertEqual(t.second,dt.second)
        self.assertEqual(t.tzinfo,dt.tzinfo)
