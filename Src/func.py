# IMPORTS
import os
import pandas as pd
import numpy as np
import warnings
import calendar
import pymannkendall as mk
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as cx
from shapely.geometry import Point
import matplotlib.colors as mcolors

from datetime import datetime
from itertools import chain

#--------------------------#
#-------# CONSTANTS #------#
#--------------------------#

# Data Retrieval Tool Constants
SERVICE = 'dv'
STATE_CODE = 'CA'
PARAM_CODE = '00060'
DEFAULT_START = '1900-10-01'
DEFAULT_END = '2020-09-30'

# Calculation Constants
# These are the thresholds to be analyzed
QUANTILE_LIST = [0.90, 0.95]
# Data ranges -- Number of years to be analyzed
DATA_RANGE_LIST = [30, 50]
# Threshold for single-site testing
QUANTILE = 0.90
# Minimum number of years of data a site must have present to be analyzable (50 years, or largest value in DATA_RANGE_LIST if > 50)
MIN_DATA_PERIOD = max(50, max(DATA_RANGE_LIST))
# Maximum % of data that can be missing
MAX_MISSING_THRESHOLD = 0.10
MK_TREND_ALPHA = 0.05

# Miscellaneous Constants
HYDRO_YEAR = 'AS-OCT'
SORT_BY_WB = True

# Site ID URI
SITES_URI = f'https://waterdata.usgs.gov/{STATE_CODE}/nwis/current?index_pmcode_STATION_NM=1&index_pmcode_DATETIME=2&index_pmcode_{PARAM_CODE}=3&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=site_no&column_name=station_nm&column_name=dec_lat_va&column_name=dec_long_va&column_name=sv_begin_date&column_name=sv_end_date&sort_key_2=site_no&html_table_group_key=NONE&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection'
SEC_PER_DAY = 86400
CUBIC_FT_KM_FACTOR = 0.0000000000283168466

#--------------------------------------#
#-------# CALCULATION FUNCTIONS #------#
#--------------------------------------#

def validate(df: pd.DataFrame, start: datetime, end: datetime):
    """Returns the % amount of data missing from the analyzed range"""
    t_delta = pd.to_datetime(end) - pd.to_datetime(start)
    days = t_delta.days
    missing = max(1.0 - (len(df) / days), 0)           
    return missing

def calc_threshold(df: pd.DataFrame, value: float):
    """Returns a threshold above which flow is considered HMF given flow values and a threshold 0 < t < 1""" 
    df = pd.DataFrame(df['00060_Mean'])
    return df.quantile(q=value, axis=0).iloc[0]

def filter_hmf(df: pd.DataFrame, threshold: float):
    """Returns a dataframe with only flow values above a given threshold present, and a second with non-HMF years zero deflated"""
    hmf_series_cont = df.copy()
    hmf_series_defl = df[df['00060_Mean'] > threshold]    
    hmf_series_cont['00060_Mean'] = hmf_series_cont['00060_Mean'].apply(lambda x: x if x >= threshold else 0) 
    return hmf_series_defl, hmf_series_cont

def convert_hmf(df: pd.DataFrame, threshold: float):
    """Converts flow values from ft^3/s to ft^3/day and returns the difference in flow above the threshold"""
    df['00060_Mean'] = df['00060_Mean'].apply(lambda x: (x - threshold) * SEC_PER_DAY if x > 0 else 0)
    return df

