"""import splinter,beautiful soup,and pandas"""
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

#set up Splinter
def scrape_all():
    #initiate headlessndriver for deployment
    executable_path ={'executable_path':ChromeDriverManager().install()}
    browser =Browser('chrome',**executable_path,headless=False)
    news_title, news_paragraph = mars_news(browser)

    #Run all function
    data = {
        "news_title":news_title,
        "news_paragraph":news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
    #stop webdive and return data
    browser.quit()
    return data

def mars_news(browser):
    url ='https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    browser.is_element_present_by_css('div.list_text',wait_time=1)

    #convert the browser html to a soup object
    html = browser.html
    news_soup =soup(html, 'html.parser')

    #Add try /except for error
    try:
        slide_elem =news_soup.select_one('div.list_text')
        news_title =slide_elem.find('div',class_='content_title').get_text()
        news_p =slide_elem.find('div',class_='article_teaser_body').get_text()
    except AttributeError:
        return None,None 
    
    return news_title,news_p

def featured_image(browser):
    url ='https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)
    full_image =browser.find_by_tag('button')[1]
    full_image.click()
    #resulting html with soup
    html =browser.html
    img_soup =soup(html,'html.parser')
    try:
        imag_url_rel =img_soup.find('img',class_='fancybox-image').get('src')
    except AttributeError:
        return None
    #use the base url to creat an absolute url
    img_url =f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html/{imag_url_rel}'
    return img_url

def mars_facts():
    #Use 'pd.read_html'to pull the  data from the Mars-Earth comparison section
    URL = 'https://space-facts.com/mars/'
    try:
        mars_df = pd.read_html(URL)[1]
    except BaseException:
        return none
    mars_df.columns=['Description','Mars','Earth']
    mars_df.set_index('Description',inplace=True)

    return mars_df.to_html()


def hemispheres(browser):
    urls ='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(urls)


    #create a list to hold the image and titles.
    hemisphere_image_urls =[]

    #get a list of all the hemispher by finding 
    links = browser.find_by_css('a.product-item img')

    #creat a loop 
    for i in range(len(links)):
        hemisphere ={}
        # finding element
        browser.find_by_css('a.product-item img')[i].click()
        sample_elem =browser.links.find_by_text('Sample').first
        hemisphere['image_url'] =sample_elem['href']
        #get hemisphere title 
        hemisphere['title'] =browser.find_by_css('h2.title').text
        #Append hemisphere object to list 
        hemisphere_image_urls.append(hemisphere)
        #finally backwards
        browser.back()
    return hemisphere_image_urls

if __name__ =="__main__":
    print(scrape_all())