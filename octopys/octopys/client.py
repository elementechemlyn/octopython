import requests
import requests.auth
import time
from datetime import datetime
from . import utils
import os

endpoints = {
    'consumption':'https://api.octopus.energy/v1/electricity-meter-points/%(mpan)s/meters/%(serial)s/consumption/',
    'products':'https://api.octopus.energy/v1/products/',
    'product':'https://api.octopus.energy/v1/products/%(product_code)s/',
    'meterpoint':'https://api.octopus.energy/v1/electricity-meter-points/%(mpan)s/',
    'tariff':'https://api.octopus.energy/v1/products/%(product_code)s/electricity-tariffs/%(tariff)s/standard-unit-rates/'
}

class OctopusClient(object):
    def __init__(self,api_key:str=None,retry_count:int=3,retry_wait:int=5):
        self.api_key = api_key
        if self.api_key==None:
            self.api_key = os.environ.get('OCTOPYS_API_KEY')
            if self.api_key==None:
                raise ValueError("API Key must be provided.")
        self.retry_count = retry_count
        self.retry_wait=retry_wait
        self.client = OctopusBasicClient(api_key,retry_count,retry_wait)

    def _yield_responses(self,resp):
            while True:
                if resp.status_code==200:
                    json_payload = resp.json()
                    yield resp.status_code,json_payload
                    if json_payload['next']==None:
                        break
                    else:
                        resp = self.client.get_next(json_payload['next'])
                else:
                    yield resp.status_code,resp.text
                    break

    def get_products(self,is_variable:bool=None,is_green:bool=None,is_tracker:bool=None,is_prepay:bool=None,is_business:bool=False,available_at=None):
        resp = self.client.get_products(is_variable,is_green,is_tracker,is_prepay,is_business,available_at)
        return self._yield_responses(resp)

    def get_product(self,product_code:str,tariffs_active_at:datetime=None):
        resp = self.client.get_product(product_code,tariffs_active_at)
        return self._yield_responses(resp)
    
    def list_tariff_charges(self,product_code:str,tariff_code:str,period_from:datetime=None,period_to:datetime=None,page_size:int=None):
        resp = self.client.list_tariff_charges(product_code,tariff_code,period_from,period_to,page_size)
        return self._yield_responses(resp)

    def get_meter_point(self,mpan:str=None):
        resp = self.client.get_meter_point(mpan)
        return self._yield_responses(resp)

    def get_consumption(self,mpan:str=None,serial:str=None,period_from:datetime=None,period_to:datetime=None,page_size:int=None,order_by:str=None,group_by:str=None):
        resp = self.client.get_consumption(mpan,serial,period_from,period_to,page_size,order_by,group_by)
        return self._yield_responses(resp)

class OctopusBasicClient(object):

    def __init__(self,api_key:str=None,retry_count:int=3,retry_wait:int=5):
        self.api_key = api_key
        if self.api_key==None:
            self.api_key = os.environ.get('OCTOPYS_API_KEY')
            if self.api_key==None:
                raise ValueError("API Key must be provided.")
        self.retry_count = retry_count
        self.retry_wait=retry_wait

    """
    Build an http auth header with api key is username and an empty password
    """
    def _make_auth(self):
        return requests.auth.HTTPBasicAuth(self.api_key,'')

    def _build_params(self,params:list[tuple]):
        param_dict = {}
        for key,value in params:
            if(not value==None):
                if(type(value)==datetime):
                    value = utils.to_iso(value)
                param_dict[key] = value

        return param_dict if len(param_dict)>0 else None
        
    """
    Make at most 'retry' attempts to call an endpoint waiting 'wait_time' seconds between each call
    """
    def _api_call(self, url:str, params:list=None):
        retry_count = 0
        if params:
            params = self._build_params(params)
        while 1:
            try:
                resp = requests.get(url,params=params,auth=self._make_auth())
                return resp
            except Exception as x:
                retry_count += 1
                if retry_count<self.retry_count:
                    time.sleep(self.retry_wait)
                else:
                    raise x

    def get_next(self,next_url:str):
        resp = self._api_call(next_url)
        return resp
            
    def get_products(self,is_variable:bool=None,is_green:bool=None,is_tracker:bool=None,is_prepay:bool=None,is_business:bool=False,available_at=None):
        url = endpoints['products']
        resp = self._api_call(url)    
        return resp
    
    def get_product(self,product_code:str,tariffs_active_at:datetime=None):
        url = endpoints['product'] % {'product_code':product_code}
        params = [("tariffs_active_at",tariffs_active_at)]
        resp = self._api_call(url,params)    
        return resp

    def list_tariff_charges(self,product_code:str,tariff_code:str,period_from:datetime=None,period_to:datetime=None,page_size:int=None):
        url = endpoints['tariff'] % {'product_code':product_code,'tariff':tariff_code}
        params = [
            ("period_from",period_from),
            ("period_to",period_to),
            ("page_size",page_size),
        ]
        resp = self._api_call(url,params)    
        return resp

    def get_meter_point(self,mpan:str=None):
        if(mpan==None):
            mpan = os.environ.get('OCTOPYS_MPAN')
            if(mpan==None):
                raise ValueError("MPAN must be provided")
        url = endpoints['meterpoint'] % {'mpan':mpan}
        resp = self._api_call(url)    
        return resp

    def get_consumption(self,mpan:str=None,serial:str=None,period_from:datetime=None,period_to:datetime=None,page_size:int=None,order_by:str=None,group_by:str=None):
        if(mpan==None):
            mpan = os.environ.get('OCTOPYS_MPAN')
            if(mpan==None):
                raise ValueError("MPAN must be provided")
        if(serial==None):
            serial = os.environ.get('OCTOPYS_SERIAL')
            if(serial==None):
                raise ValueError("Serial must be provided")
        if((not order_by==None) and (order_by not in ['period','-period'])):
            raise ValueError("invalid order_by value")
        if((not group_by==None) and (group_by not in ['hour','day','week','month','quarter'])):
            raise ValueError("invalid group_by value")
        url = endpoints['consumption'] % {'mpan':mpan,'serial':serial}
        params = [
            ("period_from",period_from),
            ("period_to",period_to),
            ("page_size",page_size),
            ('order_by',order_by),
            ('group_by',group_by),            
        ]
        resp = self._api_call(url,params)    
        return resp

