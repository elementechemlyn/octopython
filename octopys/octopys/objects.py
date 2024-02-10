from datetime import datetime
from . import client 
from . import utils
from . import dataclasses


#TODO - how do we helfully handle links/hateos stuff?
#TODO - get unit rates,standing charge etc.
#TODO - to page or not page - to yield or not to yield

class Products(object):
    def __init__(self,is_variable:bool=None,is_green:bool=None,is_tracker:bool=None,
                 is_prepay:bool=None,is_business:bool=False,available_at:datetime=None,
                 api_key:str=None):
        self._client:client.OctopusClient = client.OctopusClient(api_key)
        self.status:int = None       
        self.is_variable:bool = is_variable
        self.is_green:bool=is_green
        self.is_tracker:bool=is_tracker
        self.is_prepay:bool=is_prepay
        self.is_business:bool=is_business
        self.available_at:datetime=available_at
        self._products:list[dataclasses.ProductsData] = []
        self._count:int = 0

    def _call_products(self) -> None:
        for status,products in self._client.get_products(self.is_variable,self.is_green,
                                                         self.is_tracker,self.is_prepay,
                                                         self.is_business,self.available_at):
            self._count = 0
            self._products = []
            self.status = status
            if status==200:
                self._count += products['count']
                #Got a page. Parse it and add the products to self.products.
                for product in products['results']:
                    links = []
                    for link in product['links']:
                        l = dataclasses.LinkData(link['href'],link['method'],link['rel'])
                        links.append(l)
                    p = dataclasses.ProductsData(
                        product['code'],
                        product['full_name'],
                        product['display_name'],
                        product['description'],
                        product['is_variable'],
                        product['is_green'],
                        product['is_tracker'],
                        product['is_prepay'],
                        product['is_business'],
                        product['is_restricted'],
                        product['term'],
                        product['brand'],
                        None if product['available_from'] is None 
                        else utils.from_iso(product['available_from']),
                        None if product['available_to'] is None 
                        else utils.from_iso(product['available_to']),
                        links
                    )
                    self._products.append(p)
            else:
                break

    @property
    def products(self) -> list[dataclasses.ProductsData]:
        self._call_products()
        return self._products

    @property
    def count(self) -> int:
        return len(self._products)

class Product(object):
    def __init__(self,product_code:str,tariff_active_at:datetime=None,api_key:str=None):
        self._client:client.OctopusClient = client.OctopusClient(api_key)
        self.product_code:str = product_code
        self.tariff_active_at:datetime = tariff_active_at
        self.status:int = None
        self._product:dataclasses.ProductData = None

    def _build_tariff_detail(self,detail:dict) -> dataclasses.TariffDetail:
        if detail is None:
            return None
        links = []
        for link in detail['links']:
            link = dataclasses.LinkData(link['href'],link['method'],link['rel'])
            links.append(link)
        tariff_detail = dataclasses.TariffDetail(
            detail.get('code'),
            detail.get('standard_unit_rate_exc_vat'),
            detail.get('standard_unit_rate_inc_vat'),
            detail.get('standing_charge_exc_vat'),
            detail.get('standing_charge_inc_vat'),
            detail.get('online_discount_exc_vat'),
            detail.get('online_discount_inc_vat'),
            detail.get('dual_fuel_discount_exc_vat'),
            detail.get('dual_fuel_discount_inc_vat'),
            detail.get('exit_fees_exc_vat'),
            detail.get('exit_fees_inc_vat'),
            detail.get('exit_fees_type'),
            links
        )
        return tariff_detail

    def _build_tariffs(self,tariff:dict) -> dict[str:dataclasses.Tariff]:
        tariffs = {}
        for gsp,details in tariff.items():
            direct_debit_monthly_tariff = self._build_tariff_detail(
                details.get('direct_debit_monthly'))
            direct_debit_quarterly_tariff = self._build_tariff_detail(
                details.get('direct_debit_quarterly'))
            trf = dataclasses.Tariff(gsp,direct_debit_monthly_tariff,direct_debit_quarterly_tariff)
            tariffs[gsp] = trf
        return tariffs

    def _call_product(self):
        for status,product in self._client.get_product(self.product_code,self.tariff_active_at):
            self.status = status
            if status==200:
                sr_etariffs = self._build_tariffs(product['single_register_electricity_tariffs'])
                dr_etariffs = self._build_tariffs(product['dual_register_electricity_tariffs'])
                sr_gtariffs= self._build_tariffs(product['single_register_gas_tariffs'])
                sample_consumption = None
                links = []
                for link in product['links']:
                    l = dataclasses.LinkData(link['href'],link['method'],link['rel'])
                    links.append(l)
                pd = dataclasses.ProductData(
                    product['code'],
                    product['full_name'],
                    product['display_name'],
                    product['description'],
                    product['is_variable'],
                    product['is_green'],
                    product['is_tracker'],
                    product['is_prepay'],
                    product['is_business'],
                    product['is_restricted'],
                    product['brand'],
                    product['term'],
                    product['available_from'],
                    product['available_to'],
                    product['tariffs_active_at'],
                    sr_etariffs,
                    dr_etariffs,
                    sr_gtariffs,
                    sample_consumption,
                    links
                )
                self._product = pd
            else:
                break

    @property
    def product(self):
        self._call_product()
        return self._product

class MeterPoint(object):
    def __init__(self,mpan=None,api_key=None):
        self._client:client.OctopusClient = client.OctopusClient(api_key)
        self._meter_point:str = None
        self.status:int = None
        self.mpan:str = mpan

    def _call_meter_point(self) -> None:
        status,meter_point_json = list(self._client.get_meter_point(self.mpan))[0]
        self.status = status
        if status==200:
            mpd = dataclasses.MeterPointData(meter_point_json['mpan'],
                                             meter_point_json['gsp'],
                                             meter_point_json['profile_class'])
            self._meter_point = mpd

    @property
    def meter_point(self) -> dataclasses.MeterPointData:
        self._call_meter_point()
        return self._meter_point

class Consumption(object):
    pass