def monthly_hmf(df: pd.DataFrame, data_range: int, quantile: float):
    """Returns the average HMF value per month over the analyzed data period"""
    df = df.reset_index()
    # Aggregate hmf by month
    df['00060_Mean'] = df['00060_Mean'] * CUBIC_FT_KM_FACTOR
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Suppresses obnoxious timezone warning every time this function is called. As far as I can tell we do not care about
    # timezone information in this study, and so dropping tz information will not affect the data
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        df_grouped = df.groupby(df['datetime'].dt.to_period("M")).agg({'00060_Mean': 'sum', 'datetime': 'size'})
        
    df_grouped.rename(columns={'datetime': 'count'}, inplace=True)   
    df_grouped = df_grouped.reset_index()
     
    # Aggregate months by year    
    df_grouped['month'] = df_grouped['datetime'].dt.month
    df_grouped = df_grouped.groupby('month').agg({'00060_Mean': 'sum', 'datetime': 'size'})
    df_grouped.rename(columns={'datetime': 'count'}, inplace=True) 
    df_grouped = df_grouped.reset_index()
    
    # Temporary code for monthly frequency dataset production
    # Right now set to only produce the 30 year, 90th quantile dataset
    '''
    if data_range == 30 and quantile == 0.9:
        temp_path = 'Prelim_Data/monthly_hmf_frq.csv'
        df_temp = df_grouped.copy()
        if os.path.exists(temp_path):
            sheet_data = pd.read_csv(temp_path)
            for i, row in df_temp.iterrows():
                month = row['month']
                count = row['count']
                
                if month in sheet_data['month'].values:
                    sheet_data.loc[sheet_data['month'] == month, 'count'] += count
                else:
                    new_row = pd.DataFrame({'month': [month], 'count': [count]})
                    sheet_data = pd.concat([sheet_data, new_row])
            
            sheet_data.to_csv(temp_path, index=False)
            
        else:
            try:
                df_grouped.to_csv(temp_path)
            except Exception as e:
                print(e)
    '''   
    
    # Calculate average hmf per month including 0's (see Methodology note)
    df_grouped['00060_Mean'] = df_grouped['00060_Mean'] / df_grouped['count']
    
    # Create a dataframe to return for concatenation with single site frame
    df_pivot = df_grouped.pivot_table(index=None, columns='month', values='00060_Mean', aggfunc='first')
    df_pivot = df_pivot.reindex(range(1, 13), axis=1)
    df_pivot.fillna(0, inplace=True)

    # Rename columns to reflect their months
    df_pivot.columns = [(calendar.month_name[i][:3] + '_hmf').lower() for i in df_pivot.columns]
    
    #df_grouped.to_csv('monthly_hmf.csv')
    return df_pivot

