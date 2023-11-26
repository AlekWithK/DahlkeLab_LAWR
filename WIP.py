import pandas as pd
from dataretrieval import nwis

df = nwis.get_record(sites=['11447650', '11303500'], service='dv', parameterCD='00060', start='1900-10-01', end='2020-09-30')
df.reset_index()
print(df)


'''for i in range(len(date_series)):
    if i == 0: # First date
        if (date_series.iloc[i+1] - date_series.iloc[i]).days != 1:
            one_day_peaks.append(date_series.iloc[i])
    elif i == (len(date_series) - 1): # Last date
        if (date_series.iloc[i] - date_series.iloc[i - 1]).days != 1:
            one_day_peaks.append(date_series.iloc[i])
    else: # All other dates
        if ((date_series.iloc[i+1] - date_series.iloc[i]).days != 1 and 
            (date_series.iloc[i] - date_series.iloc[i - 1]).days != 1):
            one_day_peaks.append(date_series.iloc[i])'''
            
'''for i in range(len(date_series)):
    if (date_series.iloc[i] - curr_year)'''
    
    
'''zip_path = '../shapefile_temp/'
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
                zip_file.extract(file, temp_path)'''