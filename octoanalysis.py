import config
import json
import datetime
import os

def valid_to_date(x):
    return datetime.datetime.timestamp(datetime.datetime.fromisoformat(x['valid_to']))

def valid_from_date(x):
    return datetime.datetime.timestamp(datetime.datetime.fromisoformat(x['valid_from']))

def load_tariff_data(data_file=config.TARIFF_FILE,start_ts=None,end_ts=None):
    tariffs = []
    with open(data_file) as f:
        line = f.readline()
        json_data = json.loads(line)
        tariffs.extend(json_data)
    tariffs.sort(key=valid_to_date)
    return tariffs

def load_last_data(data_file=config.TARIFF_FILE):
    with open(data_file, "rb") as file:
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:
            file.seek(0)
        last_line = file.readline().decode()
    return json.loads(last_line)    

if __name__=="__main__":
    tariffs = load_last_data()
    print(tariffs)
    print(len(tariffs))