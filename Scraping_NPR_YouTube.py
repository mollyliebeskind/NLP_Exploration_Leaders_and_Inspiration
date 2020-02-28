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

speeches = scrape_NPR()

def connecting_YouTube():
    """Connects to YouTube and confirms scraping permissions."""
    print("Confirming scraping allowance on YouTube.")
    url = 'https://www.youtube.com/robots.txt'
    response  = requests.get(url)
    print(response.text)
    return

connecting_YouTube()

# track transcripts that have been scraped and transcripts that remain in case process stops
# part way through

all_scraped_content = []
remaining = [speech[0] for speech in speeches]
i = 1

def gettranscript(speech, i):
    """loads a selenium driver with youtube search result for the speech provided.
    Scrapes the transcript from that youtube page and returns a list of the speech
    information with the transcript."""

    waittime = 10
    sleeptime = [5,15]

    # connect to selenium driver
    chromedriver = "/Applications/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver

    driver = webdriver.Chrome(chromedriver)

    sleep(random.uniform(sleeptime[0],sleeptime[1]))

    # set wait conditions for optimal scraper performance
    wait = WebDriverWait(driver, 3)
    presence = EC.presence_of_element_located
    visible = EC.visibility_of_element_located

    query = speech[0] + ' ' + speech[1] + ' ' + speech[2] + ' ' + 'commencement speech'
    driver.get("https://www.youtube.com/results?search_query=" + str(query))

    wait.until(visible((By.ID, "video-title")))
    driver.find_element_by_id("video-title").click()
    sleep(random.uniform(2,4))

    # try and except sequence to continue process if a video / transcript does not exist
    try:
        element = driver.find_element_by_xpath('//button[@aria-label="More actions"]')
    except:
        msg = 'could not find options button'
        driver.quit()
        print(msg)
        return msg

    try:
        sleep(random.uniform(2,5))
        element.click()
    except:
        msg = 'could not click'
        driver.quit()
        print(msg)
        return msg

    try:
        element = driver.find_element_by_xpath('//ytd-menu-service-item-renderer[@aria-selected="false"]')
    except:
        msg = 'could not find transcript in options menu'
        driver.quit()
        print(msg)
        return msg

    try:
        sleep(random.uniform(2,5))
        element.click()
    except:
        msg = 'could not click'
        driver.quit()
        print(msg)
        return msg

    try:
        sleep(random.uniform(2,4))
        element = driver.find_element_by_xpath('//ytd-transcript-body-renderer[contains(@class, "style-scope")]')
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

# iterate through list of speeches obtained from NPR scraping
# look up each speech on YouTube and scrape the transcript

for speech in speeches:
    scraped_content = gettranscript(speech, i)
    all_scraped_content.append(scraped_content)
    i += 1
    remaining.pop(0)

# Note: if process above breaks, re-run with only the speeches in the remaining list

# Store all scraped content in pickle to prevent losing data if system errors
with open('scraped_content.pkl', 'wb') as f:
    pickle.dump(all_scraped_content, f)

# For speeches that did not have transcripts on YouTube, they were manually added to a list pickled
# in a different document. Read in manual list.

manually_added_speeches = pickle.load( open( "manual_speeches.pkl", "rb" ) )

def upload_to_mongo(scraped_list):
    """conneccts to mongo database 'speeches'. Uploads raw content from commencement
    speech web scraping into database."""

    client = MongoClient()

    # connect to database within mongoDB
    speech_db = client.speeches

    # add each speech to MongoDB
    for speech in scraped_content:
        speech_dict = {'name': speech[0],
                       'school': speech[1],
                       'year': speech[2],
                       'speech': speech[3]}
        speech_db.speech_collection.insert_one(speech_dict)

    print("All speeches uploaded to Mongo.")
    print("Speech count in Mongo:", speech_db.speech_collection.count())

    return

upload_to_mongo(scraped_content)

upload_to_mongo(manually_added_speeches)
