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

from datetime import datetime, timedelta
from itertools import chain

#--------------------------#
#-------# CONSTANTS #------#
#--------------------------#

# Data Retrieval Tool Constants
SERVICE = 'dv'
STATE_CODE = 'CA'
PARAM_CODE = '00060'
TIDAL_CODE = '72137'
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

# Conversion Rates
SEC_PER_DAY = 86400
CUBIC_FT_KM_FACTOR = 0.0000000000283168466
CUBIC_KM_MAF_FACTOR = 0.8107132

# Excludes Alaska and Hawaii
STATE_LIST = ['AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

# Sites with additional tidally filtered streamflow data
# UNUSED
'''TIDAL_SITES = ['02378185', '0237854520', '02470629', '02471019', '11304810', '11311300', '11312672', '11312676', '11312685', '11312968', '11313240', '11313315', '11313405', '11313431', '11313433', '11313434', '11313440', '11313452', '11313460', '11336600', '11336685', '11336790', '11336930', '11336955', '11337080', '11337190', '11447650', '11447830', '11447850', '11447890', '11447903', '11447905', '11455140', '11455315', '11455338', '11455420', '01193050', '01208760', 
               '01482100', '01482695', '01484080', '02246459', '02246518', '022908205', '02290878', '02290888', '02290918', '022929176', '02293055', '02293090', '02300082', '02301718', '02304510', '02310308', '02310650', '02310663', '02310688', '02310689', '02310700', '02310740', '02310743', '02310750', '02324170', '02326050', '02326550', '02327031', '250802081035500', '251115081075800', '251549080251200', '252230081021300', '252551081050900', '253047080555600', '255327081275900', 
               '255432081303900', '255534081324000', '295308085143700', '295323085151700', '01410500', '01467024', '01467200', '01482100', '01311875', '14246900', '01467200', '02110701', '02110704', '02135200', '02171700', '02172040', '021720677', '021720698', '08041780', '08042558', '08067250', '08072050', '08117705', '08162501', '12113390', '14246900']'''

OUTLET_GAUGES = {
    'pn_outlet_gages': ['12200500', '12040500', '14211720', '14372300'], #'11039800' -- invalid
    'sr_outlet_gages': ['13269000'],
    'cv_outlet_gages': ['11303500', '11447650'],
    'cc_outlet_gages': ['11023000', '11046000', '11078000', '11087020', '11133000', '11140000', '11152500', '11159000', '11467000', '11477000', '11530500', '11532500'],    
    'br_outlet_gages': ['09520500', '09429600', '09521100', '09519800', '09468500', '09423000', '10327500', '10351650', '10351650', '10311400'],
    'hp_outlet_gages': ['08123800', '08121000', '07297910', '07228000', '07234000', '07157500', '07144550', '06853500', '06805500', '06799500', '06465500'],
    'mr_outlet_gages': ['07077000', '07077555', '07047942', '07369000', '07369000', '07285500', '07268000'],
    'cl_outlet_gages': ['08211000', '08188500', '08176500', '08164000', '08162000', '08116650', '08066500', '08033500', '08068000', '08030500', '08013500', '08012000', '07378500', '02492000', '02489500', '02479000', '02479300', '02469761', '02428400', '02375500'],
    'na_outlet_gages': ['02105769', '02089500', '02091500', '02083500', '02085000', '02052000', '02047000', '02049500', '02041650', '02037500', '01668000', '01673000', '01646500', '01578310', '01474500', '01463500'],
    'fl_outlet_gages': ['02368000', '02365500', '02358000', '02320500', '02313230'],
}

OUTLET_GAUGES_NOMEN = {
    'pn_outlet_gages': 'Pacific Northwestern',
    'sr_outlet_gages': 'Snake River',
    'cv_outlet_gages': 'Central Valley',
    'cc_outlet_gages': 'California Coastal',    
    'br_outlet_gages': 'Basin and Range',
    'hp_outlet_gages': 'High Plains',
    'mr_outlet_gages': 'Miss. River Alluvial',    
    'cl_outlet_gages': 'Coastal Lowlands',
    'na_outlet_gages': 'Northern Atlantic',
    'fl_outlet_gages': 'Floridian',
}

# Metric Units for plot labels
# $\mathregular{km^3}$/year
FLOW_METRIC_UNITS = {
    'annual_hmf': 'Annual HMF ($\mathregular{km^3}$)', 
    'event_duration': 'Average Days per HMF Event', 
    'annual_duration': 'Average HMF Days per Year', 
    'event_hmf': 'Average HMF ($\mathregular{km^3}$/event)', 
    'timing': 'Timing (DOHY)', 
    'six_mo_hmf': 'Average HMF ($\mathregular{km^3}$/3 months)', 
    'three_mo_hmf': 'Average HMF ($\mathregular{km^3}$/6 months)', 
    'inter_annual%': 'Annual Freqency of Events (%)', 
    'intra_annual': 'Average Events per Year'
}

WATER_QUALITY_PCODES = {
    "00090": "ORP, (mV)",
    "63001": "ORP, (mV), raw emf",
    "63002": "ORP, (mV), relative to standard hydrogen electrode (SHE)",
    "00300": "DO, (mg/l), unfiltered water",
    "00301": "DO, (% saturation), unfiltered water",
    "62971": "DO, (mg/l), lab sample",
    "72210": "DO, (% saturation), mid-depth of water column",
    "85550": "DO, (oxygen % of gasses)",
    "85573": "DO, (cm3/g), at STP",
    "90300": "DO, (mg/l), area weighted average",
    "63737": "DOC, (% hydrofilic fraction of organic carbon), filtered water",
    "63738": "DOC, (% hydrofilic fraction of organic carbon), filtered water",
    "63739": "DOC, (% transphilic fraction of organic carbon)",
    "99134": "DOC, (mg/l), in situ concentration computed by regression of sensor data/field sample",
    "01044": "Fe, (ug/l), suspended sediment, recoverable",
    "01045": "Fe, (ug/l), recoverable, unfiltered water",
    "01046": "Fe, (ug/l), filtered water",
    "01047": "Fe2, (ug/l)",
    "01048": "Fe2+Fe3, (ug/l)",
    "01053": "Mn, (mg/kg), bed sediment",
    "01054": "Mn, (ug/l), suspended sediment, recoverable",
    "01055": "Mn, (ug/l), unfiltered water, recoverable",
    "01056": "Mn, (ug/l), filtered water",
    "01123": "Mn, (ug/l), unfiltered water, recoverable",
    "01248": "Mn, (ug/kg), soluble dry atmospheric deposition",
    "01249": "Mn, (ug/kg), insoluble dry atmospheric deposition",
    "01250": "Mn, (ug/kg), total dry atmospheric deposition",
    "00940": "Cloride, (mg/L), filtered water",
    "49482": "Cl-36, (pCi/L), unfiltered water",
    "50060": "Cl, (mg/l), total residual, unfiltered water",
    "50064": "Cl, (mg/l), free available, unfiltered water",
    "50066": "Cl, (mg/l), combined available, unfiltered water",
    "00945": "Sulfate, (mg/l), filtered water",
    "00946": "Sulfate, (mg/l), unfiltered water",
    "00618": "Nitrate, (mg/l as N), filtered water",
    "00620": "Nitrate, (mg/l as N), unfiltered water",
    "00631": "Nitrate plus nitrite (mg/l as N), water, filtered",
    "71851": "Nitrate (mg/l as NO3), water, filtered",
    "00665": "Phosphorus (mg/L as PO4), unfiltered water",
    "00650": "Phosphate, (mg/l as PO4)",
    "00653": "Phosphate, (mg/l as PO4)",
    "00600": "Orthophosphate, (mg/L as PO4), water, filtered",
    "00671": "Orthophosphate, (mg/L as P), water, filtered",
    "71846": "Ammonia (NH3 + NH4+), (mg/L as NH4), water, filtered",
    "00608": "Ammonia (NH3 + NH4+), (mg/L as N), water, filtered",
    "00425": "Bicarbonate, (mgl/l as CaCO3), unfiltered water",
    "00915": "Ca, (mg/l), dissolved filtered water",
    "00916": "Ca, (mg/l), unfiltered water, recoverable",
    "00918": "Ca, (mg/l), unfiltered water, recoverable",
    "00920": "Mg, (mg/l as CaCO3?), unfiltered water",
    "00921": "Mg, (mg/l), unfiltered water, recoverable",
    "00925": "Mg, (mg/l), filtered water",
    "00926": "Mg, (mg/l), suspended sediment total",
    "00927": "Mg, (mg/l), unfiltered water, recoverable",
    "00923": "Na, (mg/l), unfiltered water, recoverable",
    "00929": "Na, (mg/l), unfiltered water, recoverable",
    "00930": "Na, (mg/l), filtered water",
    "00931": "Na, Sodium absorption ratio (SAR)",
    "00932": "Na, (% total cations), sodium fraction of cations percent in equivalents of major cations",
    "00935": "K, (mg/l), filtered water",
    "00937": "K, (mg/l), unfiltered water, recoverable",
    "00939": "K, (mg/l), unfiltered water, recoverable",
    "52281": "K, (ug/l?), unfiltered water, [text says milligrams per liter, unit says ug/l]",
    "52291": "K, (mg/l), unfiltered water",
    "00954": "Silica, (ug/l), unfiltered water, recoverable, per liter as SiO2",
    "00955": "Silica, (ug/l), filtered water, per liter as SiO2",
    "00956": "Silica, (ug/l), unfiltered water, per liter as SiO2",
    "00418": "Alkalinity, (mg/l as CaCO3), fixed endpoint (pH 4.5), field titration",
    "00421": "Alkalinity, (mg/l as CaCO3), fixed endpoint (pH 4.5), lab titration",
    "29801": "Alkalinity, (mg/l as CaCO3), fixed endpoint (pH 4.5), lab titration",
    "29802": "Alkalinity, (mg/l as CaCO3), Gran field titration",
    "29803": "Alkalinity, (mg/l as CaCO3), Gran lab titration",
    "00191": "Hydrogen ion, (mg/L), water, unfiltered, calculated",
    "00400": "pH, water, unfiltered, field, standard units",
    "00403": "pH, water, unfiltered, laboratory, standard units",
    "00434": "pH, (standard units), adjusted to 25 degrees Celsius",
    "00010": "Temp, (deg C), water",
    "00011": "Temp, (deg F)",
    "80154": "Suspended sediment concentration (mg/L)",
    "00070": "Turbidity, (JTU), unfiltered water",
    "00075": "Turbidity, (mg/l as SiO2), unfiltered water, Hellige turbidimeter",
    "61028": "Turbidity, (NTU), unfiltered water, nephelometric turbidity units",
    "70303": "Dissolved solids, (short tons per acre-foot), water, filtered",
    "72395": "Turbidity, (FNU), mean storm event, composite samples",
    "80155": "Suspended sediment discharge, short tons per day",
    "00095": "Specific conductance, (uS at 25 deg C) water, unfiltered"
}

# For use in pd.read_excel() to enforce leading 0's
DATASET_DTYPES = {'site_no': str, 'huc2_code': str, 'huc4_code': str, 'within_aq': str}

#-----------------------------------#
#-------# ANALYSIS FUNCTIONS #------#
#-----------------------------------#

def merge_tidal(df_combined):
    """This function merges, if necessary, tidal data with streamflow data returning a dataframe
       with only the necessary columns for analysis. If no data is present, an empty dataframe is returned."""
    keep_cols = ['datetime', '00060_Mean', 'site_no']
    
    # If we have both stream and tidal data, merge them, prioritizing tidal data, and rename the column to '00060_Mean'
    if '72137_Mean' in df_combined.columns and '00060_Mean' in df_combined.columns:
        df_combined['00060_Mean'] = df_combined['72137_Mean'].combine_first(df_combined['00060_Mean'])
        df_combined = df_combined.drop(columns=[col for col in df_combined.columns if col not in keep_cols])
        return df_combined
    
    # If we only have stream data use it as is, drop any unnecessary columns
    if '00060_Mean' in df_combined.columns:
        df_combined = df_combined.drop(columns=[col for col in df_combined.columns if col not in keep_cols])
        return df_combined
    
    # If we only have tidal data we'll rename it to stream data and use it as is
    if '72137_Mean' in df_combined.columns:
        df_combined.rename(columns={'72137_Mean': '00060_Mean'}, inplace=True)
        df_combined = df_combined.drop(columns=[col for col in df_combined.columns if col not in keep_cols])
        return df_combined
    
    # Catch-all
    return df_combined

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

def num_hmf_years(df: pd.DataFrame):
    df_temp = df.copy()
    """Returns the integer number of HMF years"""
    '''df.loc[:, 'datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)    
    df.loc[:, 'offsetdate'] = (df.index - pd.offsets.YearBegin(month=offset))'''    
    df_temp['datetime'] = df_temp['datetime'] + pd.DateOffset(months=-9)     
    return df_temp['datetime'].dt.year.nunique()

def three_six_range(df: pd.DataFrame, three_start: int, three_end: int, six_start: int, six_end: int):
    """Returns two dataframes, one with a six month period, and one with a three month period, based on given start and end months for both"""
    df_temp = df.reset_index()
    df_temp.loc[:, 'datetime'] = pd.to_datetime(df_temp['datetime'])    
    six_month_mask = (df_temp['datetime'].dt.month >= six_start) | (df_temp['datetime'].dt.month <= six_end)
    three_month_mask = (df_temp['datetime'].dt.month >= three_start) | (df_temp['datetime'].dt.month <= three_end)
    return df_temp[six_month_mask], df_temp[three_month_mask]

def calc_inter_annual(df: pd.DataFrame, hmf_years: int):
    """Returns the frequency with which years experience at least one HMF event as well as the analyzed range"""    
    # TODO: Discuss w/KO on how we want to handle partial years. If a partial year at start/end has HMF, we can count it as a full year, however if it doesn't,
    # this current method will still count it as a full year in delta, when we don't know if there was or was not flow in the missing portions. This potentially
    # skews the frequency by 1/30th or 1/50th and so may not be worth worrying about. Solutions would involve checking the first/last year for HMF and adjusting delta
    df_inter = df.reset_index()
    df_inter['datetime'] = df_inter['datetime'] + pd.DateOffset(months=-9)
    delta = df_inter['datetime'].dt.year.nunique()
    inter_annual = hmf_years / delta
    inter_annual = min((round(inter_annual, 5) * 100), 100)
    return inter_annual, delta

def calc_duration_intra_annual(df: pd.DataFrame, hmf_years: int):
    """Calculates the average duration of HMF events per year and the intra-annual frequency of events
       per year. Also returns a results dataframe for use in the duration and intra-annual MK tests"""
    df_d = df.reset_index()
    df_results = pd.DataFrame()
    df_d['datetime'] = df_d['datetime'] + pd.DateOffset(months=-9)

    # Create a binary column for HMF events
    df_d['flow_bool'] = df_d['00060_Mean'].apply(lambda x: 1 if x > 0 else 0)    

    # Average HMF/year calculation
    df_results = df_d.groupby(df_d["datetime"].dt.year)["00060_Mean"].sum().reset_index()
    df_results["00060_Mean"] = df_results["00060_Mean"] * CUBIC_FT_KM_FACTOR

    # Total days per year calculation
    df_results["total_days"] = df_d.groupby(df_d["datetime"].dt.year)["flow_bool"].sum().reset_index()["flow_bool"]

    # Total events per year calculation
    # Insert a day at the very beginning of the dataframe with flow_bool == 0 so that the first event is counted via diff()
    first = df_d['datetime'].iloc[0] - timedelta(days=1)
    insert = {'datetime': first, '00060_Mean': 0,  '00060_Mean_cd': None, 'site_no': None, 'flow_bool': 0}
    df_d = pd.concat([pd.DataFrame(insert, index=[0]), df_d]).reset_index(drop=True)

    # Total events per year calculation
    df_d['Year'] = df_d['datetime'].dt.year
    df_d['Change'] = df_d['flow_bool'].diff()
    df_d['Year_Change'] = df_d['Year'].diff()
    
    # Edgecase where flow carries over from previous year
    df_d.loc[((df_d['Year_Change'] > 0) & (df_d['flow_bool'] == 1)), 'Change'] = 1
    
    '''# Set Change == 1 if the first day of the year has an event to account for events spanning the new year
    year_start_mask = (df_d['datetime'].dt.month == 1) & (df_d['datetime'].dt.day == 1)
    df_d.loc[year_start_mask & (df_d['flow_bool'] == 1), 'Change'] = 1'''
    
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
    
    return timing, com_series
    
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

#-------------------------------#
#-------# MISC FUNCTIONS #------#
#-------------------------------#

def merge_mk_results(df_mk_complete: pd.DataFrame, df_mk_metric: pd.DataFrame, site_no: str, date_range: float, quantile: float):
    """Merges the per date/quantile site Mann-Kendall results with the others for splitting into datasets"""
    df_mk_metric.insert(0, 'dataset_ID', date_range * quantile)
    df_mk_metric.insert(1, 'site_no', site_no)    
    return pd.concat([df_mk_complete.reset_index(drop=True), df_mk_metric.reset_index(drop=True)], axis=0)

def save_data(df_site_metrics: pd.DataFrame, df_mk_magnitude: pd.DataFrame, df_mk_duration: pd.DataFrame, df_mk_intra_annual: pd.DataFrame,
              df_mk_event_mag: pd.DataFrame, df_mk_event_dur: pd.DataFrame, df_mk_timing: pd.DataFrame, aq_name: str):
    """Splits the resulting 'aquifer_sites' dataframe into individual frames and saves them as CSV's into Prelim_Data"""
    
    dataframes = [df_site_metrics, df_mk_magnitude, df_mk_duration, df_mk_intra_annual, df_mk_event_mag, df_mk_event_dur, df_mk_timing]
    sheet_names = ['site_metrics', 'mk_magnitude', 'mk_duration', 'mk_intra_annual', 'mk_event_mag', 'mk_event_dur', 'mk_timing']
    step = len(dataframes)
    passes = len(QUANTILE_LIST) * len(DATA_RANGE_LIST)
    
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
    order_key = [i + j for j in range(passes) for i in range(0, len(df_master_list), passes)]
    df_master_list = [df_master_list[i] for i in order_key]        
    
    # Step through the master list, adding the first 4 dataframes to the first spreadsheet, the second four to the second, and so on        
    for i, df in enumerate(df_master_list):
        if i // step == 0: # First 7 dataframes
            path = f'Prelim_Data/{aq_name}_{DATA_RANGE_LIST[0]}_{int(QUANTILE_LIST[0] * 100)}.xlsx'
            if os.path.exists(path):               
                with pd.ExcelWriter(path, mode='a') as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)                  
            else:
                with pd.ExcelWriter(path) as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)
                                        
        elif i // step == 1:
            path = f'Prelim_Data/{aq_name}_{DATA_RANGE_LIST[0]}_{int(QUANTILE_LIST[1] * 100)}.xlsx'
            if os.path.exists(path):               
                with pd.ExcelWriter(path, mode='a') as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)                  
            else:
                with pd.ExcelWriter(path) as writer:
                    df.to_excel(writer, sheet_name=sheet_names[i % step], index=False)  
                    
        elif i // step == 2:
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
    print(f'% Missing: {df_single_site["missing_data%"].to_string(index=False)}')
    print(f'90%: {df_single_site["threshold"].to_string(index=False)}')
    print(f'HMF Years: {df_single_site["hmf_years"].to_string(index=False)}')
    print(f'Annual Duration: {df_single_site["annual_duration"].to_string(index=False)}')
    print(f'Event Duration: {df_single_site["event_duration"].to_string(index=False)}')
    print(f'Event HMF: {df_single_site["event_hmf"].to_string(index=False)}')
    print(f'Inter-annual Frequency: {df_single_site["inter_annual%"].to_string(index=False)}%')
    print(f'Intra-annual Frequency: {df_single_site["intra_annual"].to_string(index=False)}')
    print(f'Total HMF in km^3/year: {df_single_site["annual_hmf"].to_string(index=False)}')
    print(f'Center of Mass: {df_single_site["timing"].to_string(index=False)}')
    print(f'6 Month HMF in km^3/year: {df_single_site["six_mo_hmf"].to_string(index=False)}')
    print(f'3 Month HMF in km^3/year: {df_single_site["three_mo_hmf"].to_string(index=False)}')
    
