# Streamgauge class used solely for early testing
class StreamGauge:
    def __init__(self, id, name, mean_start_date, mean_end_date, post_start_date, post_end_date):
        self.id = id
        self.name = name
        # Start date for all-time mean daily flow data
        self.mean_start_date = mean_start_date
        self.mean_end_date = mean_end_date
        # Start date for post-impairment mean daily flow data
        self.post_start_date = post_start_date
        self.post_end_date = post_end_date 
        
# Stream Guages for testing against Kocis 2017 and data validation     
SRB_Guage = StreamGauge('11447650', 'SACRAMENTO R A FREEPORT CA', '1948-10-01', '2014-09-30', '1970-10-01', '2014-09-30')
SJTB_Guage = StreamGauge('11303500', 'SAN JOAQUIN R NR VERNALIS CA', '1923-10-01', '2014-09-30', '1989-10-01', '2014-09-30')
        
# Aquifer class used for aquifer analysis
class Aquifer():
    def __init__(self, name, datasets_dir, wb_dir, wb_shapefiles, aq_shapefile, states):
        self.name = name # Aquifer name
        self.datasets_dir = datasets_dir    
        self.wb_dir = wb_dir # Path to aquifer watershed boundary shapefiles
        self.wb_shapefiles = wb_shapefiles # Name of watershed boundary shapefiles to loop through
        self.aq_shapefile = aq_shapefile # Path to aquifer shapefile
        self.states = states # List of states aquifer overlays 

# Aquifer Definitions for Aquifer Analysis
# Upper Clairbrone alluvial aquifer in south-central US    
upper_clairborne_aquifer = Aquifer(
    name = 'Upper_Clairborne',
    datasets_dir = "Prelim_Data/Upper_Clairborne",
    wb_dir = 'ShapeFiles/Aquifers/Upper_Clairborne_MS/HUC4',
    wb_shapefiles = 'WBDHU4.shp',
    aq_shapefile = 'ShapeFiles/Aquifers/Upper_Clairborne_MS/sir2008-5098_UCAQ_extent.shp',
    states = ['AR', 'LA', 'MS', 'TN', 'KY', 'MO', 'AL']
)

# Central Valley aquifer in California's Central Valley
central_valley_aquifer = Aquifer(
    name = 'Central_Valley',
    datasets_dir = "Prelim_Data/Central_Valley",
    wb_dir = 'ShapeFiles/Aquifers/Central_Valley/HUC4',
    wb_shapefiles = 'WBDHU4.shp',
    aq_shapefile = 'ShapeFiles/Aquifers/Central_Valley/Alluvial_Bnd.shp',
    states = ['CA', 'OR']
)  

# Lake Michigan Basin in Michigan
michigan_basin_aquifer = Aquifer(
    name = 'Michigan_Basin',
    datasets_dir = "Prelim_Data/Michigan_Basin",
    wb_dir = 'ShapeFiles/Aquifers/Michigan_Basin/HUC4',
    wb_shapefiles = 'WBDHU4.shp',
    aq_shapefile = 'ShapeFiles/Aquifers/Michigan_Basin/sir2009-5060_unit_alt_grid.shp',
    states = ['MI']
)

columbia_plateau_aquifer = Aquifer(
    name = 'Columbia_Plateau',
    datasets_dir = "Prelim_Data/Columbia_Plateau",
    wb_dir = 'ShapeFiles/Aquifers/Columbia_Plateau/HUC4',
    wb_shapefiles = 'WBDHU4.shp',
    aq_shapefile = 'ShapeFiles/Aquifers/Columbia_Plateau/CRB_extent4xconnections.shp',
    states = ['WA', 'OR', 'ID', 'MT', 'NV']
)