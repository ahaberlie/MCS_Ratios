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

def download():
    for ext in ['.nc', '.cpg', '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.xml', '.shx']:

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