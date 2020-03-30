"""
This script is used to perform topic modeling on NPR's top 350 speeches using non-negative matrix
factorization, a TF-IDF vectorizer, and lemmatized transcripts.
"""

import pandas as pd

from sklearn.feature_extraction.text import  TfidfVectorizer
from sklearn.decomposition import NMF

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def create_lemmatized_words(speeches_df):
    """Returns the dataframe with an additional column with the lemmatized transcript."""

    lem = WordNetLemmatizer()

    speeches_df['lemmatized_words'] = speeches_df.speech.apply(lambda x: x.split())
    speeches_df.lemmatized_words = speeches_df.lemmatized_words.apply(lambda x: [lem.lemmatize(y)
                                                                                 for y in x])
    speeches_df.lemmatized_words = speeches_df.lemmatized_words.apply(lambda x: ' '.join(x))

    return speeches_df

# create stop words list
def new_stopwords():
    """Returns a list of of stop words that joins a custom list with the standard english
    stop words.
    """

    my_stop_words = set(['like', 'know', 'im', 'just', 'thank', 'dont', 'youre', 'get', 'would',
                         'said', 'thats', 'think', 'say', 'things', 'us', 'going', 'way', 'really',
                         'well', 'many', 'got', 'right', 'something', 'thing', 'didnt', 'wa', 'one',
                         'went', 'wanted', 'ha', 'one', 'lot', 'mean', 'want', 'congratulations',
                         'commencement', 'staff', 'speaker', 'trustees', 'board', 'members',
                         'everything', 'guy', 'someone', 'everyone', 'ive', 'actually', 'theyre',
                         'youll', 'come', 'dr', 'anything', 'new', 'also', 'says', 'must', 'though',
                         'even', 'today', 'kind', 'hes', 'stuff', 'somebody', 'gon', 'york', 'day',
                         'women', 'men', 'woman', 'man', 'lets', 'id', 'guys', 'let', 'tell',
                         'cant', 'thought', 'great', 'look', 'always', 'cant', 'big', 'see', 'take',
                         'never', 'back', 'little', 'need', 'maybe', 'every', 'still', 'ever',
                         'two', 'around', 'honor', 'three', 'please', 'called', 'may', 'yeah',
                         'high', 'mr', 'better', 'part', 'good', 'first', 'show', 'feel', 'oh',
                         'else', 'whats', 'knew', 'could', 'none', 'acts', 'bridge', 'everybody',
                         'doesnt', 'sure', 'put', 'getting', 'later', 'wasnt', 'okay',
                         'gonna', 'every', 'made', 'youve', 'much', 'theres', 'cover',
                         'john', 'words', 'person', 'without', 'old', 'kid', 'order',
                         'ways', 'group', 'point', 'applause', 'adam', 'sarah', 'sara',
                         'finally', 'suppose', 'effect', 'excellent', 'probably', 'enough',
                         'thanks', 'guest', 'speak', 'turn', 'ago', 'since', 'havent', 'side',
                         'week', 'william', 'came', 'talk', 'wait', 'girl', 'sometimes', 'song',
                         'month', 'sense', 'others', 'days', 'days', 'mit', 'might', 'michael',
                         'david', 'story', 'place', 'real', 'word', 'told', 'away', 'next',
                         'find', 'harvard', 'number', 'done', 'night', 'doe', 'long', 'weve',
                         'best', 'call', 'asked', 'another', 'keep', 'free', 'whether', 'end',
                         'four', 'door', 'become', 'orleans', 'affect', 'meal', 'tap', 'step',
                         'room', 'play', 'yes', 'start', 'true', 'last', 'wood', 'sort',
                         'tony', 'michigan', 'sweet', 'small', 'parent', 'folk', 'mom', 'dad',
                         'child', 'took', 'pas', 'across', 'amount', 'car', 'eye', 'face', 'bit'])

    eng_stop_words = set(stopwords.words('english'))
    all_stopwords = eng_stop_words.union(my_stop_words)

    return all_stopwords

