import logging, isdworker, datetime
from isdworker import StationWindow, WeatherStation

INTEREST_YEAR = 2010
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S', level=logging.NOTSET)

logging.info('isdworker started')
isdworker.initialize_local_env()
if isdworker.metadata_pull():
    isdworker.getsort_us_data()
else:
    logging.info('No metadata pulled, continuing with program')

logging.info('This is the printout for test case number 1')
window = StationWindow([39.958175, -91.02172], [41.310949, -87.934570], INTEREST_YEAR)
window.initialize_stations()
window.update_time(datetime.datetime(2010, 7, 14, 9, 33))
window.time_step(datetime.timedelta(days = 1, hours = 1))
window.make_map().save('data/map1.html')

logging.info('This is the printout for test case number 2')
window.update_area([38.149284, -108.755224], [41.951239, -102.351951])
window.initialize_stations()
window.make_map().save('data/map2.html')


# The following statement creates and saves a map to the data directory in project folder
#window.make_map().save('data/map.html')
# Implement a checker for stations in the window, checking if the window stations are in the gz files for target years

# You can add time with the code stepped_time = time + timedelta(days=1, seconds=60, etc.)
