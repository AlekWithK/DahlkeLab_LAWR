# This script is a one-time use script to download ALL HUC4 shapefiles from: https://apps.nationalmap.gov/downloader/#/
# as it's easier to sort through them locally rather than on the website. All necessary HUC4's for this study should be 
# available on my GitHub (https://github.com/AlekWithK) making this tool redundant for future use.

def huc4_downloader():
    target_folder = 'D:/HUC4/'
    test_limit = math.inf

    # HUC4's I've already downloaded -- Make empty if starting from scratch
    blacklist = set(['1114', '1501', '1503', '1504', '1505', '1506', '1507', '1508', '1802', '1803', '1804', '1805', '1809', '1701', '1702', '1703', '1705', '1706', '1707', 
                     '1012', '1014', '1015', '1017', '1018', '1019', '1020', '1021', '1022', '1025', '1026', '1027', '1102', '1103', '1104', '1105', '1106', '1108', '1109', 
                     '1110', '1112', '1113', '1205', '1208', '1306', '1307', '0315', '0316', '0317', '0318', '0514', '0604', '0714', '0801', '0802', '0803', '0804', '0805', 
                     '0806', '1101', '1111', '0101', '0102', '0103'])

    # Where 0101 is the smallest HUC4 code and 2204 is the largest on the USGS website
    with open(f'{target_folder}logfile.txt', 'a') as file:
        sys.stdout = file
        
        count = 0
        for code in range(int('0101'), 2205):
            count += 1
        
            # Handle HUC4 codes with leading zeros
            if len(str(code)) == 3:
                code = '0' + str(code)            
                            
            if code in blacklist:
                print(f'NHD_H_{code} previously downloaded')
                continue
            
            if os.path.exists(target_folder + f'NHD_H_{code}_HU4_Shape.zip'):
                print(f'NHD_H_{code} already in folder')
                continue

            try:
                download_url = f'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHD/HU4/Shape/NHD_H_{str(code)}_HU4_Shape.zip'
                response = requests.get(download_url, stream=True)
                if response.status_code == 200:
                    with open(target_folder + f'NHD_H_{code}_HU4_Shape.zip', 'wb') as f:
                        print(f'Downloading NHD_H_{code}...')
                        f.write(response.content)
                            
                else:
                    print(f'Invalid response for NHD_H_{code}: {response.status_code}')
                    print(f'URL: {download_url}')
                    continue
                            
            except Exception as e:
                print(f'Error downloading NHD_H_{code}: {e}')
                continue
            
            # Testing breakout
            if count > test_limit:
                break
        
        sys.stdout = sys.__stdout__

if __name__ == '__main__':    
    import requests
    import os
    import math
    import sys
    
    huc4_downloader()
    print('Downloads complete!')