def display_topics(model, feature_names, no_top_words, topic_names=None):
    """Helper function for viewing topic modeling results. Displays each topic and
    the top n words that fall within them.

    Args:
    model -- the model used for topic modeling
    feature_names -- feature names in the document terms matrix (words used in each script)
    no_top_words -- number of top words to be returned
    topic_names -- if specific names are assigned to each topic, displays them
    """
    for i, topic in enumerate(model.components_):
        if not topic_names or not topic_names[i]:
            print("\nTopic ", i)
        else:
            print("\nTopic: '", topic_names[i], "'")
        print(", ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))

def save_topic_modeling_results(data, fit_model):
    """Returns a dataframe with the results of the topic modeling for each speech concatenated
    onto the origonal dataframe. Saves this dataframe as a csv for later accessing.

    Args:
    data -- the dataframe used for topic modeling
    fit_model -- the nmf model used for topic modeling
    """

    #create dataframe of topic distrobutions per document to add onto the speeches dataframe
    topic_columns = ['career', 'politics', 'education', 'hope', 'culture']
    nmf_df = pd.DataFrame(fit_model, columns=topic_columns)

    #concatenate origonal speeches dataframe and topics dataframe
    categorized_speeches = pd.concat((data.reset_index(), nmf_df), axis=1)
    categorized_speeches['top_topic'] = categorized_speeches[topic_columns].idxmax(axis=1)
    print("Number of speeches per topic:\n", categorized_speeches.top_topic.value_counts())

    # remove columns with speech info (no longer needed for analysis)
    categorized_speeches = categorized_speeches.drop(['lemmatized_words', 'index'], axis=1)

    # save the dataframe for Tableau visualizations
    categorized_speeches.to_csv('topic_modeling_output.csv')

    return categorized_speeches

def topic_modeling(data):
    """Performs topic modeling using a TF-IDF vectorizer, lemmatization, non-negative matrix
    factorization, a custom list of stop words, and 5 topics. Returns a dataframe with
    the top topic for each speech indicated in a separate column.
    """

    lemmatized_df = create_lemmatized_words(data)
    stop_words = new_stopwords()

    # Use TF-IDF vectorizing
    vectorizer = TfidfVectorizer(stop_words=stop_words, max_df=.8, min_df=.3, ngram_range=(1, 1))
    doc_term_object = vectorizer.fit_transform(data.lemmatized_words).toarray()

    # create NMF object and transform the document term object created above
    nmf = NMF(5, random_state=19)
    doc_topic = nmf.fit_transform(doc_term_object)

    # View top words in each topic
    display_topics(nmf, vectorizer.get_feature_names(), 20)

    # Create a dataframe with the top topic for each speach indicated
    top_topic_per_speech = save_topic_modeling_results(lemmatized_df, doc_topic)

    return top_topic_per_speech

def compare_genders(categorized_speeches):
    """Prints the topic distrobution for male and female speakers and creates a dataframe with
    the topic distrobitons for each gender. Exports the dataframe as a csv file for Tableau
    visualization.
    """

    # create separate dataframes for males and females
    male_speeches = categorized_speeches[categorized_speeches.gender == '0']
    female_speeches = categorized_speeches[categorized_speeches.gender == '1']

    # compare percentage of each topic since the number of males > number of females
    print('Top male topics:')
    print(male_speeches.top_topic.value_counts(normalize=True))

    print('Top female topics:')
    print(female_speeches.top_topic.value_counts(normalize=True))

    # create a dataframe with the topic distrobutions for men and women to visualize in Tableau
    topic_distro = pd.DataFrame({'men': male_speeches.top_topic.value_counts(normalize=True),
                                 'women': female_speeches.top_topic.value_counts(normalize=True)})
    topic_distro.to_csv('topic_distro_gender.csv')

def main():
    """Loads the commencement speech dataframe, calls NMF topic modeling function that includes
    lemmatizaiton and TF-IDF vectorization. Creates a dataframe to compare the results for male
    and female speakers.
    """
    transcripts_df = pd.read_csv('cleaned_speeches.csv')
    top_topics = topic_modeling(transcripts_df)
    compare_genders(top_topics)
