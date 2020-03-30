"""
This script connects to NPR's top 350 commencement speeches and pulls out the speeker's
name, the school, and the year of the speech. Using that information, it uses Selenium
to serach for the speech on YouTube and then pulls the transcript off of the speech
video. Data is then uploaded to MongoDB for storage.
"""

import random
import os
import pickle

from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient

import requests
import pandas as pd


def save_csv(data, file_name):
    """Saves dataframe to csv.

    Args:
    data -- a pandas dataframe
    file_name -- name for storing csv file
    """
    data.to_csv(f'data/{file_name}.csv', index=False)

# Scrape speech information from NPR

def load_page_for_scraping():
    """Returns a beautifulSoup result from loading NPR's top 350 commencement speeches
    found at http://apps.npr.org/commencement/.
    """

    url = 'http://apps.npr.org/commencement/'
    response = requests.get(url)
    status = response.status_code

    if status == 200:
        page = response.text
        soup = BeautifulSoup(page, "lxml")

    else:
        print(f"Error code: {status}")

    return soup

def scrape_npr():
    """Returns a list of NPR's top 350 speeches. The list includes speaker name, school, and year
    they speech was given.
    """
    soup = load_page_for_scraping()

    speeches = []
    speech_names = soup.find_all('h2', class_='speech-name')
    speech_schools = soup.find_all('p', class_='speech-school')
    speech_years = soup.find_all('p', class_='speech-year')

    for i in range(len(speech_names)):
        speeches.append([speech_names[i].text, speech_schools[i].text, speech_years[i].text])

    # Save list as dataframe for accessing later
    speech_df = pd.DataFrame.from_records(speeches)
    save_csv(speech_df, 'npr_speech_list')

    return speeches

# Scrape speech transcripts from YouTube

def gettranscript(speech, i):
    """Returns a speech transcript from YouTube.

    Args:
    speech -- a list of the speaker name, school where speech was made, and the delivery year.
    i -- the count to keep track of progress
    """

    sleeptime = [5, 15]

    # connect to selenium driver
    chromedriver = "/Applications/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver

    driver = webdriver.Chrome(chromedriver)

    sleep(random.uniform(sleeptime[0], sleeptime[1]))

    # set wait conditions for optimal scraper performance
    wait = WebDriverWait(driver, 3)
    visible = EC.visibility_of_element_located

    query = speech[0] + ' ' + speech[1] + ' ' + speech[2] + ' ' + 'commencement speech'
    driver.get("https://www.youtube.com/results?search_query=" + str(query))

    wait.until(visible((By.ID, "video-title")))
    driver.find_element_by_id("video-title").click()
    sleep(random.uniform(2, 4))

    # try and except sequence to continue process if a video / transcript does not exist
    try:
        element = driver.find_element_by_xpath('//button[@aria-label="More actions"]')
    except:
        msg = 'could not find options button'
        driver.quit()
        print(msg)
        return msg

    try:
        sleep(random.uniform(2, 5))
        element.click()
    except:
        msg = 'could not click'
        driver.quit()
        print(msg)
        return msg

    try:
        path = '//ytd-menu-service-item-renderer[@aria-selected="false"]'
        element = driver.find_element_by_xpath(path)
    except:
        msg = 'could not find transcript in options menu'
        driver.quit()
        print(msg)
        return msg

    try:
        sleep(random.uniform(2, 5))
        element.click()
    except:
        msg = 'could not click'
        driver.quit()
        print(msg)
        return msg

    try:
        sleep(random.uniform(2, 4))
        body_path = '//ytd-transcript-body-renderer[contains(@class, "style-scope")]'
        element = driver.find_element_by_xpath(body_path)
    except:
        msg = 'could not find transcript text'
        driver.quit()
        print(msg)
        return msg

    tscript = element.text

    #append transcript to list along with the speaker name, school, and speech year
    body_text_ls = [speech[0], speech[1], speech[2], tscript]

    driver.quit()
    print(f'Speech number {i}, {speech[0]} scraped')

    return body_text_ls

def scrape_speech_transcripts(speeches_list):
    """Pickles and returns a list of all speeches scraped from YouTube. List output includes speaker
    name, school they spoke at, year of the speech, and the speech transcript. Keeps track of the
    number of speeches scraped.
    """

    all_scraped_content = []
    remaining = [speech[0] for speech in speeches_list]
    i = 1

    for speech in speeches_list:
        scraped_content = gettranscript(speech, i)
        all_scraped_content.append(scraped_content)
        i += 1
        remaining.pop(0)

    with open('scraped_content.pkl', 'wb') as file:
        pickle.dump(all_scraped_content, file)

    # Note: if process above breaks, re-run with only the speeches in the remaining list

    return all_scraped_content

def load_additional_speeches():
    """Return additional speeches that were on NPRs list but did not have transcripts on YouTube."""

    manually_added_speeches = pickle.load(open("manual_speeches.pkl", "rb"))
    return manually_added_speeches

def upload_to_mongo(speech_content):
    """Connects to mongo database 'speeches'. Uploads raw commencement speeches into database."""

    client = MongoClient()

    # connect to database within mongoDB
    speech_db = client.speeches

    # add each speech to MongoDB
    for speech in speech_content:
        speech_dict = {'name': speech[0],
                       'school': speech[1],
                       'year': speech[2],
                       'speech': speech[3]}
        speech_db.speech_collection.insert_one(speech_dict)

    print("All speeches uploaded to Mongo.")

def main():
    """Scrapes information from NPR's top 350 commencement speeches using BeautifulSoup and then
    uses Selenium Chrome driver to pull the transcripts from YouTube.
    """
    # Pull in speech content
    speeches = scrape_npr()
    full_scraped_speeches = scrape_speech_transcripts(speeches)
    additional_speeches = load_additional_speeches()

    # Upload both lists to MongoDB
    upload_to_mongo(full_scraped_speeches)
    upload_to_mongo(additional_speeches)
