# This contains retired code that is no longer used in the project but is kept for reference purposes

# Aquifer Data Generation by Aquifer
'''
# Set the aquifer to collect data for
curr_aquifer = cl.arizona_alluvial_aquifer

# Limit saved sites for testing purposes
# Set to >=999 to analyze all sites
site_limit = 999

# Data Creation
df_aq_sites_metric = pd.DataFrame()
df_aq_sites_mk_mag = pd.DataFrame()
df_aq_sites_mk_dur = pd.DataFrame()
df_aq_sites_mk_intra = pd.DataFrame()
master_blacklist = []

outer = "outer"
for root, dirs, files in os.walk(curr_aquifer.wb_dir):
    #print(root, dirs, files)
    if os.path.basename(root).startswith('NHD_H_'):
        if curr_aquifer.wb_shapefiles in files:
            shapefile_aq_path = os.path.join(root, curr_aquifer.wb_shapefiles)
            ws_gdf = gpd.read_file(shapefile_aq_path)
            ws_gdf = ws_gdf.to_crs(4269)           
            print("Path: ", shapefile_aq_path)
            
            for state_code in curr_aquifer.states:
                print("Trying: ", state_code)
                try:
                    state_uri = fn.create_state_uri(state_code, fn.PARAM_CODE)
                    df_state_sites = filter_state_site(shapefile_aq_path, state_uri)
                    df_temp_metric, df_temp_mk_mag, df_temp_mk_dur, df_temp_mk_intra, blacklist = create_multi_site_data(df_state_sites, site_limit, curr_aquifer)
                    master_blacklist.extend(blacklist)
                    df_temp_metric['State'] = state_code
                    df_aq_sites_metric = pd.concat([df_aq_sites_metric, df_temp_metric], axis=0, ignore_index=True).reset_index(drop=True)
                    df_aq_sites_mk_mag = pd.concat([df_aq_sites_mk_mag, df_temp_mk_mag], axis=0, ignore_index=True).reset_index(drop=True)
                    df_aq_sites_mk_dur = pd.concat([df_aq_sites_mk_dur, df_temp_mk_dur], axis=0, ignore_index=True).reset_index(drop=True)
                    df_aq_sites_mk_intra = pd.concat([df_aq_sites_mk_intra, df_temp_mk_intra], axis=0, ignore_index=True).reset_index(drop=True)                    
                     
                except Exception as e:
                    print("ERROR: ", e)
                    print(state_uri)

# Filtering out invalid sites by data range and duplicates as some sites are listed in 2+ states   
# Also adds a column to indicate presence in HCDN-2009
#df_aq_sites = df_aq_sites.drop_duplicates(subset=['site_no'])
df_aq_sites_metric = fn.gages_2_filtering(df_aq_sites_metric)

try:
    with open(f'Prelim_Data/{curr_aquifer.name}_Blacklist.txt', 'w') as f:
        master_blacklist = ["'" + str(x) + "'" for x in master_blacklist]        
        f.write(', '.join(master_blacklist))
except Exception as e:
    print(e)
    
#df_aq_sites_metric.to_csv(f'{curr_aquifer.name}_Raw.csv') 

fn.save_data(df_aq_sites_metric, df_aq_sites_mk_mag, df_aq_sites_mk_dur, df_aq_sites_mk_intra, curr_aquifer.name)  
#print(df_aq_sites)
'''

#####################################################################################################################

