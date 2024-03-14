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
    def __init__(self, name, datasets_dir, huc2s, huc4s):
        self.name = name # Aquifer name
        self.datasets_dir = datasets_dir
        self.huc2s = huc2s
        self.huc4s = huc4s

# Aquifer Definitions for Aquifer Analysis
upper_clairborne_aquifer = Aquifer(
    name = 'Upper_Clairborne',
    datasets_dir = "Prelim_Data/Upper_Clairborne",
    huc2s = [],
    huc4s = ['0315', '0316', '0317', '0318', '0514', '0604', '0714', '0801', '0802', '0803', '0804', '0805', '0806', '1101', '1111', '1114'],
)

central_valley_aquifer = Aquifer(
    name = 'Central_Valley',
    datasets_dir = f"Prelim_Data/Central_Valley",
    huc2s = [],
    huc4s = ['1802', '1803', '1804', '1805'],
)  

columbia_plateau_aquifer = Aquifer(
    name = 'Columbia_Plateau',
    datasets_dir = "Prelim_Data/Columbia_Plateau",
    huc2s = [],
    huc4s = ['1701', '1702', '1703', '1705', '1706', '1707'],
)

high_plains_aquifer = Aquifer(
    name = 'High_Plains',
    datasets_dir = "Prelim_Data/High_Plains",
    huc2s = [],
    huc4s = ['1012', '1014', '1015', '1017', '1018', '1019', '1020', '1021', '1022', '1025', '1026', '1027', '1102', '1103', '1104', '1105', '1106', '1108', '1109', '1110', '1112', '1113', '1205', '1208', '1306', '1307'],
)

arizona_alluvial_aquifer = Aquifer(
    name = 'Arizona_Alluvial',
    datasets_dir = "Prelim_Data/Arizona_Alluvial",
    huc2s = [],
    huc4s = ['1501', '1503', '1504', '1505', '1506', '1507', '1508'],
)

snake_river_aquifer = Aquifer(
    name = 'Snake_River',
    datasets_dir = "Prelim_Data/Snake_River",
    huc2s = [],
    huc4s = ['1704', '1705'],
)

coastal_lowlands_aquifer = Aquifer(
    name = 'Coastal_Lowlands',
    datasets_dir = "Prelim_Data/Coastal_Lowlands",
    huc2s = [],
    huc4s = ['0314', '0315', '0316', '0317', '0318', '0804', '0805', '0806', '0807', '0808', '0809', '1114', '1201'],
)

edwards_trinity_aquifer = Aquifer(
    name = 'Edwards_Trinity',
    datasets_dir = "Prelim_Data/Edwards_Trinity",
    huc2s = [],
    huc4s = ['1211', '1210', '1209', '1207', '1206', '1203', '1201', '1114', '1113', '0804', '1307', '1304', '1308', '1208']
)

floridian_aquifer = Aquifer(
    name = 'Floridian',
    datasets_dir = "Prelim_Data/Floridian",
    huc2s = [],
    huc4s = ['0309', '0310', '0308', '0311', '0312', '0314', '0313', '0307', '0306', '0305', '0304', '0303']
)

texas_gulf_coast_aquifer = Aquifer(
    name = 'Texas_Gulf_Coast',
    datasets_dir = "Prelim_Data/Texas_Gulf_Coast",
    huc2s = [],
    huc4s = ['1201', '1202', '1203', '1204', '1207', '1209', '1210', '1211', '1309', '1308', '1114']
)

upper_colorado_aquifer = Aquifer(
    name = 'Upper_Colorado',
    datasets_dir = "Prelim_Data/Upper_Colorado",
    huc2s = [],
    huc4s = ['1404', '1405', '1406', '1401', '1402', '1403', '1407', '1408']
)

pennsylvanian_aquifer = Aquifer(
    name = 'Pennsylvanian',
    datasets_dir = "Prelim_Data/Pennsylvanian",
    huc2s = [],
    huc4s = ['0411', '0501', '0502', '0503', '0504', '0505', '0205', '0509', '0507', '0510', '0513', '0601', '0602', '0603', '0316']
)

# List of all aquifers for easy iteration
ALL_AQUIFERS = [
    arizona_alluvial_aquifer,
    central_valley_aquifer,
    coastal_lowlands_aquifer,
    columbia_plateau_aquifer,
    edwards_trinity_aquifer,
    floridian_aquifer,
    high_plains_aquifer,
    pennsylvanian_aquifer,
    snake_river_aquifer,
    texas_gulf_coast_aquifer,
    upper_clairborne_aquifer,
    upper_colorado_aquifer
]
    