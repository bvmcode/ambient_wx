import logging
from datetime import datetime
from types import SimpleNamespace

import pandas as pd
from pint import Quantity, UnitRegistry

from ambient_wx.api import ApiRequestHandler

logging.getLogger("AmbientWx").addHandler(logging.NullHandler())


class AmbientApi:
    def __init__(
        self,
        api_key,
        application_key,
        base_url="https://rt.ambientweather.net",
        version=1,
    ):
        self.api_key = api_key
        self.application_key = application_key
        self.base_url = base_url
        self.version = version
        self.api_url = f"{self.base_url}/v{self.version}"

    def __repr__(self):
        return (
            f"AmpientApi(api_key=***, application_key=***, version={self.version},"
            "base_url={self.base_url})"
        )


class WxObservation:
    ureg = UnitRegistry()
    Q_ = ureg.Quantity

    def __init__(
        self,
        dateutc,
        date,
        winddir,
        windspeedmph,
        windgustmph,
        maxdailygust,
        winddir_avg10m,
        tempf,
        humidity,
        baromrelin,
        baromabsin,
        tempinf,
        humidityin,
        hourlyrainin,
        dailyrainin,
        monthlyrainin,
        yearlyrainin,
        feelsLike,
        dewPoint,
        **kwargs,
    ):
        self.dateutc = dateutc
        self.date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.windspeedmph = self.Q_(windspeedmph, self.ureg.mph)
        self.windgustmph = self.Q_(windgustmph, self.ureg.mph)
        self.maxdailygust = self.Q_(maxdailygust, self.ureg.mph)
        self.tempf = self.Q_(tempf, self.ureg.degF)
        self.baromrelin = self.Q_(baromrelin, self.ureg.Hg)
        self.baromabsin = self.Q_(baromabsin, self.ureg.Hg)
        self.tempinf = self.Q_(tempinf, self.ureg.degF)
        self.hourlyrainin = self.Q_(hourlyrainin, self.ureg.inches)
        self.dailyrainin = self.Q_(dailyrainin, self.ureg.inches)
        self.monthlyrainin = self.Q_(monthlyrainin, self.ureg.inches)
        self.yearlyrainin = self.Q_(yearlyrainin, self.ureg.inches)
        self.feelsLike = self.Q_(feelsLike, self.ureg.degF)
        self.dewPoint = self.Q_(dewPoint, self.ureg.degF)
        self.winddir = self.Q_(winddir, self.ureg.degrees)
        self.winddir_avg10m = self.Q_(winddir_avg10m, self.ureg.degrees)
        self.humidity = self.Q_(humidity, self.ureg.percent)
        self.humidityin = self.Q_(humidityin, self.ureg.percent)
        for attr in kwargs.keys():
            self.__dict__[attr] = kwargs[attr]

    def __repr__(self):
        return f"WxObservation(date={self.date})"

    def set_units(self, field, units):
        self.__dict__[field] = self.Q_(self.__dict__[field], units)


class WxDevice:
    def __init__(
        self,
        mac_addr,
        name=None,
        location=None,
        address=None,
        elevation=None,
        lat=None,
        lon=None,
        data=None,
    ):
        self.mac_addr = mac_addr
        self.name = name
        self.location = location
        self.address = address
        self.elevation = elevation
        self.lat = lat
        self.lng = lon
        if isinstance(data, dict):
            self.data = WxObservation(**data)
        else:
            self.data = None

    def __repr__(self):
        return f"WxDevice(mac_addr={self.mac_addr})"


class WxDeviceCollection(ApiRequestHandler):
    def __init__(self, ambient_api, **kwargs):
        super().__init__(ambient_api.api_url, **kwargs)
        self.ambient_api = ambient_api

    def __repr__(self):
        return f"WxDeviceCollection(ambient_api={self.ambient_api})"

    def __parse_response_data(self):
        self.devices = []
        for data in self.raw_data:
            mac_addr = data["macAddress"]
            last_data = data["lastData"]
            info = SimpleNamespace(**data["info"])
            coords = SimpleNamespace(**info.coords)
            lat_lon = SimpleNamespace(**coords.coords)
            self.devices.append(
                WxDevice(
                    mac_addr=mac_addr,
                    name=info.name,
                    location=coords.location,
                    address=coords.address,
                    elevation=coords.elevation,
                    lat=lat_lon.lat,
                    lon=lat_lon.lon,
                    data=last_data,
                )
            )

    def get_devices(self):
        params = {}
        params["applicationKey"] = self.ambient_api.application_key
        params["apiKey"] = self.ambient_api.api_key
        endpoint = "devices"
        response = self.get(endpoint=endpoint, params=params)
        self.raw_data = response.json()
        self.__parse_response_data()


class WxObservationCollection(ApiRequestHandler):
    def __init__(self, ambient_api, device=None, mac_addr=None, **kwargs):
        super().__init__(ambient_api.api_url, **kwargs)
        self.ambient_api = ambient_api
        if device is not None:
            self.device = device
        else:
            self.device = WxDevice(mac_addr)

    def __repr__(self):
        return f"WxStationData(ambient_api={self.ambient_api}, device={self.device})"

    def __parse_response_data(self):
        self.data = [WxObservation(**record) for record in self.raw_data]

    def get_observations(self, **kwargs):
        params = {}
        params["applicationKey"] = self.ambient_api.application_key
        params["apiKey"] = self.ambient_api.api_key
        params["limit"] = kwargs.get("limit", 288)
        end_date = kwargs.get("end_date")
        if end_date:
            params["endDate"] = end_date.isoformat()
        endpoint = f"devices/{self.device.mac_addr}"
        response = self.get(endpoint=endpoint, params=params)
        self.raw_data = response.json()
        self.__parse_response_data()

    def to_dataframe(self):
        try:
            common_fields = []
            for observation in self.data:
                common_fields.extend(observation.__dict__.keys())
            common_fields = list(set(common_fields))
            data = {}
            for observation in self.data:
                obs_data = observation.__dict__
                for field in common_fields:
                    value = None
                    if field in obs_data:
                        value = obs_data[field]
                    if isinstance(value, Quantity):
                        value = value.magnitude
                    if field not in data:
                        data[field] = [value]
                    else:
                        data[field].append(value)
            return pd.DataFrame(data)
        except AttributeError:
            return pd.DataFrame()

    def write_csv(self, filepath):
        df = self.to_dataframe()
        df.to_csv(filepath, index=False)
