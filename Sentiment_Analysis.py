# Vader Sentiment analysis

# Full speech analysis
# create a copy in case of needing to revert to previous state
sent_df = categorized_speeches.copy()

analyser = SentimentIntensityAnalyzer()

# for each of the speeches, create columns for the four sentiments captured by Vader to analyze
sent_df['pos'] = sent_df.speech.apply(lambda x: analyser.polarity_scores(x)['pos'])
sent_df['neg'] = sent_df.speech.apply(lambda x: analyser.polarity_scores(x)['neg'])
sent_df['neu'] = sent_df.speech.apply(lambda x: analyser.polarity_scores(x)['neu'])
sent_df['comp'] = sent_df.speech.apply(lambda x: analyser.polarity_scores(x)['compound'])

# view and compare results for each gender
sent_df.groupby('gender')['pos','neg','neu','compount'].agg(['mean'])

# By Section
# create a copy in case of needing to revert to previous state. Maintain only gender and speech
# columns to avoid clutter
sent_df_split = categorized_speeches[['gender','speech']]

# split speeches into 10 sections, each is a new column to keep the speech together
sent_df_split['s1'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[0:int(len(x)/10)]))
sent_df_split['s2'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[int(len(x)/10):2*int(len(x)/10)]))
sent_df_split['s3'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[2*int(len(x)/10):3*int(len(x)/10)]))
sent_df_split['s4'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[3*int(len(x)/10):4*int(len(x)/10)]))
sent_df_split['s5'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[4*int(len(x)/10):5*int(len(x)/10)]))
sent_df_split['s6'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[5*int(len(x)/10):6*int(len(x)/10)]))
sent_df_split['s7'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[6*int(len(x)/10):7*int(len(x)/10)]))
sent_df_split['s8'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[7*int(len(x)/10):8*int(len(x)/10)]))
sent_df_split['s9'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[8*int(len(x)/10):9*int(len(x)/10)]))
sent_df_split['s10'] = sent_df_split.speech.str.split().apply(lambda x: ' '.join(x[9*int(len(x)/10):10*int(len(x)/10)]))

def obtain_comp_score(data, col):
    """Takes in a dataframe and column and return the compound sentiment score for the text
    in that column. Used to obtain sentiment scores for the 10 smaller sections of the
    commencement speecches."""

    new_col_name = 'comp' + col
    data[new_col_name] = data[col].apply(lambda x: analyser.polarity_scores(x)['compound'])
    return data

sent_df_split = obtain_comp_score(sent_df_split, 's1')
sent_df_split = obtain_comp_score(sent_df_split, 's2')
sent_df_split = obtain_comp_score(sent_df_split, 's3')
sent_df_split = obtain_comp_score(sent_df_split, 's4')
sent_df_split = obtain_comp_score(sent_df_split, 's5')
sent_df_split = obtain_comp_score(sent_df_split, 's6')
sent_df_split = obtain_comp_score(sent_df_split, 's7')
sent_df_split = obtain_comp_score(sent_df_split, 's8')
sent_df_split = obtain_comp_score(sent_df_split, 's9')
sent_df_split = obtain_comp_score(sent_df_split, 's10')

# view the average sentiment for each section of the speeches by gender
sent_by_gender = sent_df_split.groupby('gender')['comps1',
                                                'comps2',
                                                'comps3',
                                                'comps4',
                                                'comps5',
                                                'comps6',
                                                'comps7',
                                                'comps8',
                                                'comps9',
                                                'comps10'].agg(['mean'])

# create a dataframe of mean sentiment by gender to export for Tableau visualization
sent_each = pd.DataFrame({'f':list(sent_by_gender.iloc[0,:].values) ,
                          'm': list(sent_by_gender.iloc[1,:].values)})

# export for vis
sent_each.to_csv('mean_sentiment_per_gender.csv')

# view the overall top words per section to have an idea of where sentiment change is derived from

def top_words_by_section(data, section):
    """Takes in a dataframe and a section and returns the most commonly used words within
    that section."""
    cv = CountVectorizer(stop_words=create_stopwords(), ngram_range=(1,1))
    data_cv = cv.fit_transform(data[section])

    data_dtm = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names())
    data_dtm.index = data.index

    top_words_ls = np.sum(data_dtm, axis=0).sort_values(ascending=False)

    return top_words_ls

