import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
def sflipkart(query):
     url=f"https://www.flipkart.com/search?q={query.replace('','+')}"
     headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
           }
     response=requests.get(url,headers=headers)
     if response.status_code!=200:
          st.error("Failed to fetch data from flipkart. Try again later")
          return[]
     soup=BeautifulSoup(response.content,"html.parser")
     product=soup.find_all("div",class_="_4rR01T")
     prices=soup.find_all("div",class_="_30jeq3_1_WHN1")
     specs=soup.find_all("ul",class_="_1xgFaf")
     rating=soup.find_all("div",class_="_3LWZIK")
     data=[]
     for i in range(len(product)):
          name=product[i].text
          price=prices[i].text if i<len(prices) else " "
          feature=specs[i].text if i<len(specs) else " "
          rate=rating[i].text if i<len(rating) else " "
          data.append({"Product name":name,"price":price,"feature":feature,"rating":rate})
     return data
