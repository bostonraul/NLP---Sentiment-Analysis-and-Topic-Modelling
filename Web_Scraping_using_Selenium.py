# Web Scraping using Selenium

'''
SOURCE: https://github.com/dddat1017/Scraping-Youtube-Comments

Prerequisites:
    1. Install selenium package
    2. Install chromedriver for your chrome version
       2.1 Download driver from https://sites.google.com/a/chromium.org/chromedriver/downloads
       2.2 Copy driver to C:\webdrivers\chromedriver.exe
'''

from selenium import webdriver
from selenium.common import exceptions
import sys

def scrape(url):
    """
    Extracts the comments from the Youtube video given by the URL and returns a list object
    
    Args:
        url (str): The URL to the Youtube video
    Raises:
        selenium.common.exceptions.NoSuchElementException:
        When certain elements to look for cannot be found
    """

    # Note: replace argument with absolute path to the driver executable.
    driver = webdriver.Chrome('C:\webdrivers\chromedriver')

    # Navigates to the URL, maximizes the current window, and
    # then suspends execution for (at least) 5 seconds (this
    # gives time for the page to load).
    driver.get(url)
    driver.maximize_window()
    time.sleep(5)

    try:
        # Extract the elements storing the video title and
        # comment section.
        title = driver.find_element_by_xpath('//*[@id="container"]/h1/yt-formatted-string').text
        comment_section = driver.find_element_by_xpath('//*[@id="comments"]')
    except exceptions.NoSuchElementException:
        # Note: Youtube may have changed their HTML layouts for
        # videos, so raise an error for sanity sake in case the
        # elements provided cannot be found anymore.
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)

    # Scroll into view the comment section, then allow some time
    # for everything to be loaded as necessary.
    driver.execute_script("arguments[0].scrollIntoView();", comment_section)
    time.sleep(7)

    # Scroll all the way down to the bottom in order to get all the
    # elements loaded (since Youtube dynamically loads them).
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        # Scroll down 'til "next load".
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

        # Wait to load everything thus far.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # One last scroll just in case.
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        # Extract the elements storing the dates and comments.
        #username_elems = driver.find_elements_by_xpath('//*[@id="author-text"]')
        date_elems = driver.find_elements_by_xpath('//*[contains(@class,"published-time-text above-comment style-scope ytd-comment-renderer")]')
        comment_elems = driver.find_elements_by_xpath('//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)

    #print("> VIDEO TITLE: " + title + "\n")
    #print("> USERNAMES & COMMENTS:")
    
    text = []

    for date, comment in zip(date_elems, comment_elems):
        #print(username.text + ":")
        if date.text.split(' ')[-1]=='ago':
            text.append([date.text,comment.text])
        else:
            text.append(["",comment.text])
        
    driver.close()

    return text

#--------------------------------------------------------------------------------------------------
def get_youtube_comments(urlids):
    
    comments = [[scrape('https://www.youtube.com/watch?v='+id) for id in urlids[x]] for x in urlids.keys()]
    
    # Double flattening list to create a list of lists
    comments = [item for sublist in [item for sublist in comments for item in sublist] for item in sublist]
    
    return pd.DataFrame(comments,columns=['Date','Comment'])

#----------------------------------------------------------------------------------------------------
# Pass a dictionary of lists as input to the function

urlids = {'classic':['dA9S0ca4aqo','8bvRDdtoLag','oy0pKO3OA2w','uPEqoCrT_h0','RucIQ1oi4sA','kAoxWLuYx8g'],
         'thunderbird':['JE4TF986Qao','WcHR543CLWA','HQ-onzb3Y2U','DQDoflX43Ck','SGdPrHshsLQ']}
#-----------------------------------------------------------------------------------------------------
yt_comments = get_youtube_comments(urlids)
yt_comments