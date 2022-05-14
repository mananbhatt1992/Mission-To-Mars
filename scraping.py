# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres":hemisphere_images(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p



def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemisphere_images(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    hemisphere_image_urls = []

    html = browser.html
    hemisphere_soup = soup(html, 'html.parser')
    try:
        hemisphere_items = hemisphere_soup.find_all('div', class_='item')

        # loop through the image links on page
        for item in hemisphere_items:
            # create empty dictionary to hold results
            hemispheres = {}
            # get html url of page where the full image link is located
            try:
                img_href = url + item.find('a',class_='itemLink product-item')['href']
                # change browser to url of where full image link is located
                browser.visit(img_href)
                # capture the html into Beautifulsoup
                img_href_html = browser.html
                img_href_html_soup = soup(img_href_html, 'html.parser')
                try:
                    # get the full image url
                    img_url = url + img_href_html_soup.find('div', class_='downloads').find_all('li')[0].a['href']
                except AttributeError:
                    img_url = "No URL Found"
                try:
                    # get title of image
                    image_title = img_href_html_soup.find('h2', class_='title').text
                except AttributeError:
                    image_title = "No Title Found"
                # add items to dictionary
                hemispheres = {
                    'img_url' : img_url,
                    'title' : image_title
                }
                # append dictionary to list
                hemisphere_image_urls.append(hemispheres)
            except:
                return None
            # change browser back one page to list of hemispheres
            browser.back()

    except AttributeError:
        return None
    
    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
