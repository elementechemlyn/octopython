import datetime
from datetime import timezone
import requests
from requests.auth import HTTPBasicAuth
import json
from config import API_KEY,MPAN,SERIAL

TIMESTAMP_PATH = 'octopus_last_read'
CONSUMPTION_FILE = 'consumption.json'

endpoints = {
    'consumption':'https://api.octopus.energy/v1/electricity-meter-points/%(mpan)s/meters/%(serial)s/consumption/',
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

def drop_timestamp(tspath:str=TIMESTAMP_PATH,ts:datetime.datetime = None):
    with open(tspath,'w') as f:
        if ts==None:
            ts = datetime.datetime.now(timezone.utc)
        f.write(str(ts.timestamp()))
    return ts

def get_timestamp(tspath:str=TIMESTAMP_PATH):
    try:
        with open(tspath) as f:
            ts = float(f.read())
            ts = datetime.datetime.fromtimestamp(ts,tz=timezone.utc)
    except FileNotFoundError:
        ts = datetime.datetime.now(tz=timezone.utc)
    return ts

def get_last_date_from_resp(response_json:dict):
    if response_json['count']==0:
        return None
    interval_ends = [datetime.datetime.fromisoformat(x['interval_end']) for x in response_json['results']]
    return max(interval_ends)

def get_consumption(start_time:datetime.datetime,end_time:datetime.datetime):
    param_str = 'period_from=%s&period_to=%s' % (dt_format(start_time),dt_format(end_time))
    params = {'mpan':MPAN,'serial':SERIAL}
    url = "%s?%s" % (endpoints['consumption'] % params,param_str)
    print(url)
    resp = requests.get(url,auth=make_auth())
    print(resp.status_code)
    print(resp.json())
    return resp.json()

if __name__=="__main__":
    last_ts = get_timestamp()
    consumption = get_consumption(last_ts,datetime.datetime.now(tz=timezone.utc))
    end_ts = get_last_date_from_resp(consumption)
    if end_ts:
        store_consupmtion(consumption)
        drop_timestamp(TIMESTAMP_PATH,ts=end_ts)

