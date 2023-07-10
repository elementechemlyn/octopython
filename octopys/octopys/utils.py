import datetime

"""
Convert a datetime object to an ISO string using Z to indicate UTC
"""
def to_iso(dt:datetime.datetime):
    return dt.isoformat(timespec='minutes').replace("+00:00", "Z")

"""
Convert an ISO string using Z to indicate UTC to a datetime object
"""
def from_iso(iso_str:str):
    return datetime.datetime.fromisoformat(iso_str.replace("Z","+00:00"))
    
