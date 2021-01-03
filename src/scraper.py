import requests
import pandas as pd
from bs4 import BeautifulSoup

RES_TABLE_BASE = "https://www.un.org/depts/dhl/resguide/r{}_resolutions_table_eng.htm"
BOUNDS = [48, 75]  # since the 48th sessions the pdf documents are nicely formatted for text extraction

## TODO:
# set content id tags

list_df = list()

for i, url in enumerate([RES_TABLE_BASE.format(x) for x in range(BOUNDS[0], BOUNDS[1])]):
    page = requests.get(url)

    if page.status_code == 404:
        # '_eng' ending to '_en'
        page = requests.get(url[:-5] + ".htm")

    soup = BeautifulSoup(page.text, 'html.parser')
    
    table = soup.find('tbody')
    table_rows = table.find_all('tr')
    
    # the first two rows are just the headings
    for tr in table_rows[2:]:
        td = tr.find_all('td')
        td = [td[0], td[-1]]  # only care about resolution no and topic
        row = [tr.text for tr in td]
        list_df.append(row)
    
    print(f"INFO: retrieved & extracted {BOUNDS[0] + i} page")

df = pd.DataFrame(list_df, columns=["resolution", "topic"])
df.to_csv("res_names.csv")