# Old multi-site data creation function used by per aquifer data generation function
'''
# REQUIRES: 'df_state_sites' from 'Multi-Site Filtering'
# Used for now to limit runtime when running independently
site_limit = 3

def create_multi_site_data(df_state_sites: pd.DataFrame, site_limit: int, aquifer: cl.Aquifer):
	"""Generates detailed HMF, MK, and POS information for each site in the passed dataframe"""
	# Necessary for proper iterrows() behavior
	df_state_sites.reset_index(drop=True, inplace=True)

	# Creating the dataframe that will hold final results for mapping
	df_multi_site_metric = pd.DataFrame()
	df_multi_site_mk_mag = pd.DataFrame()
	df_multi_site_mk_dur = pd.DataFrame()
	df_multi_site_mk_intra = pd.DataFrame()
 
	site_blacklist = []

	for index, row in df_state_sites.iterrows():
		while index < site_limit:
      
			if str(row['site_no']) in aquifer.blacklist:
				print(f'IGNORED: Site {row["site_no"]} is in aquifer blacklist')
				break
			
			# Create a dataframe for the current site in the iteration to perform calculations on
			df = nwis.get_record(sites=row['site_no'], service=fn.SERVICE, parameterCD=fn.PARAM_CODE, start=fn.DEFAULT_START, end=fn.DEFAULT_END)
			df = df.reset_index()
			
			# Confirm that dataframe is not empty and has the required streamflow data before continuing
			if df.empty:
				site_blacklist.append(row['site_no'])
				print(f'IGNORED: No data for site {row["site_no"]}')
				break

			if '00060_Mean' not in df.columns:
				site_blacklist.append(row['site_no'])
				print(f'IGNORED: No 00060_Mean data for site {row["site_no"]}')
				break
			
			# Filter out sites with less than the minimum required range of data
			start = df['datetime'].min().date()
			end = df['datetime'].max().date()
			range = round((end - start).days / 365.25, 1)
			
			# Ignore sites with less than the minimum required years of data
			if range < fn.MIN_DATA_PERIOD:
				site_blacklist.append(row['site_no'])
				print(f'IGNORED: Not enough data for site {row["site_no"]}')
				break			
				
			df_single_site_metric, df_mk_mag, df_mk_dur, df_mk_intra = single_site_data(df, fn.QUANTILE_LIST, fn.DATA_RANGE_LIST)			
			
			# Append positional data to dataframe created by single_site_data()
			add_data = {'dec_lat_va': row['dec_lat_va'], 'dec_long_va': row['dec_long_va'], 'data_start': start, 'data_end': end, 'total_record': range}			
			add_data = pd.DataFrame(add_data, index=['0'])
   
			# Duplicates the rows of add_data so that positional information is passed to each individual dataframe when this frame is split
			add_data = pd.DataFrame(np.tile(add_data.values, (len(df_single_site_metric), 1)), columns=add_data.columns)
			df_single_site_metric = pd.concat([df_single_site_metric.reset_index(drop=True), add_data.reset_index(drop=True)], axis=1)

			# Append single site data to multi-site dataframes
			df_multi_site_metric = pd.concat([df_multi_site_metric, df_single_site_metric], ignore_index=True)
			df_multi_site_mk_mag = pd.concat([df_multi_site_mk_mag, df_mk_mag], ignore_index=True)
			df_multi_site_mk_dur = pd.concat([df_multi_site_mk_dur, df_mk_dur], ignore_index=True)
			df_multi_site_mk_intra = pd.concat([df_multi_site_mk_intra, df_mk_intra], ignore_index=True)   
   		
			print(f'Added site {index + 1} of {len(df_state_sites)}')
			
			#clear_output(wait=True)
			#time.sleep(0.500)
			break

	return df_multi_site_metric, df_multi_site_mk_mag, df_multi_site_mk_dur, df_multi_site_mk_intra, site_blacklist


df_multi_site_metric, df_multi_site_mk_mag, df_multi_site_mk_dur, df_multi_site_mk_intra, site_blacklist = create_multi_site_data(df_state_sites, site_limit, cl.central_valley_aquifer)
df_multi_site, df_invalid_site = fn.filter_by_valid(df_multi_site_metric)
#df_multi_site.to_csv('df_multi_site.csv')
#print(df_multi_site)

print(f'Max HMF for this region: {df_multi_site["annual_hmf"].max():.1f}')
print(f'{len(df_multi_site)} site(s) valid out of {len(df_multi_site_metric)}')
'''

#####################################################################################################################