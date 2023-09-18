# This code just handles the processing of the HUC4 zipped shapefiles from:
# https://apps.nationalmap.gov/downloader/#/
# It moves the shapefiles and other required files to a project directory, and (eventually) deletes the rest

import os
import re
import zipfile
import shutil

zip_path = '../shapefile_temp/'
temp_path = '../extract_temp/'
folder = 'Shape'
dest = '/US_HUC4_SF'
prefix = 'NHD_H_'
files_to_extract = ['Shape/WBDHU4.dbf', 'Shape/WBDHU4.prj', 'Shape/WBDHU4.shp', 'Shape/WBDHU4.shx']

for file in os.listdir(zip_path):
    print(file)
    region = re.search(r'\d{4}', file).group() + '_'
    path = os.path.join(zip_path, file)
    
    with zipfile.ZipFile(path, 'r') as zip_file:
        for file in files_to_extract:
            zip_file.extract(file, temp_path)


