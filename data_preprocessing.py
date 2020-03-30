"""This script pulls commencement speeches from MongoDB and preprocesses for topic modeling."""

import pickle
import re
import string

from pymongo import MongoClient
import pandas as pd

#load data from mongodb
def pull_from_mongo():
    """Returns a dataframe of commencement speeches stored in MongoDB."""

    client = MongoClient()
    speech_db = client.speeches
    speech_collection = speech_db.speech_collection

    cursor = speech_collection.find()

    speech_df = pd.DataFrame(list(cursor))

    return speech_df

#clean text
def clean_text_round1(text):
    """Return text with lowercase, removed text in square brackets,
    removed punctuation and remove words containing numbers.
    """

    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)

    return text

def clean_text_round2(text):
    """Return text with removed additional punctuation and non-sensical
    text that was not considered in the first time around.
    """
    text = re.sub('[‘’“”…]', '', text)
    text = re.sub('\n', ' ', text)
    return text

def clean_dataframe(speeches_df):
    """Returns the dataframe with duplicate values and non-enlgish transcripts removed."""
    #drop mongodb unique ID - not needed for analysis
    speeches_df = speeches_df.drop('_id', axis=1)

    # removing two speeches that downloaded in spanish
    spanish_speeker1 = 'Henry A. Wallace'
    spanish_speeker2 = 'Billy Collins'

    speeches_df = speeches_df[speeches_df.name != spanish_speeker1]
    speeches_df = speeches_df[speeches_df.name != spanish_speeker2]

    # A few duplicates were loaded to Mongo - drop them and keep only the first occurance
    speeches_df = speeches_df.drop_duplicates(keep='first')

    #save cleaned data to csv file to access later
    speeches_df.to_csv('speeches_df_basic_cleaning.csv')

    return speeches_df

def add_gender_column(cleaned_speeches_df):
    """Returns a dataframe of the cleaned speeches with the addition of a column indicating
    the speaker's sex. 1 represents female and 0 represents male.
    """

    # gender information stored in separate pickled document and saved in pickled list
    m_f_designation = pickle.load(open("m_f_designation.pkl", "rb"))

    # remove any \n new from string and split into a list
    gender = re.sub('\n', ' ', m_f_designation).split(' ')

    #create new column with speeker gender
    cleaned_speeches_df["gender"] = gender

    return cleaned_speeches_df

def main():
    """Loads speech data from MongoDB database, cleans transcript text and dataset, then saves
    the dataframe as a csv file.
    """
    # Pull speeches from mongodb and store as df
    speeches = pull_from_mongo()

    # Text cleaning
    speeches.speech = speeches.speech.apply(lambda x: clean_text_round1(x))
    speeches.speech = speeches.speech.apply(lambda x: clean_text_round2(x))

    # Dataframe cleaning
    cleaned_speeches = clean_dataframe(speeches)
    cleaned_speeches = add_gender_column(cleaned_speeches)

    cleaned_speeches.to_csv('cleaned_speeches.csv')

main()
