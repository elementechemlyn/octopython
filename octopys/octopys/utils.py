"""General utility functions
"""
import datetime

def to_iso(dt_obj:datetime.datetime):
    """Convert a datetime object to an ISO string using Z to indicate UTC
    """
    return dt_obj.isoformat(timespec='minutes').replace("+00:00", "Z")

def from_iso(iso_str:str):
    """
    Convert an ISO string using Z to indicate UTC to a datetime object
    """
    return datetime.datetime.fromisoformat(iso_str.replace("Z","+00:00"))
