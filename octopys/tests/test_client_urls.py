import unittest
from octopys.client import OctopusClient
import octopys.utils as utils
from unittest import mock
import requests

from datetime import datetime

def _mock_api_call(self,url:str, params:list=None):
    retry_count = 0
    if params:
        url = '%s%s' % (url,self._build_param_string(params))
    return url

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
    return args[0],kwargs.get('params')

class TestClientUrls(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_products(self,mock_get):
        client = OctopusClient('foo_key')
        url,params = client.get_products()
        self.assertEqual(url, 'https://api.octopus.energy/v1/products/')
        self.assertIsNone(params)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_product(self,mock_get):
        now = datetime.now()
        now_str = utils.to_iso(now)
        client = OctopusClient('foo_key')
        url,params = client.get_product('pcode')
        self.assertEqual(url, 'https://api.octopus.energy/v1/products/pcode/')
        self.assertIsNone(params)
        url,params = client.get_product('pcode',now)
        self.assertEqual(url, 'https://api.octopus.energy/v1/products/pcode/')
        self.assertDictEqual(params,{'tariffs_active_at': now_str})


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_list_tariff_charges(self,mock_get):
        now = datetime.now()
        now_str = utils.to_iso(now)
        client = OctopusClient('foo_key')
        url,params = client.list_tariff_charges('pcode','tcode')
        self.assertEqual(url, 'https://api.octopus.energy/v1/products/pcode/electricity-tariffs/tcode/standard-unit-rates/')
        url,params = client.list_tariff_charges('pcode','tcode',period_from=now)
        self.assertEqual(url, 'https://api.octopus.energy/v1/products/pcode/electricity-tariffs/tcode/standard-unit-rates/')
        self.assertDictEqual(params,{'period_from': now_str})
        url,params = client.list_tariff_charges('pcode','tcode',period_to=now)
        self.assertEqual(url, 'https://api.octopus.energy/v1/products/pcode/electricity-tariffs/tcode/standard-unit-rates/')
        self.assertDictEqual(params,{'period_to': now_str})
        url,params = client.list_tariff_charges('pcode','tcode',page_size=20)
        self.assertEqual(url, 'https://api.octopus.energy/v1/products/pcode/electricity-tariffs/tcode/standard-unit-rates/')
        self.assertDictEqual(params,{'page_size': 20})

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_meter_point(self,mock_get):
        client = OctopusClient('foo_key')
        url,params = client.get_meter_point('foo')
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/foo/')
        self.assertIsNone(params)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_consumption(self,mock_get):
        client = OctopusClient('foo_key')
        now = datetime.now()
        now_str = utils.to_iso(now)
        url,params = client.get_consumption('mpan','serial')
        self.assertIsNone(params)
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        url,params = client.get_consumption('mpan','serial',period_from=now)
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'period_from': now_str})
        url,params = client.get_consumption('mpan','serial',period_to=now)
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'period_to': now_str})
        url,params = client.get_consumption('mpan','serial',page_size=20)
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'page_size': 20})
        url,params = client.get_consumption('mpan','serial',order_by='period')
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'order_by': 'period'})
        url,params = client.get_consumption('mpan','serial',order_by='-period')
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'order_by': '-period'})
        url,params = client.get_consumption('mpan','serial',group_by='hour')
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'group_by': 'hour'})
        url,params = client.get_consumption('mpan','serial',group_by='day')
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'group_by': 'day'})
        url,params = client.get_consumption('mpan','serial',group_by='week')
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'group_by': 'week'})
        url,params = client.get_consumption('mpan','serial',group_by='month')
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'group_by': 'month'})
        url,params = client.get_consumption('mpan','serial',group_by='quarter')
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/mpan/meters/serial/consumption/')
        self.assertDictEqual(params,{'group_by': 'quarter'})
        self.assertRaises(ValueError,client.get_consumption,'mpan','serial',order_by='foobar')
        self.assertRaises(ValueError,client.get_consumption,'mpan','serial',group_by='foobar')

if __name__ == '__main__':
    unittest.main()
