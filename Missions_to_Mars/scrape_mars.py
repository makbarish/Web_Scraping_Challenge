import time
import pymongo
import requests
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as bs

# DB Setup
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 

def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()
    collection.drop()

    # Nasa Mars news
    news_url = 'https://redplanetscience.com/'
    browser.visit(news_url)
    news_html = browser.html
    news_soup = bs(news_html,'lxml')
   # Extract title  and paragraph text
    news_title = news_soup.find("div",class_="content_title").text
    news_para = news_soup.find("div", class_="article_teaser_body").text 


    # JPL Mars Space Images - Featured Image
    jurl = 'https://spaceimages-mars.com/'
    browser.visit(jurl)
    jhtml = browser.html
    image_soup = bs(jhtml,"html.parser")
    image_url = image_soup.find("a", class_="showimg")["href"]
    featured_image_url = jurl + image_url

     # Mars fact
    murl = 'https://galaxyfacts-mars.com/'
    table = pd.read_html(murl)
    mars_df = table[0]
    print(table)
    print(mars_df)
    mars_df.columns = ["Properties", "Mars", "Earth"]
    mars_df =  mars_df[['Properties', 'Mars']]
    mars_fact_html = mars_df.to_html(header=False, index=False)

    # Mars Hemispheres
    mhurl = 'https://marshemispheres.com/'
    browser.visit(mhurl)  
    html = browser.html
    mh_soup = bs(html, "html.parser")
    results = mh_soup.find_all("div",class_='item')
    hemisphere_image_urls = []
    for result in results:
        product_dict = {}
        titles = result.find('h3').text
        end_link = result.find("a")["href"]
        image_link = "https://marshemispheres.com/" + end_link    
        browser.visit(image_link)
        html = browser.html
        soup= bs(html, "html.parser")
        downloads = soup.find("div", class_="downloads")
        image_url = "https://marshemispheres.com/" + downloads.find("a")["href"]
        print(titles)
        print(image_url)
        product_dict['title']= titles
        product_dict['image_url']= image_url
        hemisphere_image_urls.append(product_dict)


     # Close the browser after scraping
    browser.quit()

    # Return results
    mars_data ={
		'news_title' : news_title,
		'summary': news_para,
        'featured_image': image_url,
		# 'featured_image_title': featured_image_title,
		'fact_table': mars_fact_html,
		'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'jpl_url': jurl,
        'fact_url': murl,
        'hemisphere_url': mhurl,
        }
    return mars_data