# A quick one-time use script to process all downloaded HUC4 zipfiles, extracting the 4 required WBDHU4 files
# to a new folder. This script is not necessary for future use as the WBDHU4 files are already available on my GitHub


def huc4_processor():
    
    test_limit = math.inf
    count = 0
    target_files = ['WBDHU4.dbf', 'WBDHU4.prj', 'WBDHU4.shp', 'WBDHU4.shx']
    target_folder = 'D:/HUC4/'
    dest_folder = 'D:/HUC4/_processed/'    

    for zipfile_name in os.listdir('D:/HUC4/'):
        if zipfile_name.endswith('.zip'):
            count += 1
            print(f'Processing {zipfile_name}...')
            zipfile_path = os.path.join(target_folder, zipfile_name)
            
            dest_path = f'{dest_folder}{zipfile_name[:-14]}/'
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            
            temp = f'{target_folder}_temp/'
            if not os.path.exists(temp):
                os.makedirs(temp)
                
            with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
                subfolder = 'Shape/'
                for file in target_files:
                    path_in_zip = os.path.join(subfolder, file)
                    zip_ref.extract(path_in_zip, temp)
                    
                    extract_file_path = os.path.join(temp, path_in_zip)
                    output_file_path = os.path.join(dest_path, file)
                    shutil.move(extract_file_path, output_file_path)
                    
            shutil.rmtree(temp)
            
            if count > test_limit:
                break                          


if __name__ == '__main__':
    import os
    import zipfile
    import shutil
    import math
    
    huc4_processor()
    print('HUC4 processing complete')
    
    