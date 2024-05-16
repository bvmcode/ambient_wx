import logging
from datetime import datetime

from dotenv import dotenv_values

from ambient_wx import AmbientApi, WxDeviceCollection, WxObservationCollection, WxDevice

# add logging
logging.basicConfig(filename='app.log', filemode='w', format='%(levelname)s: %(asctime)s - %(message)s', level=logging.DEBUG)


creds = dict(dotenv_values(".env"))

# set up the Ambient api object
api = AmbientApi(creds["AMBIENT_API_KEY"], creds["AMBIENT_APPLICATION_KEY"])

# get all the devices
devices = WxDeviceCollection(api)
devices.get_devices()
device = devices.devices[0] # first device
print(device.mac_addr)


# set a device if mac address already known (bypass above call)
device = WxDevice(creds["AMBIENT_MAC_ADDRESS"])



# Get data from the device, returns a list of observations (WxObservation)
obs = WxObservationCollection(api, device)
obs.get_observations()
print(obs.data[0].date)
print(obs.data[0].tempf)
print(obs.data[0].winddir)
print(obs.data[0].humidity)
print(obs.data[0].humidity.units)
# convert deg F to deg C
degc = obs.data[0].tempf.to('degC')
print(degc)

df = obs.to_dataframe()
print(df)


# Get data with an end_date
obs.get_observations(end_date=datetime(2024, 4, 25))
obs.write_csv("myfile.csv")
