from bs4 import BeautifulSoup
import requests
import time, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from IPython.core.display import display, HTML
from selenium.common.exceptions import NoSuchElementException

from pymongo import MongoClient
from pprint import pprint
import pandas as pd
import re
import string


#Connecting to NPR to scrape top 350 speeches
def load_page_for_scraping():
    """Requests connection to the NPR page and prints confirmation if the page is
    loaded correctly. If fails to load, reports error. Returns beautiful soup
    object for scraping."""

    print("Connecting to NPR")
    url = 'http://apps.npr.org/commencement/'
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        print("Page loaded succcessfully")
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        return soup
    else:
        print(f"Error code: {status}")
        return

def scrape_NPR():
    """For NPRs 350 top commencement speeches, scrapes the speeker name, school name,
    and year speech was given. Returns list of speech information."""
    soup = load_page_for_scraping()
    print("Scraping speeker name, school, and year.")

    speeches = []
    speech_names = soup.find_all('h2', class_='speech-name')
    speech_schools = soup.find_all('p', class_='speech-school')
    speech_years = soup.find_all('p', class_='speech-year')

    for i in range(len(speech_names)):
        speeches.append([speech_names[i].text, speech_schools[i].text, speech_years[i].text])

    print("Speeker names, school, and year scraped.")

    return speeches


# leverage information from NPR to scrape youtube for the actual speech transcripts
def connecting_YouTube():
    """Connects to YouTube and confirms scraping permissions."""
    print("Confirming scraping allowance on YouTube.")
    url = 'https://www.youtube.com/robots.txt'
    response  = requests.get(url)
    print(response.text)
    return

def scraping_speeches(speech, i):
    """loads a selenium driver with youtube search result for the speech provided.
    Scrapes the transcript from that youtube page and returns a list of the speech
    information with the transcript."""

    chromedriver = "/Applications/chromedriver" # path to the chromedriver executable
    os.environ["webdriver.chrome.driver"] = chromedriver

    driver = webdriver.Chrome(chromedriver)

    wait = WebDriverWait(driver, 3)
    presence = EC.presence_of_element_located
    visible = EC.visibility_of_element_located

    #searches youtube for the speech speaker, school, year, and commencement speech
    query = speech[0] + ' ' + speech[1] + ' ' + speech[2] + ' ' + 'commencement speech'
    driver.get("https://www.youtube.com/results?search_query=" + str(query))

    #time delays accoutn for load time
    wait.until(visible((By.ID, "video-title")))
    driver.find_element_by_id("video-title").click()
    time.sleep(4)

    try:
        #identify and click on transcript if it exists. If not, skip and print error message.
        transcript_button = driver.find_element_by_xpath('//button[@aria-label="More actions"]')
        time.sleep(4)
        transcript_button.click()
        time.sleep(4)

        open_transcript_button = driver.find_element_by_xpath('//ytd-menu-service-item-renderer[@aria-selected="false"]')
        time.sleep(4)
        open_transcript_button.click()
        time.sleep(4)

        transcript_text = driver.find_element_by_xpath('//ytd-transcript-body-renderer[contains(@class, "style-scope")]')
        time.sleep(4)
        tscript = transcript_text.text

        driver.close()

        print(f"{i} transcripts scraped.")
        body_text_ls = [speech[0], speech[1], speech[2], tscript]
        time.sleep(5)

    except NoSuchElementException:
        print(f'{speech} does not have a transcript')
        driver.close()
        body_text_ls = []
        time.sleep(5)

    return body_text_ls

def upload_to_mongo(content):
    """conneccts to mongo database 'speeches'. Uploads raw content from commencement
    speech web scraping into database."""
    client = MongoClient()
    db = client.speeches
    commencement_speeches = db.commencement_speeches

    speech_entries = [{'name': entry[0],
                  'school': entry[1],
                  'year': entry[2],
                  'transcript': entry[3]}
                  for entry in content]

    commencement_speeches.insert_many(speech_entries)

    return

def pull_from_mongo():
    client = MongoClient()
    speech_db = client.speeches
    speech_collection = speech_db.speech_collection

    cursor = speech_collection.find()

    df = pd.DataFrame(list(cursor))

    return df