def num_hmf_years(df: pd.DataFrame, offset: int):
    """Returns the integer number of HMF years, using an offset to indicate the start of the Hydrologic Year (i.e. 10 = October)"""
    df.loc[:, 'datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)    
    df.loc[:, 'offsetdate'] = (df.index - pd.offsets.YearBegin(month=offset))    
    return df['offsetdate'].dt.year.nunique()

def three_six_range(df: pd.DataFrame, three_start: int, three_end: int, six_start: int, six_end: int):
    """Returns two dataframes, one with a six month period, and one with a three month period, based on given start and end months for both"""
    df = df.reset_index()
    df.loc[:, 'datetime'] = pd.to_datetime(df['datetime'])    
    six_month_mask = (df['datetime'].dt.month >= six_start) | (df['datetime'].dt.month <= six_end)
    three_month_mask = (df['datetime'].dt.month >= three_start) | (df['datetime'].dt.month <= three_end)
    return df[six_month_mask], df[three_month_mask]

def calc_duration_intra_annual(df: pd.DataFrame, hmf_years: int):
    """Calculates the average duration of HMF events per year and the intra-annual frequency of events
       per year. Also returns a results dataframe for use in the duration and intra-annual MK tests"""
    df_d = df.reset_index()
    df_d['datetime'] = df_d['datetime'] + pd.DateOffset(months=-9)

    # Create a binary column for HMF events
    df_d['flow_bool'] = df_d['00060_Mean'].apply(lambda x: 1 if x > 0 else 0)

    # Initialize results dataframe with required years 
    years = list(range(df_d["datetime"].dt.year.min(), df_d["datetime"].dt.year.max() + 1))
    df_results = pd.DataFrame()

    # Average HMF/year calculation
    df_results = df_d.groupby(df_d["datetime"].dt.year)["00060_Mean"].sum().reset_index()
    df_results["00060_Mean"] = df_results["00060_Mean"] * CUBIC_FT_KM_FACTOR

    # Total days per year calculation
    df_results["total_days"] = df_d.groupby(df_d["datetime"].dt.year)["flow_bool"].sum().reset_index()["flow_bool"]

    # Total events per year calculation
    df_d['Year'] = df_d['datetime'].dt.year
    df_d['Change'] = df_d['flow_bool'].diff()
    series_continuous_sets = df_d[(df_d['Change'] == 1) & (df_d['flow_bool'] == 1)].groupby('Year').size()
    series_continuous_sets = series_continuous_sets.reset_index()
    series_continuous_sets.columns = ['Year', 'total_events']
    df_results.rename(columns={'datetime': 'Year'}, inplace=True)
    df_results = pd.merge(df_results, series_continuous_sets, on='Year', how='left')
    df_results = df_results.fillna(0)

    # Event HMF
    df_results['event_hmf'] = df_results['00060_Mean'] / df_results['total_events']

    # Event Duration
    df_results['duration'] = df_results['total_days'] / df_results['total_events']
    
    # Annual, Event, and Intra-annual calculations
    df_results = df_results.fillna(0)
    annual_duration = df_results['total_days'].sum() / hmf_years    
    event_duration = df_results['duration'].sum() / hmf_years
    intra_annual = df_results['total_events'].sum() / hmf_years
    event_hmf = df_results['event_hmf'].sum() / hmf_years
    
    return event_duration, annual_duration, intra_annual, event_hmf, df_results

# Old intra-annual calculation
'''def calc_intra_annual(df: pd.Series, hmf_years: int):
    """Calculates the number of HMF events per hydrological year (consecutive days count as one event). 
       Also returns a zero-deflated dataframe for use in the intra-annual MK test""" 
    df = df.reset_index()   
    # Offsetting dates to make calculations easier (currently HARDCODED)
    date_series = pd.to_datetime(df['datetime'])        
    date_series = date_series + pd.DateOffset(months=-9)
    
    df = pd.DataFrame(columns=['Year'])
    
    for i in range(len(date_series)):
        if i == 0:   
            df = pd.concat([df, pd.DataFrame({'Year': date_series.iloc[i].year}, index=[i])], ignore_index=True, axis=0)                          
        else:
            if (date_series.iloc[i] - date_series.iloc[i - 1]).days > 1:
                df = pd.concat([df, pd.DataFrame({'Year': date_series.iloc[i].year}, index=[i])], ignore_index=True, axis=0)
    
    # Group and sum years, and insert missing years with 0 for MK test
    df = df.groupby('Year').size().reset_index(name='hmf_events')
    series_defl = df.copy()
    years = pd.DataFrame({'Year': range(df['Year'].min(), df['Year'].max() + 1)})
    df = pd.merge(years, df, how='left', on='Year')
    df['hmf_events'].fillna(0, inplace=True)
    series_cont = df.copy()
    
    return df['hmf_events'].sum() / hmf_years, series_defl, series_cont'''

def calc_oneday_peaks(df: pd.DataFrame):
    """Calculates the number of one-day peaks per hydrological year"""    
       
    return

def calc_timing(df: pd.DataFrame):
    """Calculates the average numerical day per hydrologic year that HMF reaches the center of mass threshold"""
    df = df.reset_index()
    
    df['datetime'] = df['datetime'] + pd.DateOffset(months=-9)
    
    df['year'] = df['datetime'].dt.year
    df['day'] = df['datetime'].dt.dayofyear
    df['cumsum'] = df.groupby('year')['00060_Mean'].cumsum()
    df['t_sum'] = df.groupby('year')['00060_Mean'].transform('sum')

    com_series = df[df['cumsum'] >= df['t_sum'] / 2].groupby('year')['day'].first()
    timing = com_series.mean()    

    return timing
    
def convert_cubic_ft_hm(value: float):
    """Convert ft^3 to km^3"""
    return value * CUBIC_FT_KM_FACTOR

def mann_kendall(defl_data: pd.Series, cont_data: pd.Series, alpha: float):
    """Perform a Mann-Kendall Trend test on a continuous series of data and a zero-deflated series"""
    data = mk.original_test(defl_data, alpha=alpha) + mk.original_test(cont_data, alpha=alpha)
    mk_trend = pd.DataFrame([data], columns=['trend_zd', 'h_zd', 'p_zd', 'z_zd', 'tau_zd', 's_zd', 'var_s_zd', 'slope_zd', 'int_zd', 
                                           'trend', 'h', 'p', 'z', 'tau', 's', 'var_s', 'slope', 'int'])  

    return mk_trend

def create_state_uri(state: str, param: str):
    """Creates the URL on a per state from which a list of site_id's to be processed and analzyed is scraped"""
    return f'https://waterdata.usgs.gov/{state}/nwis/current?index_pmcode_STATION_NM=1&index_pmcode_DATETIME=2&index_pmcode_{PARAM_CODE}=3&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=site_no&column_name=station_nm&column_name=dec_lat_va&column_name=dec_long_va&column_name=sv_begin_date&column_name=sv_end_date&sort_key_2=site_no&html_table_group_key=NONE&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection'
    
    
def filter_by_valid(df: pd.DataFrame):
    """Filters a dataframe by it's 'valid' column and returns two dataframes, the first being valid and second invalid gauges"""
    df_valid = df[df['valid'] == True]
    df_invalid = df[df['valid'] == False]    
    return df_valid, df_invalid

def gages_2_filtering(df: pd.DataFrame):
    """Adds a column to the site dataframe indicating presence in the HCDN-2009 Gages-II Network"""
    path = 'GagesII/g2_list.csv'
    df_g2 = pd.read_csv(path)        
    df['HCDN_2009'] = df['site_no'].isin(df_g2['STAID'].astype(str)) 
    return df

def save_data(df_site_metrics: pd.DataFrame, df_mk_magnitude: pd.DataFrame, df_mk_duration: pd.DataFrame, df_mk_intra_annual: pd.DataFrame, aq_name: str):
    """Splits the resulting 'aquifer_sites' dataframe into individual frames and saves them as CSV's into Prelim_Data"""
    
    #TODO: Remove this once site_analysis() is updated to return a list of dataframes
    dataframes = [df_site_metrics, df_mk_magnitude, df_mk_duration, df_mk_intra_annual]
    sheet_names = ['site_metrics', 'mk_magnitude', 'mk_duration', 'mk_intra_annual']
    step = len(QUANTILE_LIST) * len(DATA_RANGE_LIST)
    
    # Creating lists of each of the 4 (2 date range x 2 quantile) dataframes based on ID     
    df_master_list = []
    # 0 = site_metrics, 1 = magnitude, 2 = duration, 3 = intra_annual
    for df in dataframes:
        df_list = [group for _, group in df.groupby('dataset_ID')]
        for df_l in df_list:
            df_l = df_l.drop('dataset_ID', axis=1)
            df_l = df_l.drop_duplicates(subset=['site_no'])
            df_l = df_l.reset_index(drop=True)
            df_master_list.append(df_l)
            
    # Reordering df_master_list so that dataframes are grouped by spreadsheet they're a member of
    order_key = [i + j for j in range(step) for i in range(0, len(df_master_list), step)]
    df_master_list = [df_master_list[i] for i in order_key]        
    
    # Step through the master list, adding the first 4 dataframes to the first spreadsheet, the second four to the second, and so on        
    for i, df in enumerate(df_master_list):
        if i // step == 0: # First 4 dataframes
            path = f'Prelim_Data/{aq_name}_{DATA_RANGE_LIST[0]}_{int(QUANTILE_LIST[0] * 100)}.xlsx'
            if os.path.exists(path):               
                with pd.ExcelWriter(path, mode='a') as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)                  
            else:
                with pd.ExcelWriter(path) as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)
                                        
        elif i // step == 1: # 5-8
            path = f'Prelim_Data/{aq_name}_{DATA_RANGE_LIST[0]}_{int(QUANTILE_LIST[1] * 100)}.xlsx'
            if os.path.exists(path):               
                with pd.ExcelWriter(path, mode='a') as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)                  
            else:
                with pd.ExcelWriter(path) as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)  
                    
        elif i // step == 2: # 9-12
            path = f'Prelim_Data/{aq_name}_{DATA_RANGE_LIST[1]}_{int(QUANTILE_LIST[0] * 100)}.xlsx'
            if os.path.exists(path):               
                with pd.ExcelWriter(path, mode='a') as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)                  
            else:
                with pd.ExcelWriter(path) as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)  
                    
        else: # 13-16
            path = f'Prelim_Data/{aq_name}_{DATA_RANGE_LIST[1]}_{int(QUANTILE_LIST[1] * 100)}.xlsx'
            if os.path.exists(path):               
                with pd.ExcelWriter(path, mode='a') as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)                  
            else:
                with pd.ExcelWriter(path) as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)    


