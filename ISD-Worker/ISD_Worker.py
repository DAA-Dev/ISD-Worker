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

logging.info('This is the printout for rect1')
window = StationWindow([39.958175, -91.02172], [41.310949, -87.934570], INTEREST_YEAR)
window.check_data_availablity()
window.debug(datetime.datetime.now())
window.debug(datetime.datetime(2005, 7, 14, 12, 30))

logging.info('This is the printout for rect2')
window.update([38.149284, -108.755224], [41.951239, -102.351951])
window.check_data_availablity()


# The following statement creates and saves a map to the data directory in project folder
#window.make_map().save('data/map.html')
# Implement a checker for stations in the window, checking if the window stations are in the gz files for target years


# Things to do:
#   Create a binary search method to search through the US stations
#   Create a method to list out station matches for a given year as an int

# This code can download a gz file
    #with open(loc_fols['gzs']+sample_file, 'wb') as writer:
    #    ftp.retrbinary('RETR '+isd_folder+sample_year+sample_file, writer.write, 8*1024)

# This code converts the gz file into a txt file, good for visual debugging
#logging.debug('Converting gz file into a txt file')
#with gzip.open(loc_fols['gzs']+sample_file, 'rt') as gzFile:
#    with open(loc_fols['gzs']+unzipped_file, 'wt') as writer:
#        writer.write(gzFile.read())

#worker = DataWorker(loc_fols['templates']+'station-data-template.txt')
#with open(loc_fols['gzs']+unzipped_file, 'r') as reader:
#    for line in reader:
#        print(worker.parse_line(line))
#logging.info('Program execution finished')

# Figure out if whole file read and then binary search is faster as opposed to a line by line search shifting prev and next value
