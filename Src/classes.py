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
    def __init__(self, name, datasets_dir, wb_dir, wb_shapefiles, aq_shapefile, states, blacklist):
        self.name = name # Aquifer name
        self.datasets_dir = datasets_dir    
        self.wb_dir = wb_dir # Path to aquifer watershed boundary shapefiles
        self.wb_shapefiles = wb_shapefiles # Name of watershed boundary shapefiles to loop through
        self.aq_shapefile = aq_shapefile # Path to aquifer shapefile
        self.states = states # List of states aquifer overlays 
        self.blacklist = blacklist # Set of blacklisted stream gauges known to lack data

# Aquifer Definitions for Aquifer Analysis
# Upper Clairbrone alluvial aquifer in south-central US    
upper_clairborne_aquifer = Aquifer(
    name = 'Upper_Clairborne',
    datasets_dir = "Prelim_Data/Upper_Clairborne",
    wb_dir = 'ShapeFiles/Aquifers/Upper_Clairborne_MS/HUC4',
    wb_shapefiles = 'WBDHU4.shp',
    aq_shapefile = 'ShapeFiles/Aquifers/Upper_Clairborne_MS/sir2008-5098_UCAQ_extent.shp',
    states = ['AR', 'LA', 'MS', 'TN', 'KY', 'MO', 'AL'],
    blacklist = set()
)

# Central Valley aquifer in California's Central Valley
central_valley_aquifer = Aquifer(
    name = 'Central_Valley',
    datasets_dir = "Prelim_Data/Central_Valley",
    wb_dir = 'ShapeFiles/Aquifers/Central_Valley/HUC4',
    wb_shapefiles = 'WBDHU4.shp',
    aq_shapefile = 'ShapeFiles/Aquifers/Central_Valley/Alluvial_Bnd.shp',
    states = ['CA', 'OR'],
    blacklist = {11203580, 11204100, 11206820, 360013118575201, 111626182, 11162619, 11162620, 11162735, 11162737, 11162753, 11169025, 11169860, 11170000, 11172175, 11172945, 11172955, 11173510, 11173575, 11173800, 11174160, 11174600, 11176340, 11179100, 11180825, 11180900, 11180960, 11181008, 11458433, 11458600, 11460151, 11460400, 11460600, 11460605, 11460750, 373507121472101, 11337080, 11355010, 11370700, 11401920, 11447830, 11447850, 11447890, 11447905, 11448750, 11448800, 11449255, 11451100, 11451300, 11451715, 11451800, 11452800, 11452900, 11453590, 11455095, 11455140, 11455280, 11455315, 11455338, 11455385, 11455420, 11224000, 11255575, 11261100, 11262900, 11273400, 11274550, 11274790, 11289850, 11299600, 11304810, 11311300, 11312672, 11312676, 11312685, 11312968, 11313240, 11313315, 11313405, 11313431, 11313433, 11313434, 11313440, 11313452, 11313460, 11336600, 11336685, 11336790, 11336930, 11336955, 11337190, 11447903, 375450121331701}
)  

# Lake Michigan Basin in Michigan
michigan_basin_aquifer = Aquifer(
    name = 'Michigan_Basin',
    datasets_dir = "Prelim_Data/Michigan_Basin",
    wb_dir = 'ShapeFiles/Aquifers/Michigan_Basin/HUC4',
    wb_shapefiles = 'WBDHU4.shp',
    aq_shapefile = 'ShapeFiles/Aquifers/Michigan_Basin/sir2009-5060_unit_alt_grid.shp',
    states = ['MI'],
    blacklist = set()
)

columbia_plateau_aquifer = Aquifer(
    name = 'Columbia_Plateau',
    datasets_dir = "Prelim_Data/Columbia_Plateau",
    wb_dir = 'ShapeFiles/Aquifers/Columbia_Plateau/HUC4',
    wb_shapefiles = 'WBDHU4.shp',
    aq_shapefile = 'ShapeFiles/Aquifers/Columbia_Plateau/CRB_extent4xconnections.shp',
    states = ['WA', 'OR', 'ID', 'MT', 'NV'],
    blacklist = {12422990, 12433200, 12301250, 12301933, 12308000, 12322000, 12391950, 12392155, 12393501, 12413125, 12413130, 12413131, 12413210, 12413355, 12413470, 12413860, 12413875, 12415135, 12417650, 12301250, 12301933, 12323233, 12323242, 12323250, 12323600, 12323670, 12323700, 12323710, 12323720, 12323750, 12323760, 12323770, 12323800, 12323840, 12323850, 12324200, 12324400, 12324590, 12324680, 12331800, 12334510, 12334550, 12335100, 12338300, 12350250, 12363500, 12365700, 12377150, 12381400, 12388700, 480608115242901, 12434590, 12438905, 12444290, 12444550, 12445500, 12445900, 12446150, 12446400, 12446995, 12447285, 12447383, 12448000, 12448998, 12452550, 12452890, 12452990, 12505450, 12507573, 13213100, 13215480, 13159800, 13161930, 13162225, 13176400, 13206305, 13206400, 13210045, 13210810, 13210824, 13210831, 13210980, 13210986, 132109867, 13211205, 13212549, 13212890, 13213000, 13213072, 13213100, 13215480, 13237920, 13162225, 13175100, 13317660, 13335050, 13297330, 13297350, 13297355, 13297380, 13302005, 13304050, 13304700, 13305310, 13306370, 13306385, 13309220, 13310199, 13311250, 13311450, 13317660, 13338950, 13341140, 13341570, 13342450, 13346800, 14013700, 14015350, 14111400}
)

high_plains_aquifer = Aquifer(
    name = 'High_Plains',
    datasets_dir = "Prelim_Data/High_Plains",
    wb_dir = 'ShapeFiles/Aquifers/High_Plains/HUC4',
    wb_shapefiles = 'WBDHU4.shp',
    aq_shapefile = 'ShapeFiles/Aquifers/High_Plains/hp_bound2010.shp',
    states = ['TX', 'OK', 'NM', 'KS', 'CO', 'NE', 'WY', 'SD', 'IA'],
    blacklist = set()
)