# view top words in section 1
print("Top words in section 1:'\n'", top_words_by_section(sent_df_split, 's1')[:20], '\n')

# view top words in a middle section
print("Top words in section 5:'\n'", top_words_by_section(sent_df_split, 's5')[:20], '\n')

# view top words in a section 10
print("Top words in section 10:'\n'", top_words_by_section(sent_df_split, 's10')[:20])

# IBM Watson Tone Analysis
# IBM_API_KEY = os.environ['IBM_API_KEY']

from ibm_connect import ibm_connnection()

# connect to ibm with authentication key stored in separate .py file (ibm_comment)
imb_connection()

# re-pull dataset from MongoDB because IBM's Tone Analyzer leverages sentence structure and
# periods were stripped away during cleaning

ibm_df = pull_from_mongo()

def clean_text_ibm(text):
    """Remove text in square brackets and remove words containing numbers."""

    text = re.sub('\[.*?\]', '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[‘’“”…:"\"><]', '', text)
    text = re.sub('\n', ' ', text)
    return text

ibm_round = lambda x: clean_text_for_ibm(x)
ibm_df.speech = speeches.speech.apply(ibm_round)

# repeat other data touch ups
ibm_df = ibm_df.drop('_id', axis=1)

spanish_speeker1, spanish_speeker2 = 'Henry A. Wallace', 'Billy Collins'
ibm_df = ibm_df[ibm_df.name != spanish_speeker1]
ibm_df = ibm_df[ibm_df.name != spanish_speeker2]

ibm_df = ibm_df.drop_duplicates(keep='first')

# add gender column back in
m_f_designation = pickle.load( open( "m_f_designation.pkl", "rb" ) )
gender = re.sub('\n', ' ', m_f_designation).split(' ')
ibm_df["gender"] = gender

# due to YouTube transcripts, many of the speeches do not include periods. To isolate those
# that do, create a column that indicates the number of sentences per speech.
ibm_df['sent_len'] = ibm_df.speech.apply(lambda x: len(sent_tokenize(x)))

# select only those with a reasonable amount of sentences
ibm_df_use = ibm_df[ibm_df.sent_len >= 50]

# create separate dataframes for male and female to run through Watson as gender information
# will otherwise be lost
f_for_ibm = ibm_df_use[ibm_df_use.gender =='1']
m_for_ibm = ibm_df_use[ibm_df_use.gender =='0']

# run watson for female speeches and store in result list
resp_f_ls = []

for s in f_for_ibm.speech:
    resp = tone_analyzer.tone(
        {'text': s},
        content_type='application/json',
        sentences=False
    )

    resp_f_ls.append(resp.result)

# run watson for male speeches and store in result list
resp_m_ls = []

for s in m_for_ibm.speech:
    resp = tone_analyzer.tone(
        {'text': s},
        content_type='application/json',
        sentences=False
    )

    resp_m_ls.append(resp.result)

# Watson output is a dictionary of dictionaries. Access information on tone and store
# as a new dataframe for easier accessing

# create female df & and add gender indicator column
start_f_df = pd.DataFrame.from_dict(resp_f_ls[0]['document_tone']['tones'])
for i in range(1, len(resp_f_ls)):
    start_f_df = pd.concat((start_f_df, pd.DataFrame.from_dict(resp_f_ls[i]['document_tone']['tones'])), axis=0)

start_f_df['gender'] = '1'

# create male df and add gender indicator column
start_m_df = pd.DataFrame.from_dict(resp_m_ls[0]['document_tone']['tones'])
for i in range(len(resp_m_ls)):
    start_m_df = pd.concat((start_m_df, pd.DataFrame.from_dict(resp_m_ls[i]['document_tone']['tones'])), axis=0)

start_m_df['gender'] = '0'

# concatenate the male and female dataframes and export to csv for Tableau visualization
full_sent_df = pd.concat((start_f_df, start_m_df), axis=0)

full_sent_df.to_csv('full_sent_df.csv')