def save_plot_as_image(img_path: str, overwrite: bool=False):
    """Saves a generated plot as an image to the specified img_path"""
    
    if os.path.exists(img_path) and overwrite:
        plt.savefig(img_path)
    elif not os.path.exists(img_path):
        plt.savefig(img_path)
        

def single_site_report(df_single_site: pd.DataFrame):
    """Produces console report for single_site_data()"""
    print(f'Site No: {df_single_site["site_no"]}')
    print(f'Analyzed Range: {df_single_site["analyze_range"].to_string(index=False)}')
    print(f'Quantile: {df_single_site["quantile"].to_string(index=False)}')
    print(f'Valid: {df_single_site["valid"].to_string(index=False)}')
    print(f'% Missing: {df_single_site["missing"].to_string(index=False)}')
    print(f'90%: {df_single_site["threshold"].to_string(index=False)}')
    print(f'HMF Years: {df_single_site["hmf_years"].to_string(index=False)}')
    print(f'Annual Duration: {df_single_site["annual_duration"].to_string(index=False)}')
    print(f'Event Duration: {df_single_site["event_duration"].to_string(index=False)}')
    print(f'Event HMF: {df_single_site["event_hmf"].to_string(index=False)}')
    print(f'Inter-annual Frequency: {df_single_site["inter_annual"].to_string(index=False)}%')
    print(f'Intra-annual Frequency: {df_single_site["intra_annual"].to_string(index=False)}')
    print(f'Total HMF in km^3/year: {df_single_site["annual_hmf"].to_string(index=False)}')
    print(f'Center of Mass: {df_single_site["timing"].to_string(index=False)}')
    print(f'6 Month HMF in km^3/year: {df_single_site["six_mo_hmf"].to_string(index=False)}')
    print(f'3 Month HMF in km^3/year: {df_single_site["three_mo_hmf"].to_string(index=False)}')
    
