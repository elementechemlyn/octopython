import requests
from requests.auth import HTTPBasicAuth
from config import API_KEY,MPAN,SERIAL
import time
import datetime
import re

endpoints = {
    'consumption':'https://api.octopus.energy/v1/electricity-meter-points/%(mpan)s/meters/%(serial)s/consumption/',
    'products':'https://api.octopus.energy/v1/products/',
    'product':'https://api.octopus.energy/v1/products/%(product_code)s/',
    'meterpoint':'https://api.octopus.energy/v1/electricity-meter-points/%(mpan)s/',
    'tariff':'https://api.octopus.energy/v1/products/%(product)s/electricity-tariffs/%(tariff)s/standard-unit-rates/'
}

def dt_format(dt:datetime.datetime):
    return dt.isoformat(timespec='minutes').replace("+00:00", "Z")

def from_iso(iso_str:str):
    return datetime.datetime.fromisoformat(iso_str.replace("Z","+00:00"))
    
def make_auth():
    return HTTPBasicAuth(API_KEY,'')

def api_call(url,retry=3):
    retry_count = 0
    while 1:
        try:

            requests.get(url,auth=make_auth())
        except Exception as x:
            if retry_count<retry:
                time.sleep(10)
                retry_count += 1
            else:
                raise x

def get_consumption(start_time:datetime.datetime,end_time:datetime.datetime):
    param_str = 'period_from=%s&period_to=%s' % (dt_format(start_time),dt_format(end_time))
    params = {'mpan':MPAN,'serial':SERIAL}
    url = "%s?%s" % (endpoints['consumption'] % params,param_str)
    print(url)
    resp = requests.get(url,auth=make_auth())
    print(resp.status_code)
    return resp.json()

def get_current_products(brand='OCTOPUS_ENERGY',pattern='^AGILE-FLEX.+'):
    matched_products = []
    url = endpoints['products']
    while(not url==None):
        resp = requests.get(url,auth=make_auth())
        print(resp.status_code)
        products = resp.json()
        for product in products['results']:
            if brand==None or product['brand']==brand:
                if pattern==None or not re.match(pattern,product['code'])==None:
                    matched_products.append(product)
        url = products['next']
    return matched_products

def get_product(product_code):
    url = endpoints['product'] % {'product_code':product_code}
    resp = requests.get(url,auth=make_auth())
    print(resp.status_code)
    #print(resp.text)
    return resp.json()

def get_tariff(product_code,tariff_code,start_time):
    tariffs = []
    param_str = 'period_from=%s&page_size=1000' % (dt_format(start_time),)
    params = {'product':product_code,'tariff':tariff_code}
    url = "%s?%s" % (endpoints['tariff'] % params,param_str)
    print(url)
    while not url==None:
        resp = requests.get(url,auth=make_auth())
        print(resp.status_code)
        tariff_json = resp.json()
        print(tariff_json)
        tariffs.extend(tariff_json['results'])
        url = tariff_json['next']

    return tariffs

def get_gsp():
    params = {'mpan':MPAN}
    url = "%s" % (endpoints['meterpoint'] % params)
    resp = requests.get(url,auth=make_auth())
    print(resp.status_code)
    gsp = resp.json()
    return gsp['gsp']

def get_current_agile_rates(start_time):
    gsp = get_gsp()
    print("Got gsp",gsp)
    products = get_current_products()
    if len(products)>1:
        raise RuntimeError("Got more than one agile product!!!")
    agile_product = products[0]['code']
    product = get_product(agile_product)
    gsp_tariff = product['single_register_electricity_tariffs'][gsp]
    print(gsp_tariff)
    tariff_code = gsp_tariff['direct_debit_monthly']['code']
    print(tariff_code)
    tariff = get_tariff(agile_product,tariff_code,start_time)
    print(len(tariff))
    return(tariff)

def get_current_var_rates(starttime):
    gsp = get_gsp()
    products = get_current_products(pattern='VAR-22-11-01')
    if len(products)>1:
        raise RuntimeError("Got more than one VAR product!!!")
    var_product = products[0]['code']
    product = get_product(var_product)
    gsp_tariff = product['single_register_electricity_tariffs'][gsp]
    print(gsp_tariff)
    #print(product)