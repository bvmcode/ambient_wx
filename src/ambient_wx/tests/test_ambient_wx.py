from datetime import datetime

from ambient_wx.ambient_wx import AmbientApi, WxDevice, WxObservation


def test_ambient_api_data():
    api = AmbientApi("123", "345", version=2, base_url="http://www.example.com")
    assert api.api_key == "123"
    assert api.application_key == "345"
    assert api.api_url == "http://www.example.com/v2"


class TestWxDevice:

    def setup_method(self):
        self.device_data = [
            {
                "macAddress": "00:00:00:00:00:00",
                "info": {"name": "My Weather Station", "location": "Home"},
                "lastData": {
                    "dateutc": 1515436500000,
                    "date": "2018-01-08T18:35:00.000Z",
                    "winddir": 58,
                    "windspeedmph": 0.9,
                    "windgustmph": 4,
                    "maxdailygust": 5,
                    "windgustdir": 61,
                    "winddir_avg2m": 63,
                    "windspdmph_avg2m": 0.9,
                    "winddir_avg10m": 58,
                    "windspdmph_avg10m": 0.9,
                    "tempf": 66.9,
                    "humidity": 30,
                    "baromrelin": 30.05,
                    "baromabsin": 28.71,
                    "tempinf": 74.1,
                    "humidityin": 30,
                    "hourlyrainin": 0,
                    "dailyrainin": 0,
                    "monthlyrainin": 0,
                    "yearlyrainin": 0,
                    "feelsLike": 66.9,
                    "dewPoint": 34.45380707462477,
                },
            }
        ]

    def test_initialize_object(self):
        device_data = self.device_data[0]
        mac_addr = device_data["macAddress"]
        name = device_data["info"]["name"]
        location = device_data["info"]["location"]
        data = device_data["lastData"]
        tempf = data["tempf"]
        device = WxDevice(mac_addr=mac_addr, name=name, location=location, data=data)
        assert device.mac_addr == mac_addr
        assert device.name == name
        assert device.location == location
        assert isinstance(device.data, WxObservation)
        assert device.data.tempf.magnitude == tempf


class TestWxObservation:

    def setup_method(self):
        self.data = [
            {
                "dateutc": 1515436500000,
                "date": "2018-01-08T18:35:00.000Z",
                "winddir": 58,
                "windspeedmph": 0.9,
                "windgustmph": 4,
                "maxdailygust": 5,
                "windgustdir": 61,
                "winddir_avg2m": 63,
                "windspdmph_avg2m": 0.9,
                "winddir_avg10m": 58,
                "windspdmph_avg10m": 0.9,
                "tempf": 66.9,
                "humidity": 30,
                "baromrelin": 30.05,
                "baromabsin": 28.71,
                "tempinf": 74.1,
                "humidityin": 30,
                "hourlyrainin": 0,
                "dailyrainin": 0,
                "monthlyrainin": 0,
                "yearlyrainin": 0,
                "feelsLike": 66.9,
                "dewPoint": 34.45380707462477,
                "some_other_field": 2,
            }
        ]

    def test_initialize_object(self):
        data = self.data[0]
        obs = WxObservation(**self.data[0])
        assert obs.date == datetime.strptime(self.data[0]["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        assert obs.tempf.magnitude == data["tempf"]
        assert obs.tempf.units == "degree_Fahrenheit"
        assert obs.some_other_field == self.data[0]["some_other_field"]


class TestWxDeviceCollection:
    pass


class TestWxObservationCollection:
    pass
