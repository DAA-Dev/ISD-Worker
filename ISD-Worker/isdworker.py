import os, logging, folium, gzip, datetime, sys
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
        self.data_file = LOC_FOLS['metadata']+META_FILES['rectangle-list']
        self.interest_year = interest_year
        self.update_area(gps_bot_left, gps_top_right)

    def update_area(self, gps_bot_left, gps_top_right):
        META_WORKER.read_filter(LOC_FOLS['metadata']+META_FILES['station-list'], 
                                LOC_FOLS['metadata']+META_FILES['rectangle-list'], 
                                ['lat', gps_bot_left[0], gps_top_right[0]], 
                                filter2=['lon', gps_bot_left[1], gps_top_right[1]])

        self.station_list = []
        meta_list = META_WORKER.get_vals(self.data_file, META_WORKER.labels)
        for sub_list in meta_list:
            self.station_list.append(WeatherStation(sub_list, self.interest_year))
        # self.clean_data()
        # Add this for the actual simulation, where the change in station window is incremental

    def make_map(self):
        coordinate_list = META_WORKER.get_vals(self.data_file, ['lat', 'lon'])
    
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
    def initialize_stations(self):
        updated_station_list = []
        for station in self.station_list:
            file_name = station.get_file_name()
            with open(LOC_FOLS['metadata']+'/'+str(self.interest_year)+'.txt', 'rt') as reader:
                for line in reader.readlines():
                    line = line.rstrip()
                    if line == file_name:
                        updated_station_list.append(station)  
                        break;
        self.station_list = updated_station_list
        for station in self.station_list:
            station.pull_gz()


    # Local method, deletes gz files if pulled for a station
    def clean_data(self):
        for filename in os.listdir(LOC_FOLS['current-data']):
            found_file = False
            for station in self.station_list:
                if station.get_file_name() == filename:
                    found_file = True
                    break
            if not found_file:
                os.remove(LOC_FOLS['current-data']+filename)
                logging.debug(TAG+'removing ' + filename)

    # Creates or updates the current window snapshot with up to date weather information
    def update_time(self, time):
        for station in self.station_list:
            station.update(time)

# Class in order to represent a station - has methods to fetch and store data
class WeatherStation():
    DATA_LABELS = ['time', 'lat', 'lon', 'elev', 'winAngle', 'visibility', 'degreesC', 'seaLvlPress']
    DATA_WORKER = DataWorker(LOC_FOLS['templates']+TEMP_FILES['station-data-temp'])

    def __init__(self, metadata, interest_year):
        self.metaDataDictionary = {}
        self.interest_year = interest_year
        self.sim_time = datetime.datetime.now()           # Default time for simulation is the most recent time, now
        for i, data in enumerate(metadata):
            self.metaDataDictionary.update({META_WORKER.labels[i] : data})
        self.data = []
    
    # Updates data as well as the sim_time of the object
    def update(self, new_time):
        logging.info(TAG+'Updating weather station...')
        prev_line = []
        prev_line_delta = sys.maxsize
        time_index = WeatherStation.DATA_WORKER.labels.index('time')
        desired_time = get_isd_time(new_time)
        with gzip.open(LOC_FOLS['current-data']+self.get_file_name(), 'rt') as gzFile:
            for line in gzFile.readlines():
                parsed_line = WeatherStation.DATA_WORKER.parse_line(line)
                time = parsed_line[time_index]
                time_delta = abs(int(time) - desired_time)
                if time_delta < prev_line_delta:
                    prev_line = line
                    prev_line_delta = time_delta
                elif time_delta < 10000:
                    break
                else:
                    logging.info(TAG+'line not in chronological order encountered')
        self.data = WeatherStation.DATA_WORKER.get_vals_lined(prev_line, WeatherStation.DATA_LABELS)
        print(self.data)

    def pull_gz(self):
        path = self.get_ftp_path()
        if not os.path.exists(LOC_FOLS['current-data']+self.get_file_name()):
            with open(LOC_FOLS['current-data']+self.get_file_name(), 'wb') as writer:
                with FTP(FTP_URL) as ftp:
                    ftp.login(user = 'anonymous', passwd=FTP_EMAIL)
                    ftp.retrbinary('RETR '+path, writer.write, 8*1024)
                    logging.info(TAG+'pulling ' + path)
        else:
            logging.info(TAG+path+' already pulled')

    def get_file_name(self):
        return self.metaDataDictionary['usaf'] + '-' + self.metaDataDictionary['wban'] + '-' + str(self.interest_year) + '.gz'

    def get_ftp_path(self):
        return FTP_GEN_PATH + str(self.interest_year) + '/' + self.get_file_name()

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

# Converts datetime into time in the format used in .gz files
def get_isd_time(time):
    isd_time = s_ext(str(time.year), 4) + s_ext(str(time.month), 2) + s_ext(str(time.day), 2) + s_ext(str(time.hour), 2) + s_ext(str(time.minute), 2)
    return int(isd_time)

def s_ext(str, length):
    while len(str) != length:
        str = '0'+str
    return str
