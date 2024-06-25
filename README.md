# Ambient Weather Station API Wrapper

There are a couple of great packages that do a great job but this package introduces units.
It also serves as a side-project for me. ☺️

This is currently a work in progress to get it in a package and with the proper tests and CI.

### Install

python 3.8 or greater is required

`pip install ambient_wx`

### Units

Units are set for these fields using the [pint](https://pint.readthedocs.io/en/stable/) python library:
* windspeedmph - mph
* windgustmph - mph
* maxdailygust - mph
* tempf - degF
* baromrelin - Hg
* baromabsin - Hg
* tempinf - degF
* hourlyrainin - inches
* dailyrainin - inches
* monthlyrainin - inches
* yearlyrainin - inches
* feelsLike - degF
* dewPoint - degF
* winddir - degrees
* winddir_avg10m - degrees
* humidity - percent
* humidityin - percent

### Setup the API object
```python
from ambient_wx import AmbientApi
api_key = "123"
app_key = "456"
api = AmbientApi(api_key, app_key)
```

### Get Devices
```python
from ambient_wx import WxDeviceCollection
devices = WxDeviceCollection(api)
devices.get_devices()
device = devices.devices[0] # first device
print(device.mac_addr)
```

### Get Device Obervations
```python
from ambient_wx import WxObservationCollection
# with a device object
obs = WxObservationCollection(api, device=device)

# or with a known device mac addr to skip an api call for a device
obs = WxObservationCollection(api, mac_addr="some_mac_addr")

# get the last 5 observations this populates obs.data as a 
# list of WxObservation objects
obs.get_observations(limit=5)

# iterate through observations
for o in obs.data:
    print(o.tempf, o.winddir, o.humidity)
```

### Get data for an end date
```python
obs = WxObservationCollection(api, device)
obs.get_observations(end_date=datetime(2024, 4, 25))

for o in obs.data:
    print(o.tempf, o.winddir, o.humidity)
```

### Perform Unit Conversions
```python
# convert deg F to deg C
degc = obs.data[0].tempf.to('degC') 
print(degc)
```

### Create pandas Dataframe from Observations
```python
df = obs.to_dataframe()
print(df)
```

### Write csv from Observations
```python
obs.write_csv("/some_path/my_observations.csv")
```
