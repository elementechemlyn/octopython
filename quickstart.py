import datetime
from datetime import timezone
import requests
from requests.auth import HTTPBasicAuth
import json
from config import API_KEY,MPAN,SERIAL,CONSUMPTION_TIMESTAMP_PATH,CONSUMPTION_FILE,TARIFF_TIMESTAMP_PATH,TARIFF_FILE
import re

endpoints = {
    'consumption':'https://api.octopus.energy/v1/electricity-meter-points/%(mpan)s/meters/%(serial)s/consumption/',
    'products':'https://api.octopus.energy/v1/products/',
    'product':'https://api.octopus.energy/v1/products/%(product_code)s/',
    'meterpoint':'https://api.octopus.energy/v1/electricity-meter-points/%(mpan)s/',
    'tariff':'https://api.octopus.energy/v1/products/%(product)s/electricity-tariffs/%(tariff)s/standard-unit-rates/'
}

def store_consupmtion(json_data):
    f = open(CONSUMPTION_FILE,"+a")
    f.write(json.dumps(json_data))
    f.write('\n')
    f.close()

def make_auth():
    return HTTPBasicAuth(API_KEY,'')

def dt_format(dt:datetime.datetime):
    return dt.isoformat(timespec='minutes').replace("+00:00", "Z")

def drop_timestamp(tspath:str=CONSUMPTION_TIMESTAMP_PATH,ts:datetime.datetime = None):
    with open(tspath,'w') as f:
        if ts==None:
            ts = datetime.datetime.now(timezone.utc)
        f.write(str(ts.timestamp()))
    return ts

def get_timestamp(tspath:str=CONSUMPTION_TIMESTAMP_PATH):
    try:
        with open(tspath) as f:
            ts = float(f.read())
            ts = datetime.datetime.fromtimestamp(ts,tz=timezone.utc)
    except FileNotFoundError:
        ts = datetime.datetime.now(tz=timezone.utc)
    return ts

def get_last_date_from_consumption(response_json:dict):
    if response_json['count']==0:
        return None
    interval_ends = [datetime.datetime.fromisoformat(x['interval_end']) for x in response_json['results']]
    return max(interval_ends)

def get_last_date_from_rates(rates:list):
    if len(rates)==0:
        return None
    interval_ends = [datetime.datetime.fromisoformat(x['valid_to'].replace('Z','')) for x in rates]
    return max(interval_ends)

def get_consumption(start_time:datetime.datetime,end_time:datetime.datetime):
    param_str = 'period_from=%s&period_to=%s' % (dt_format(start_time),dt_format(end_time))
    params = {'mpan':MPAN,'serial':SERIAL}
    url = "%s?%s" % (endpoints['consumption'] % params,param_str)
    print(url)
    resp = requests.get(url,auth=make_auth())
    print(resp.status_code)
    #print(resp.json())
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

def store_tariffs(rates:list):
    f = open(TARIFF_FILE,"+a")
    f.write(json.dumps(rates))
    f.write('\n')
    f.close()

if __name__=="__main__":
    #Get most recent consumption
    last_ts = get_timestamp(CONSUMPTION_TIMESTAMP_PATH)
    consumption = get_consumption(last_ts,datetime.datetime.now(tz=timezone.utc))
    end_ts = get_last_date_from_consumption(consumption)
    if end_ts:
        store_consupmtion(consumption)
        drop_timestamp(CONSUMPTION_TIMESTAMP_PATH,ts=end_ts)
    #Get agile tariffs
    last_ts = get_timestamp(TARIFF_TIMESTAMP_PATH)
    rates = get_current_agile_rates(last_ts)
    print(rates)
    end_ts = get_last_date_from_rates(rates)
    if end_ts:
        store_tariffs(rates)
        drop_timestamp(TARIFF_TIMESTAMP_PATH,ts=end_ts)
