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

'''

'''