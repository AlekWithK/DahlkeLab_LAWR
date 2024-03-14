# This script is a one-time use script to download ALL HUC2/4 shapefiles from: https://apps.nationalmap.gov/downloader/#/
# as it's easier to sort through them locally rather than on the website. All necessary HUC4's for this study should be 
# available on my GitHub (https://github.com/AlekWithK) making this tool redundant for future use.

def huc4_downloader():
    target_folder = 'D:/HUC4/'
    test_limit = math.inf

    # HUC4's I've already downloaded -- Make empty if starting from scratch
    blacklist = set([])

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
        
def huc2_downloader():
    target_folder = 'D:/HUC2/'
    test_limit = math.inf
    
    with open(f'{target_folder}logfile.txt', 'a') as file:
        sys.stdout = file
        count = 0
        for code in range(int('01'), 19):
            if len(str(code)) == 1:
                code = '0' + str(code)
                
            if os.path.exists(target_folder + f'WBD_{code}_HU2_Shape.zip'):
                print(f'WBD_{code} already in folder')
                continue
            
            try:
                download_url = f'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_{str(code)}_HU2_Shape.zip'
                response = requests.get(download_url, stream=True)
                if response.status_code == 200:
                    with open(target_folder + f'WBD_{code}_HU2_Shape.zip', 'wb') as f:
                        print(f'Downloading WBD_{code}...')
                        f.write(response.content)
                        
                else:
                    print(f'Invalid response for WBD_{code}: {response.status_code}')
                    print(f'URL: {download_url}')
                    continue
                
            except Exception as e:
                print(f'Error downloading WBD_{code}: {e}')
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
    
    if len(sys.argv) < 2:
        print('Usage: python huc4_downloader.py <huc4 | huc2>')
        sys.exit(1)
    else:
        arg = sys.argv[1]
        
    if arg.lower() == 'huc4':
        huc4_downloader()
        print('Downloads complete!')
    elif arg.lower() == 'huc2':
        huc2_downloader()
        print('Downloads complete!')        
    else:
        print('Usage: python huc4_downloader.py <huc4 | huc2>')
        sys.exit(1)
        

    