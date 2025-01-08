import pandas as pd
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
import glob
import os




def filename_to_title(filename):
    filename = os.path.basename(filename)
    filename = filename.replace("&", "-").replace("?", "")
    return filename.replace(".pdf", "").replace("_", " ").replace(" - ", " ")   

################################################################################################
###                                 allianz
################################################################################################
print("Loader allianz")

source   = "allianz"
base_url = "https://www.allianz-trade.com"
scrap    = "c-link c-link--block" #class that contains the pdf url

if sys.platform == "win32":
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
else:
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
headers = { 'User-Agent': user_agent }


pages = range(1,2) # range(0,215)
for numpage in pages:
    print(f"Page : {numpage}")

    # Base url
    url      = f"https://www.allianz-trade.com/en_global/news-insights/economic-insights.html/{numpage}"
    response  = requests.get(url, headers=headers)
    html_data = response.content

    soup_item = BeautifulSoup(html_data, 'html.parser')
    list_pub  = soup_item.find_all(class_="article-image")

    for pub in list_pub:
        try:
            url_pub = pub.get('href') # Get the url of the article
            url_pub = f"{base_url}{url_pub}"

            resp_pub = requests.get(url_pub, headers=headers)
            soup_pub = BeautifulSoup(resp_pub.content, 'html.parser')
            
            # Get the title and formate the date
            title = soup_pub.find('div', class_='l-grid__column-large-12')
            title = title.find('h1')
            title = title.get_text(strip=True)
            title_item = re.sub(r'[^A-Za-z0-9]+', ' ', title).lower().replace(' ','_')
            title_item = title_item[1:] if title_item[0] == "_" else title_item
            
            date_div = soup_pub.find('div', class_='c-copy c-stage__additional-info u-text-hyphen-auto')
            pub_date = date_div.get_text(strip=True)
            pub_date = datetime.strptime(pub_date, "%d %B %Y").strftime("%Y-%m-%d")
            year_pdf       = pd.to_datetime(pub_date).year
            month_pdf      = pd.to_datetime(pub_date).strftime('%m')
            day_pdf        = pd.to_datetime(pub_date).strftime('%d')
            
            # Get the url pdf
            pdf = [a.get("href") for a in soup_pub.find_all(class_=scrap) if 'pdf' in a.get('href', '').lower()]
            pdf = pdf[0]
            url_pdf = f"{base_url}{pdf}"

                # pub_date     = datetime.strptime(pdf.split("/")[4], "%Y-%m").strftime("%Y-%m-01")
            response_pdf = requests.get(url_pdf, headers=headers)
                # title_pdf    = f'output/{source}_{pub_date}{title_item}.pdf'

            title_pdf    = f'{title_item}.pdf'.replace("__","_")
        except:
            print("Erreur check :", url_pub)
            continue
        
        # Store it in your folder
        path = f"output/{source}/{year_pdf}/{month_pdf}"
        if not os.path.exists(path):
                os.makedirs(path)
        with open(f'{path}/{title_pdf}', 'wb') as pdf_file:
                pdf_file.write(response_pdf.content)

            # title_pdf = f'{path}/{source}_{pub_date}_{title_item}.pdf'.replace("__","_")



print("Done")

