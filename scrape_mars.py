
# coding: utf-8

# import dependencies
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
from pprint import pprint

# Need to use splinter otherwise the list items that contain the articles wont't show up. Found that out the hard way...

def initBrowser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    return (browser)

def scrape():
    '''
    Gathers the following info on Mars:

        Latest article from 'https://mars.nasa.gov/news/'
        Featured iamge from 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
        Latest tweet for the weather on Mars
        Mars Facts
        Hi-res piics of Martian hemispheres

        Returns a dictionary with all this information
    '''

    # initialiize browser
    browser = initBrowser()

    # Define function that uses splinter to navigate to the various websites
    def soupBrowser (input_url):
        '''
        Takes an input url and gets the html content of that page in Chrome. 
        
        Returns a Beautiful Soup object of the html page.
        '''
        browser.visit(input_url)
        html = browser.html
        soup = bs(html, 'lxml')
        return soup

    # define url for the nasa site to scrape it
    nasa_url = 'https://mars.nasa.gov/news/'
    nasa_soup = soupBrowser(nasa_url)

    print('Getting latest article...')

    latestArticle = nasa_soup.find('div', class_='list_text')

    newsTitle = latestArticle.a.text

    newsTeaser = latestArticle.find('div', class_='article_teaser_body').text

    print('Article retrieved!')

    # ### JPL Mars Space Images - Featured Image

    # define new url for jpl mars space images
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    jpl_soup = soupBrowser(jpl_url)

    # Find the section tag that holds the featured image
    feat_img_section = jpl_soup.find('section', class_="centered_text clearfix main_feature primary_media_feature single")
    # The url is held in the anchor tag
    feat_img_anchor= feat_img_section.find('a', class_='button fancybox')

    # The featured inmage url is located in 'data-fancybox-href'
    feat_img_url = feat_img_anchor['data-fancybox-href']

    # need to add 'https://www.jpl.nasa.gov' to the beginning of the url
    nasa_base_url = 'https://www.jpl.nasa.gov'
    feat_img_url = nasa_base_url + feat_img_url
    print(feat_img_url)

    # ### Mars Weather

    # Define urls and create bs object
    mars_twitter_url = 'https://twitter.com/marswxreport?lang=en'
    mars_twitter_soup = soupBrowser(mars_twitter_url)

    mars_tweet = mars_twitter_soup.find('div', class_='js-tweet-text-container')

    mars_weather_text = mars_tweet.find('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text
    print(mars_weather_text)

    # ### Mars Facts

    # Define urls
    facts_url = 'http://space-facts.com/mars/'

    # read html with pandas
    mars_facts = pd.read_html(facts_url)

    # grab the df out of the returned list
    marsFacts_df = mars_facts[0]

    # rename df columns
    marsFacts_df.columns = ['Fact', 'Answer']

    marsFacts_df.head()

    # save as html, replace uneccesary '\n' characters
    marsFacts_html = marsFacts_df.to_html(index=False).replace('\n', '')

    # ### Mars Hemispheres

    # Define urls
    usgs_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    usgs_soup = soupBrowser(usgs_url)

    # Gather all the links to the image. The links are on the h3 tag
    link_texts = usgs_soup.findAll('h3')

    # Define emptu list to hold url dictionary
    hemisphere_img_urls = []

    # link to home site
    usgs_home = 'https://astrogeology.usgs.gov'

    # Loop through all links and gather the image
    for link in link_texts:
        # Click on the link to the full image
        browser.click_link_by_partial_text(link.text)
        
        # Get the html elements from this page using beautiful soup
        html = browser.html
        elements = bs(html, 'lxml')
        
        # get the partial image url using the 'img' tag with class_='wide-image'. The url is contained where src=''
        partial_img_url = elements.find('img', class_='wide-image')['src']
        
        # create full url
        full_img_url = usgs_home + partial_img_url
        
        # remove 'Enhanced' from the text
        title = link.text.replace(' Enhanced', '')
        # print(full_img_url)

        # Create dictionary with 'title' and 'img_url'
        img_dict = {'title': title, 'img_url':full_img_url}
        
        # append this dictionary to the hemisphere_img_urls list
        hemisphere_img_urls.append(img_dict)
        
        # Go back to the page with all the links
        browser.visit(usgs_url)

    # Print the dictionary to confirm sucess
    for url_info in hemisphere_img_urls:
        pprint(url_info)

    # Create a dictioonary to hold the scraped iinformation from all 4 sites
    scraped_data = {'newsTitle':newsTitle,
                    'newsTeaser':newsTeaser,
                    'featImg':feat_img_url,
                    'marsTweet':mars_weather_text,
                    'marsFacts':marsFacts_html,
                    'marsHemisphereImgs':hemisphere_img_urls
                    }
    return(scraped_data)

    