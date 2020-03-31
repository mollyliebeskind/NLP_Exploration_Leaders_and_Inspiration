""" This script performs Vader Sentiment Analysis on the full dataset of commencement
speeches and then consolidates results for male and female speeches.

Dataframes that are created in this script are exported for Tableau visualization. They include:
* overall_sentiment_analysis.csv
* mean_sentiment_per_gender.csv
"""

import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import  CountVectorizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from topic_modeling import new_stopwords

def split_speeches(data):
    """Returns the dataframe with ten new columns, each including a 10th of the origonal
    speech. This enables comparison of sentiment throughout the speech.
    """
    for n in range(10):
        data[f's{n}'] = data.speech.str.split().apply(lambda x: ' '.join(x[n*int(len(x)/10):
                                                                           (n+1)*int(len(x)/10)]))

    return data

def obtain_comp_score(data_with_splits):
    """Returns the dataframe with a new column indicating the sentiment analysis score for
    each section of the speech. For example, section 0 of the speech will have an output
    column 'comp0' that indicates the compilation sentiment score of seciton 0.
    """
    analyser = SentimentIntensityAnalyzer()

    for n in range(10):
        col = 's' + n
        new_col = 'comp' + col
        data_with_splits[new_col] = data_with_splits[col].apply(lambda x:
                                                                analyser.polarity_scores(x)
                                                                ['compound'])

    data_with_splits.to_csv('overall_sentiment_analysis.csv')

    return data_with_splits

def sentiment_by_gender(sentiment_data):
    """Prints the mean sentiment score by gender for each section of the speeches.
    Creates a dataframe of speech sentiment by gender and exports to csv to be used
    for Tableau visualization.
    """
    # view the average sentiment for each section of the speeches by gender
    sent_by_gender = sentiment_data.groupby('gender')['comps1', 'comps2', 'comps3',
                                                      'comps4', 'comps5', 'comps6',
                                                      'comps7', 'comps8', 'comps9',
                                                      'comps10'].agg(['mean'])
    print('Sentiment score by gender:', sent_by_gender)

    # create a dataframe of mean sentiment by gender to export for Tableau visualization
    sent_each = pd.DataFrame({'f':list(sent_by_gender.iloc[0, :].values),
                              'm': list(sent_by_gender.iloc[1, :].values)})
    sent_each.to_csv('mean_sentiment_per_gender.csv')


def top_words_single_section(data, section):
    """Returns the most commonly used words in a given section of a dataframe.

    Args:
    data -- a dataframe with sentiment analysis performed
    section -- the speech section to provide a list of top words for
    """

    cv = CountVectorizer(stop_words=new_stopwords(), ngram_range=(1, 1))
    data_cv = cv.fit_transform(data[section])

    data_dtm = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names())
    data_dtm.index = data.index

    top_words_ls = np.sum(data_dtm, axis=0).sort_values(ascending=False)

    return top_words_ls

def top_words_all_sections(data):
    """Prints a list of the most commonly used words in each of the ten
    sections of the speech.
    """

    for n in range(10):
        print(f"Top words in section {n}:")
        print(top_words_single_section(data, f's{n}')[:10])

def main():
    """Imports the commencement speeches, then breaks each speech into 10
    sections for sentiment analysis. Performs vader sentiment analysis on each
    section and then analyzes the results per gender.
    """
    model_output = pd.read_csv('topic_modeling_output.csv')
    split_df = split_speeches(model_output)
    sentiment_df = obtain_comp_score(split_df)
    sentiment_by_gender(sentiment_df)
    top_words_all_sections(sentiment_df)

main()
