#import libraries
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup as bs
import requests

import csv
import os

#keyword for what we want to search and headers for request 
#you can modify it for the categories easly
keyword="monitör"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

#amazon search is always 7 pages, but we are going to check it anyways
def get_total_page():
    url = "https://www.amazon.com.tr/s?k=" + keyword
    page = requests.get(url, headers=headers)
    soup= bs(page.content, "html.parser")
    totalpage=soup.find("span", {"class": "s-pagination-item s-pagination-disabled"})
    return int(totalpage.text)

#getting links for every search item for every page, later on we are going to use it for populate our database
def get_hrefs(totalpage):
    hrefs=[]
    for page in range(totalpage):
        page = page+1
        url = "https://www.amazon.com.tr/s?k=" + keyword +"&page="+ str(page)
        page = requests.get(url, headers=headers)
        soup1= bs(page.content, "html.parser")
        productpages=soup1.find_all("a", {"class": "a-link-normal s-no-outline"})
        totalpage=soup1.find("span", {"class": "s-pagination-item s-pagination-disabled"})
        hrefs_temp = [productpage['href'] for productpage in productpages if productpage.get('href')]
        for href in hrefs_temp:
            hrefs.append(href)

    return hrefs

#finally we are collecting data for each item from its page
def get_product_data(hrefs = []):
    for link in hrefs:
        url = "https://www.amazon.com.tr" + link
        page = requests.get(url, headers=headers)
        soup1 = bs(page.content, "html.parser")

        #product price
        product_price = soup1.find("span", {"class" : "a-price aok-align-center reinventPricePriceToPayMargin priceToPay"})
        if product_price:
            product_price = product_price.get_text().replace(',', '.')
        else:
            #if it hasn't product price then its useless for us
            continue

        #product name
        product_name = soup1.find("span", {"id" : "productTitle"}).get_text(strip=True)

        #seller and shipper info
        info = soup1.find_all("span", {"class" : "a-size-small offer-display-feature-text-message"})
        if info:
            seller = info[1].get_text(strip=True)
            shipper = info[2].get_text(strip=True)
        else:
            seller = "not available"
            shipper = "not available"

        #details that can be useful
        details = soup1.find_all("td", {"class" : "a-size-base prodDetAttrValue"})
        if details:
            brand = details[0].get_text(strip=True)
            date_first_available = details[-1].get_text(strip=True)
        else:
            brand = "not available"
            date_first_available = "not available"
        #we can create a timestap for comparing price changes in time but i'm not going to use that in this project

        #creating csv to use afterwards
        get_csv(product_name, product_price, brand, seller, shipper, date_first_available)

    
#function for creating a csv   
def get_csv(product_name, product_price, brand, seller, shipper, date_first_available):
    #Columns and rows
    header = ["Product Name", "Product Price", "Brand", "Seller", "Shipper", "Date First Available"]
    data = [product_name, product_price, brand, seller, shipper, date_first_available]

    #Checking if file exists
    file_exists = os.path.exists('AmazonScrappingDataset'+keyword+'.csv')

    if not file_exists:
        #Create the file and write the data
        with open('AmazonScrappingDataset'+keyword+'.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(data)
    else:
        #Opens file and append new datas
        with open('AmazonScrappingDataset'+keyword+'.csv', 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # Veriyi dosyaya ekle
            writer.writerow(data)

totalpage = get_total_page()
hrefs = get_hrefs(totalpage)
get_product_data(hrefs)