#-----------------------------------#
#-------# PLOTTING FUNCTIONS #------#
#-----------------------------------#

def plot_lower_48(ax: plt.Axes, crs: int=4269, facecolor: str='grey', edgecolor: str='darkgrey', linewidth: float=0.75, alpha: float=1.0, zorder: int=1):
    """Plots a simple basemap of the lower 48 with state boundaries"""
    lower48 = gpd.read_file('ShapeFiles/Lower48/lower48.shp')        
    lower48 = lower48.to_crs(crs)
    lower48.plot(ax=ax, edgecolor=edgecolor, facecolor=facecolor, linewidth=linewidth, alpha=alpha, zorder=zorder) 
    
def plot_stream_network(stream_network_shapefile, ax: plt.Axes, crs: int=4269, color: str='blue', linewidth: float=0.75, alpha: float=0.30, zorder: int=1):
    """Plots a nationwide stream network"""
    stream_network = stream_network_shapefile.to_crs(crs)
    stream_network.plot(ax=ax, color=color, linewidth=linewidth, alpha=alpha, zorder=zorder)     
    
def plot_basemap(ax: plt.Axes, crs: int=4269, source: cx.providers=cx.providers.OpenStreetMap.Mapnik, zoom: int=7):
    """Plots a contexily basemap"""
    ax.margins(0, tight=True)
    ax.set_axis_off()
    cx.add_basemap(ax, crs=crs, source=source, zoom=zoom)
    
