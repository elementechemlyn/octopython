"""Python dataclasses to represent json data retrieved from the API
"""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LinkData(object):
    """Dataclass to represnt links from json responses
    """
    href:str
    method:str
    rel:str

@dataclass
class MeterPointData():
    """Dataclass to represnt data retrieved from the meter point endpoint
    """
    mpan:str
    gsp:str
    profile_class:str

@dataclass
class ProductsData():
    """Dataclass to represnt data retrieved from the products endpoint
    """
    code:str
    full_name:str
    display_name:str
    description:str
    is_variable:bool
    is_green:bool
    is_tracker:bool
    is_prepay:bool
    is_business:bool
    is_restricted:bool
    term:str
    brand:str
    available_from:datetime
    available_to:datetime
    links:list[LinkData]

@dataclass
class TariffDetail():
    """Dataclass to represnt tariff data retrieved from the meter point endpoint
    """
    code:str
    standard_unit_rate_exc_vat:float
    standard_unit_rate_inc_vat:float
    standing_charge_exc_vat:float
    standing_charge_inc_vat:float
    online_discount_exc_vat:float
    online_discount_inc_vat:float
    dual_fuel_discount_exc_vat:float
    dual_fuel_discount_inc_vat:float
    exit_fees_exc_vat:float
    exit_fees_inc_vat:float
    exit_fees_type:str
    links:list[LinkData]

@dataclass
class Tariff():
    """Dataclass to represnt tariffs retrieved from the meter point endpoint
    """
    gsp:str
    direct_debit_monthly_tariff:TariffDetail
    direct_debit_quarterly_tariff:TariffDetail

@dataclass
class ProductData():
    """Dataclass to represnt data retrieved from the product endpoint
    """
    code:str
    full_name:str
    display_name:str
    description:str
    is_variable:bool
    is_green:bool
    is_tracker:bool
    is_prepay:bool
    is_business:bool
    is_restricted:bool
    brand:str
    term:int
    available_from:datetime
    available_to:datetime
    tariffs_active_at:datetime
    single_register_electricity_tariffs:dict[str:Tariff]
    dual_register_electricity_tariffs:dict[str:Tariff]
    single_register_gas_tariffs:dict[str:Tariff]
    sample_consumption:dict[str:dict[str:int]]
    links:list[LinkData]