#-----------------------------------#
#-------# PLOTTING FUNCTIONS #------#
#-----------------------------------#

def plot_lower_48(ax: plt.Axes, shapefile_path: str, crs: int=4269):
    """Plots a simple basemap of the lower 48 with state boundaries"""
    lower48 = gpd.read_file(shapefile_path)
    
    non_contiguous = ['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP']
    for reg in non_contiguous:
        lower48 = lower48[lower48['STUSPS'] != reg]
        
    lower48 = lower48.to_crs(epsg=crs)
    lower48.plot(ax=ax, edgecolor='grey', facecolor='darkgrey', linewidth=0.75)  
    
def plot_basemap(ax: plt.Axes, crs: int=4269, source: cx.providers=cx.providers.OpenStreetMap.Mapnik, zoom: int=7):
    """Plots a contexily basemap"""
    ax.margins(0, tight=True)
    ax.set_axis_off()
    cx.add_basemap(ax, crs=crs, source=source, zoom=zoom)
    
def convert_geometry(df: pd.DataFrame):
    """Converts 'dec_lat/long_va' columns to geopandas dataframe"""
    lat = df['dec_lat_va']
    long = df['dec_long_va']
    geometry = geometry = [Point(xy) for xy in zip(long, lat)]
    geo_df = gpd.GeoDataFrame(geometry=geometry)
    return geo_df

def scale_colorbar(df: pd.DataFrame, metric: str):
    """Set colorbar scale format based on min/max of metric being plotted"""
    vmin = df[metric].min()
    vmax = df[metric].max()        
    norm = mcolors.Normalize(vmin, vmax)
    cmap = 'plasma'
    mappable = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    mappable.set_array(df[metric])    
    return cmap, mappable
    