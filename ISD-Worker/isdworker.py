import os, logging, folium, gzip, datetime
from ftplib import FTP
from txtparsing import DataWorker

TAG = 'isdworker - '
FIL_TAG = 'filtered.txt'

# Range for possible simulation years
INTEREST_RANGE = (2005, 2019)

FTP_URL = 'ftp.ncdc.noaa.gov'
FTP_GEN_PATH = '/pub/data/noaa/'
FTP_EMAIL = 'martinm6@illinois.edu'

LOC_FOLS = {
    'data' : 'data/',
	'metadata' : 'data/metadata/',
	'templates' : 'data/templates/',
	'current-data' : 'data/current-data/'
}
TEMP_FILES = {
    'station-list-temp' : 'isd-history-template.txt',
    'station-data-temp' : 'station-data-template.txt'
}
META_FILES = {
    'station-list' : 'isd-history.txt',
    'rectangle-list' : 'current-rectangle.txt'
}
META_FTP_PATHS = {
    'station-list' : '/pub/data/noaa/isd-history.txt'
}
META_WORKER =  DataWorker(LOC_FOLS['templates']+TEMP_FILES['station-list-temp'])

# Class in order to represent a viewing window in the GUI
class StationWindow():
    def __init__(self, gps_bot_left, gps_top_right, interest_year):
        META_WORKER.read_filter(LOC_FOLS['metadata']+META_FILES['station-list'], 
                                     LOC_FOLS['metadata']+META_FILES['rectangle-list'], 
                                     ['lat', gps_bot_left[0], gps_top_right[0]], 
                                     filter2=['lon', gps_bot_left[1], gps_top_right[1]])
        self.interest_year = interest_year

        self.data_file = LOC_FOLS['metadata']+META_FILES['rectangle-list']
        self.station_list = []

        meta_list = META_WORKER.get_vals(self.data_file, META_WORKER.labels)
        for sub_list in meta_list:
            self.station_list.append(WeatherStation(sub_list, self.interest_year))

    def update(self, gps_bot_left, gps_top_right):
        META_WORKER.read_filter(LOC_FOLS['metadata']+META_FILES['station-list'], 
                                LOC_FOLS['metadata']+META_FILES['rectangle-list'], 
                                ['lat', gps_bot_left[0], gps_top_right[0]], 
                                filter2=['lon', gps_bot_left[1], gps_top_right[1]])

        self.station_list = []
        meta_list = META_WORKER.get_vals(self.data_file, META_WORKER.labels)
        for sub_list in meta_list:
            self.station_list.append(WeatherStation(sub_list, self.interest_year))

    def make_map(self):
        coordinate_list = self.meta_worker.get_vals(self.data_file, ['lat', 'lon'])
    
        for i, point in enumerate(coordinate_list):
            for j, val in enumerate(point):
                coordinate_list[i][j] = DataWorker.str_to_flt(val)
        map = folium.Map(location=[40.12, -88.22], zoom_start=4)
        for point in coordinate_list:
            folium.Marker(point).add_to(map)
        return map

    def debug(self, time):
        print(time)

    # Checks that all data is available for all stations in the given interest year, deletes if there is not
    def check_data_availablity(self):
        updated_station_list = []
        for station in self.station_list:
            file_name = station.get_file_name()
            with open(LOC_FOLS['metadata']+'/'+str(self.interest_year)+'.txt', 'rt') as reader:
                for line in reader.readlines():
                    line = line.rstrip()
                    if line == file_name:
                        updated_station_list.append(station)  
                        break;


    # Local method, deletes gz files if pulled for a station
    # Not sure this will even be necessary
    def clean_data(self):
        return None

    # Creates or updates the current window snapshot with up to date weather information
    # Use self.data_worker to work with gz files
    def update_snapshot(self):
        for station in self.station_list:
            logging.info(TAG+station)
        return None
    # NEXT - INCORPORATE A WORKER IN ORDER TO PULL TIMING INFORMATION 

