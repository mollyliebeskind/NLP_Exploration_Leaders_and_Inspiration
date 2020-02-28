#load data from mongodb
def pull_from_mongo():
    client = MongoClient()
    speech_db = client.speeches
    speech_collection = speech_db.speech_collection

    cursor = speech_collection.find()

    df = pd.DataFrame(list(cursor))

    return df

speeches = pull_from_mongo()

#clean text
def clean_text_round1(text):
    """Make text lowercase, remove text in square brackets,
    remove punctuation and remove words containing numbers."""

    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)

    return text

round1 = lambda x: clean_text_round1(x)
speeches.speech = speeches.speech.apply(round1)

def clean_text_round2(text):
    """Remove additional punctuation and non-sensical
    text that was missed the first time around."""
    text = re.sub('[‘’“”…]', '', text)
    text = re.sub('\n', ' ', text)
    return text

round2 = lambda x: clean_text_round2(x)
speeches.speech = speeches.speech.apply(round2)

#drop mongodb unique ID - not needed for analysis
speeches = speeches.drop('_id', axis=1)

# removing two speeches that downloaded in spanish
spanish_speeker1 = 'Henry A. Wallace'
spanish_speeker2 = 'Billy Collins'

speeches = speeches[speeches.name != spanish_speeker1]
speeches = speeches[speeches.name != spanish_speeker2]

# A few duplicates were loaded to Mongo - drop them and keep only the first occurance
speeches = speeches.drop_duplicates(keep='first')

#save cleaned data to csv file to access later
speeches.to_csv('speeches_df_basic_cleaning.csv')


# add gender column
# gender information grabbed manually and saved in pickled list
m_f_designation = pickle.load( open( "m_f_designation.pkl", "rb" ) )

# remove any \n new from string and split into a list
gender = re.sub('\n', ' ', m_f_designation).split(' ')

#create new column with speeker gender
speeches["gender"] = gender

# confirm column was added correctly
speeches.head()
