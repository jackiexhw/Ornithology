
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as urlr
#import sys
#!{sys.executable} -m pip install requests 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests


# In[2]:


#open new chrome window and go to audubon website
driver = webdriver.Chrome('C:\chromedriver_win32\chromedriver.exe')
driver.get('https://www.audubon.org/bird-guide')

#if there is a popup close it
if len(driver.find_elements_by_id('popup-full-takeover-close')) != 0:
    no_thanks = driver.find_element_by_id('popup-full-takeover-close')
    no_thanks.click()

#scrolls all the way to the bottom of the page so that all the birds (385 of them) are loaded
last_bird = 0
while last_bird == 0:
    last_bird = len(driver.find_elements_by_id('node-385'))
    driver.find_element_by_tag_name('body').send_keys(Keys.END)
    
# add bird names to name list
name_list = []
card_list = driver.find_elements_by_class_name('bird-card')
for card in card_list:
    name = card.find_element_by_tag_name('h4').text
    name_list.append(name)
name_list[40]

#creates a csv file to hold the list of names and all the information later
df = pd.DataFrame(name_list,columns=['names'])
df.drop([0], axis=0,inplace=True)
df.to_csv('bird_names.csv')
driver.close()


# In[3]:


base_url = "https://www.audubon.org/field-guide/bird/"
file_name = "birds'csv"
#adds the headers (info about each bird we want to obtain from the website) into the file
f = open(file_name, "w")
headers = "common_name, scientific_name, family, habitat, feeding behavior, eggs/youth, diet, nesting \n"
f.write(headers)

for name in df["names"]:
    #adjust names
    name = name.replace(" ", "-", 5)
    name = name.replace("'", "", 5)
    #get url for bird of interest
    #open connection, downloads webpage
    full_url = base_url + name
    req = requests.get(full_url)
    if req.status_code == 200:
        uClient = urlr(full_url)
    else:
        continue
   
    #stores html of entire page
    page_html = uClient.read()
    #closes connection once html is obtained
    uClient.close()

    page_soup = soup(page_html, "html.parser")
    bird_card = page_soup.find("div", {"class": "bird-guide-card"})
    #finds scientific name html of page
    sci_name = bird_card.p.text.strip()
    #family
    family = bird_card.a.text.strip()
    #finds the habitat description for each bird in html, if it's not there then puts NA
    if "habitat" in bird_card.find("table", "collapse").tbody.text or "Habitat" in bird_card.find("table", "collapse").tbody.text:
        try:
            habitat = bird_card.find("table", "collapse").find("th", text="Habitat").find_next_sibling("td").text
        except:
            habitat = "NA"
    else:
        habitat = "NA"
    
    bird_tweets = bird_card.findAll("section", {"class": "bird-guide-section"})[2]
    #feeding behavior
    if "Feeding Behavior" in bird_tweets.text:
        try:
            feed = bird_tweets.find("h5", text="Feeding Behavior").find_next_sibling("p").text
        except:
            feed = "NA"
    else:
        feed = "NA"
    #eggs/youth
    if "Eggs" in bird_tweets.text:
        try:
            eggy = bird_tweets.find("h5", text="Eggs").find_next_sibling("p").text
        except:
            eggy = "NA"
    else:
        eggy = "NA"
    #diet
    if "Diet" in bird_tweets.text:
        try:
            diet = bird_tweets.find("h5", text="Diet").find_next_sibling("p").text
        except:
            diet = "NA"
    else:
        diet = "NA"
    #nesting
    if "Nesting" in bird_tweets.text:
        try:
            nest = bird_tweets.findAll("h5")[-1].find_next_sibling("p").text #.find_next_sibling("p").text
        except:
            nest = "NA"
    else:
        nest = "NA"
    
    #adds all the text to the file, separate each section with a comma and replace pre-existing commas with semi-colon
    f.write(name.replace(",", ";") + "," + sci_name.replace(",", ";") + "," + family.replace(",", ";") + "," +             habitat.replace(",", ";") + "," + feed.replace(",", ";") + "," + eggy.replace(",", ";") + "," + 
            diet.replace(",", ";") + "," + nest.replace(",", ";") + "\n")
    #prints name after each bird is complete
    print(name)

#close file after all brids complete
f.close()


