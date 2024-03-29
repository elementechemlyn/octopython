"""Tests for the OctopusBasicClient"""
import unittest
from unittest import mock
import os
from datetime import datetime
import requests
from octopys.client import OctopusBasicClient
import octopys.utils as utils

def mocked_requests_get(*args, **kwargs):
    """Mock for the requests.get function. 
    Returns:
      The url that would be called
    """
    return args[0],kwargs.get('params')

def mocked_requests_error(*args, **kwargs):
    """Mock for the requests.get function. 
    Raises:
      requests.HTTPError
    """
    raise requests.HTTPError

class TestBasicClient(unittest.TestCase):

    def test_create_client(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertRaises(ValueError,OctopusBasicClient)
        with mock.patch.dict(os.environ, {'OCTOPYS_API_KEY':'api_key'}, clear=True):
            client = OctopusBasicClient()
        client = OctopusBasicClient('foo_key')

    @mock.patch('requests.get', side_effect=mocked_requests_error)
    def test_retries(self,mock_get):
        client = OctopusBasicClient('foo_key',retry_count=2,retry_wait=1)
        self.assertRaises(requests.HTTPError,client.get_products)
        self.assertEqual(mock_get.call_count,2)
        client = OctopusBasicClient('foo_key',retry_count=3,retry_wait=1)
        self.assertRaises(requests.HTTPError,client.get_products)
        self.assertEqual(mock_get.call_count,5)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_products(self,mock_get):
        client = OctopusBasicClient('foo_key')
        url,params = client.get_products()
        self.assertEqual(url, 'https://api.octopus.energy/v1/products/')
        self.assertIsNone(params)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_product(self,mock_get):
        now = datetime.now()
        now_str = utils.to_iso(now)
        client = OctopusBasicClient('foo_key')
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
        client = OctopusBasicClient('foo_key')
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
        client = OctopusBasicClient('foo_key')
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertRaises(ValueError,client.get_meter_point)
        with mock.patch.dict(os.environ, {'OCTOPYS_MPAN':'foo'}, clear=True):
            client.get_meter_point()
        url,params = client.get_meter_point('foo')
        self.assertEqual(url, 'https://api.octopus.energy/v1/electricity-meter-points/foo/')
        self.assertIsNone(params)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_consumption(self,mock_get):
        client = OctopusBasicClient('foo_key')
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertRaises(ValueError,client.get_consumption)
        with mock.patch.dict(os.environ, {'OCTOPYS_MPAN':'foo','OCTOPYS_SERIAL':'bar'}, clear=True):
            client.get_consumption()
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
