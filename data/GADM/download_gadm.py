import wget
import zipfile
import os
import shutil
import wget
import pandas as pd 
import sys 

if not os.path.isdir("./zipfiles"):
    os.mkdir("./zipfiles")

def download_gadm_zip(country_code):
    '''
    Just pulls down the country zip file of GADM boundaries
    '''

    url = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_{}_shp.zip".format(country_code)
    wget.download(url, "./zipfiles")


def process_zip(country_code, replace=False):
    '''
    Just unpacks the GADM country zip file and stores content

    Inputs:
        - replace: (bool) if True will replace contents, if False will skip if 
                          country code has been processed already
    '''

    p = os.path.join("./zipfiles", "gadm36_{}_shp.zip".format(country_code))

    with zipfile.ZipFile(p) as z:
        if not os.path.isdir(country_code):
            os.mkdir(country_code)
        z.extractall(country_code)

def update_gadm_data(replace=False):
    '''
    Gets all the GADM data

    Inputs:
        - replace: (bool) if True will replace contents, if False will skip if 
                          country code has been processed already

    '''

    df = pd.read_csv("../country_codes.csv")
    b = ~ df['gadm_name'].isna()
    codes = df[ b ]['gadm_name'].values
    names = df[ b ]['country'].values

    i = 0

    for country_name, country_code in zip(names, codes):
        print("\nProcessing GADM: ", country_name)
        if replace or not os.path.isdir(country_code):
            print("\tdownloading...")
            download_gadm_zip(country_code)
            process_zip(country_code)

        else:
            print("\tskip, file present")



if __name__ == "__main__":

    if len(sys.argv) == 1:
        replace_boolean = False
    else:
        replace_boolean = sys.argv[1]

    update_gadm_data(replace_boolean)
