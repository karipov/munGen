import requests
import time
from urllib.parse import urljoin
import pandas as pd
import glob

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


LOAD_BASE = "https://daccess-ods.un.org/access.nsf/Get?OpenAgent&DS={}&Lang=E"
DESTINATION = "/Users/komron/dev/github/munGen/src/files/"

df = pd.read_csv("meta/clean_res_names.csv", usecols=['resolution', 'topic'])

chrome_options = Options()
chrome_options.add_experimental_option('prefs',  {
    "download.default_directory": DESTINATION,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
    }
)

driver = webdriver.Chrome('drivers/chromedriver', options=chrome_options)

# try:
#     latest_file = max([int(x.split(DELIM)[0]) for x in glob.glob(DESTINATION.format('*'))])
# except ValueError:  # empty
#     latest_file = 0
    

# those that haven't been downloaded yet
# df = df.iloc[latest_file:, :]

def main():
    print("SETUP: starting downloads...")

    for i, res_name in zip(df.index, df['resolution']):
        driver.get(LOAD_BASE.format(res_name))
        print(f"INFO: progress {round(i+1 / df.shape[0] * 100)}%; saved {res_name};\n")
        
        time.sleep(2)