def convert_geometry(df: pd.DataFrame):
    """Converts 'dec_lat/long_va' columns to geopandas dataframe"""
    lat = df['dec_lat_va']
    long = df['dec_long_va']
    geometry = [Point(xy) for xy in zip(long, lat)]
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

def plot_rateb_aquifers(ax, crs: int=4269, edgecolor: str='orange', facecolor: str='none', alpha: float=0.75, linewidth: float=1.00):
    """Plots the aquifer outlines as used by Rateb et al. 2020"""
    rateb_aqs = gpd.read_file('ShapeFiles/Lower48/POWELL_AQs_2020.shp')
    rateb_aqs = rateb_aqs.to_crs(crs)
    rateb_aqs.plot(ax=ax, edgecolor=edgecolor, facecolor=facecolor, alpha=alpha, linewidth=linewidth)
    
def plot_huc2(ax, shapefile, codes: list=[], crs: int=4269, edgecolor: str='royalblue', facecolor: str='cornflowerblue', alpha: float=0.30, linewidth: float=1.00):
    """Plots HUC2 shapefiles either by a list of codes or all HUC2's if no list is provided"""
    if codes == [-1]: return
    # If no list is provided, plot all HUC2's
    shapefile = shapefile.to_crs(crs)
    if not codes:        
        shapefile.plot(ax=ax, edgecolor=edgecolor, facecolor=facecolor, alpha=alpha, linewidth=linewidth)       
    else:
        shapefile = shapefile[shapefile['huc2_code'].isin(codes)]
        shapefile.plot(ax=ax, edgecolor=edgecolor, facecolor=facecolor, alpha=alpha, linewidth=linewidth) 
                        
def plot_huc4(ax, shapefile, codes: list=[], crs: int=4269, edgecolor: str='royalblue', facecolor: str='cornflowerblue', alpha: float=0.30, linewidth: float=1.00):
    """Plots HUC4 shapefiles either by a list of codes or all HUC2's if no list is provided"""
    if codes == [-1]: return
    # If no list is provided, plot all HUC4's
    shapefile = shapefile.to_crs(crs)
    if not codes:        
        shapefile.plot(ax=ax, edgecolor=edgecolor, facecolor=facecolor, alpha=alpha, linewidth=linewidth)       
    else:
        shapefile = shapefile[shapefile['huc4_code'].isin(codes)]
        shapefile.plot(ax=ax, edgecolor=edgecolor, facecolor=facecolor, alpha=alpha, linewidth=linewidth)
        
def set_plot_bounds(shapefile, padding: float=3.0):
    """Sets the plot bounds for single aquifer plotting"""
    xmin, ymin, xmax, ymax = shapefile.total_bounds
    padding = padding
    xmin -= padding
    ymin -= padding
    xmax += padding
    ymax += padding
    return xmin, xmax, ymin, ymax 
