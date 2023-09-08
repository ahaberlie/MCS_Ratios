import requests
import os
from bs4 import BeautifulSoup

def get_url_paths(url, ext='', params={}):
    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return response.raise_for_status()
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent

def download_geog():
    for ext in ['.cpg', '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.xml', '.shx']:

        url = "https://svrimg.niu.edu/npjcas23/"

        result = get_url_paths(url, ext)

        for url in result:

            fname = url.replace("%20", " ")

            fname = fname.split("/")[-1]

            fname = f"../data/{fname}"

            if not os.path.exists(fname):

                r = requests.get(url)
                print("Downloaded", fname)
                with open(fname, 'wb') as f:
                    f.write(r.content)
            else:
                print(fname, "exists")
    
    
def download(period=None):
    '''
    Takes a period to download. If None, all files will download
    If annual, the annual files will download, if a season of
    DJF, MAM, JJA, or SON, download only that season.
    '''
    
    download_geog()
    
    for ext in ['.nc']:

        url = "https://svrimg.niu.edu/npjcas23/"

        result = get_url_paths(url, ext)

        for url in result:

            fname = url.replace("%20", " ")

            fname = fname.split("/")[-1]

            fname = f"../data/{fname}"
            
            if period == None:
            
                if not os.path.exists(fname):

                    r = requests.get(url)
                    print("Downloaded", fname)
                    with open(fname, 'wb') as f:
                        f.write(r.content)
                else:
                    print(fname, "exists")
                    
            elif period.lower() == 'annual':
                
                if 'years' in fname:
                    
                    if not os.path.exists(fname):

                        r = requests.get(url)
                        print("Downloaded", fname)
                        with open(fname, 'wb') as f:
                            f.write(r.content)
                    else:
                        print(fname, "exists")
                        
            else:
                
                if period in fname:
                    
                    if not os.path.exists(fname):

                        r = requests.get(url)
                        print("Downloaded", fname)
                        with open(fname, 'wb') as f:
                            f.write(r.content)
                    else:
                        print(fname, "exists")