# Class in order to represent a station - has methods to fetch and store data
class WeatherStation():
    DATA_LABELS = ['time', 'lat', 'lon', 'elev', 'win-vector', 'visibility', 'temperature', 'sea-lvl-pressure']
    DATA_WORKER = DataWorker(LOC_FOLS['templates']+TEMP_FILES['station-data-temp'])

    def __init__(self, metadata, interest_year):
        self.metaDataDictionary = {}
        self.interest_year = interest_year
        self.sim_time = datetime.datetime.now()           # Default time for simulation is the most recent time, now
        for i, data in enumerate(metadata):
            self.metaDataDictionary.update({META_WORKER.labels[i] : data})

    # Updates data without updating the time of the object
    def update(self):
        return 0
    
    # Updates data as well as the sim_time of the object
    def update(self, new_time):
        print(new_time)

    def get_file_name(self):
        return self.metaDataDictionary['usaf'] + '-' + self.metaDataDictionary['wban'] + '-' + str(self.interest_year) + '.gz'

    def get_ftp_path(self):
        return FTP_GEN_PATH + self.get_file_name(self.interest_year)

    def __str__(self):
        return str(self.metaDataDictionary)

class WindVector:
    def __init__():
        return 0

# Method to create all required folders and check for required files on local machine
def initialize_local_env():
    logging.info(TAG+'Initializing local environment')
    for path in LOC_FOLS.values():
        if not os.path.exists(path):
            if path is LOC_FOLS['templates']:
                logging.error(TAG+'the required templates are missing')
            logging.info(TAG+'Creating ' + path)
            os.mkdir(path)
        else:
            logging.info(TAG + path + ' found')

# Method to check for and pull metadata, returns if there was data pulled
def metadata_pull():
    logging.info(TAG+'Checking for metadata')
    data_pulled = False
    with FTP(FTP_URL) as ftp:
        ftp.login(user = 'anonymous', passwd=FTP_EMAIL)
        for fileKey in META_FILES.keys():
            if not os.path.exists(LOC_FOLS['metadata']+META_FILES[fileKey]):
                data_pulled = True
                logging.info(TAG+'Attempting pull of '+META_FILES[fileKey]+' from FTP server')
                with open(LOC_FOLS['metadata']+META_FILES[fileKey], 'wb') as writer:
                    try:
                        ftp.retrbinary('RETR '+META_FTP_PATHS[fileKey], writer.write)
                        logging.info(TAG+'\tPull successful')
                    except:
                        data_pulled = False
                        logging.info(TAG+'\tMetadata file '+META_FILES[fileKey]+' was not found on the FTP server')
        for i in range (INTEREST_RANGE[0], INTEREST_RANGE[1]):
            if not os.path.exists(LOC_FOLS['metadata']+str(i)+'.txt'):
                data_pulled = True
                logging.info(TAG+'Downloading metadata for ' + str(i))
                file_list = ftp.nlst(FTP_GEN_PATH+str(i)+'/')
                DataWorker.save_lines(LOC_FOLS['metadata']+str(i)+'.txt', file_list, [20, len(file_list)])
    return data_pulled

# Method to strip away stations not in the United States, as well as quicksort and merge metadata
def getsort_us_data():
    worker = DataWorker(LOC_FOLS['templates']+TEMP_FILES['station-list-temp'])

    logging.info(TAG+'Reading pulled ISD metadata')
    DataWorker.read_save(22, 29700, LOC_FOLS['metadata']+META_FILES['station-list'], LOC_FOLS['metadata']+FIL_TAG)
    DataWorker.replace(LOC_FOLS['metadata']+META_FILES['station-list'], LOC_FOLS['metadata']+FIL_TAG)

    logging.info(TAG+'Filtering metadata for US stations')
    worker.read_filter(LOC_FOLS['metadata']+META_FILES['station-list'], LOC_FOLS['metadata']+FIL_TAG, ['lat', 24.53105, 49.04069], filter2=['lon', -124.48491, -66.56499])
    DataWorker.replace(LOC_FOLS['metadata']+META_FILES['station-list'], LOC_FOLS['metadata']+FIL_TAG)

    logging.info(TAG+'Quicksorting metadata w/latitude')
    worker.quicksort_lg(LOC_FOLS['metadata']+META_FILES['station-list'], LOC_FOLS['metadata']+FIL_TAG, 'lat')
    DataWorker.replace(LOC_FOLS['metadata']+META_FILES['station-list'], LOC_FOLS['metadata']+FIL_TAG)
