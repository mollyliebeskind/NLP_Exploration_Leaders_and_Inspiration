# Create a new column in the speeches dataframe with lemmatized words
lem = WordNetLemmatizer()

speeches['lemmatized_words'] = speeches.speech.apply(lambda x: x.split())
speeches.lemmatized_words = speeches.lemmatized_words.apply(lambda x: [lem.lemmatize(y) for y in x])
speeches.lemmatized_words = speeches.lemmatized_words.apply(lambda x: ' '.join(x))

def display_topics(model, feature_names, no_top_words, topic_names=None):
    """Displays each topic and the words that fall within them."""
    for ix, topic in enumerate(model.components_):
        if not topic_names or not topic_names[ix]:
            print("\nTopic ", ix)
        else:
            print("\nTopic: '",topic_names[ix],"'")
        print(", ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))

# create stop words list
def new_stopwords():
    my_stop_words = set(['like', 'know', 'im', 'just', 'thank', 'dont', 'youre', 'get', 'would', 'said', 'thats',
                         'think', 'say', 'things', 'us', 'going', 'way', 'really', 'well', 'many', 'got', 'right',
                         'something','thing', 'didnt', 'wa','one','went','wanted','ha','one','lot','mean', 'want',
                         'congratulations', 'commencement','staff','speaker','trustees','board','members',
                         'everything','guy', 'someone', 'everyone', 'ive', 'actually', 'theyre','youll', 'come', 'dr',
                         'anything', 'new', 'also', 'says', 'must', 'though','even', 'today', 'kind', 'hes', 'stuff',
                         'somebody', 'gon', 'york', 'day','women','men','woman','man','lets','id','guys', 'let','tell',
                         'cant','thought','great','look','always','cant','big','see','take','never','back','little',
                         'need','maybe','every','still','ever','two', 'around','honor', 'three','please','called',
                         'may', 'yeah','high', 'mr', 'better','part','good','first','show','feel','oh','else','whats',
                         'doesnt','sure','put','getting','later','wasnt','okay','knew', 'could', 'gonna', 'every',
                         'made', 'youve', 'much', 'theres', 'cover','none', 'acts', 'john','words','person',
                         'without', 'old', 'kid', 'order', 'everybody','ways', 'group','point', 'applause', 'adam',
                         'sarah','sara', 'bridge', 'finally', 'suppose', 'effect', 'excellent', 'probably','enough',
                         'thanks','guest','speak','turn','ago','since','havent','side','week','month', 'sense',
                         'others','days','days', 'mit', 'might', 'michael','william','david','story','place','real',
                         'word','told','away','next','came', 'find','harvard', 'number','done','night','doe','long',
                         'weve', 'talk','best','call','asked','another','keep','free','whether','end','wait','four',
                         'door','become', 'orleans', 'affect','meal', 'tap','step', 'girl','room','play', 'yes',
                         'start', 'true','last','wood','sort', 'sometimes','tony', 'michigan','sweet','small',
                         'parent','folk','mom','dad','song','child','took', 'pas', 'across','amount',
                         'car','eye','face','bit'])

    eng_stop_words = set(stopwords.words('english'))

    new_stopwords = eng_stop_words.union(my_stop_words)

    return new_stopwords

# use TF-IDF vectorizing
vectorizer = TfidfVectorizer(stop_words=new_stopwords, max_df=.8, min_df=.3, ngram_range=(1,1))
doc_term_object = vectorizer.fit_transform(speeches.lemmatized_words).toarray()

# create NMF object and transform the document term object created above
nmf = NMF(5, random_state=19)
doc_topic = nmf.fit_transform(doc_term_object)

#view top words in each topic
display_topics(nmf, vectorizer.get_feature_names(), 20)

# View results

#create dataframe of topic distrobutions per document to add onto the speeches dataframe
topic_columns = ['career','politics','education','hope','culture']
nmf_df = pd.DataFrame(doc_topic, columns=topic_columns)

#concatenate origonal speeches dataframe and topics dataframe
categorized_speeches = pd.concat((speeches.reset_index(), nmf_df),axis=1)

# remove columns with speech info (no longer needed for analysis)
categorized_speeches = categorized_speeches.drop(['lemmatized_words', 'index'], axis=1)

# create a column to indicate the top topic for each document
categorized_speeches['top_topic'] = categorized_speeches[topic_columns].idxmax(axis=1)

# view top topics per document
categorized_speeches.top_topic.value_counts()

# save the dataframe to access later
categorized_speeches.to_csv('topic_modeling_output.csv')

# plot the distrobution of top topics
x = list(categorized_speeches.top_topic.value_counts().index)
y = list(categorized_speeches.top_topic.value_counts())

chart = sns.barplot(x=x, y=y, color='#00274C')
plt.xlabel('Top Topic')
plt.ylabel('Count')
plt.title('Top Topic Distrobution')
sns.despine();

# plot with t-sne

def t_sne_prep(doc_term_object)
    """Takes in a document-term matrix created during topic modeling and returns a
    t-sne dataframe with two columns for 2-dimensional graphing and a labels column
    to indicate topic."""
    doc_term_df = pd.DataFrame(doc_term_object)

    ss = StandardScaler()
    doc_term_df = ss.fit_transform(nmf_df)

    tsne = TSNE(n_components=2, random_state=19, verbose=1, n_iter=2000, learning_rate=10)
    tsne_results = tsne.fit_transform(doc_term_df)

    #concat pca dataframe with the top topics per document
    t_sn_df = pd.concat((pd.DataFrame(tsne_results), categorized_speeches.top_topic), axis=1)
    t_sn_df = t_sn_df.rename(columns={0:'first',1:'second'})

    return t_sne_df

t_sne_df = t_sne_prep(doc_term_object)

# plot
fig = plt.figure(figsize=(10,8))
vis = sns.scatterplot(x=t_sn_df['first'], y=t_sn_df['second'], lw=0, s=40, hue=t_sn_df['top_topic'])
plt.xlim(-25, 25)
plt.ylim(-25, 25)
vis.legend(loc=3)
sns.despine();

# Explore by gender
# create separate dataframes for males and females
male_categorized_speeches = categorized_speeches[categorized_speeches.gender == '0']
female_categorized_speeches = categorized_speeches[categorized_speeches.gender == '1']

# compare percentage of each topic since the number of males > number of females
print('Top male topics:')
print(male_categorized_speeches.top_topic.value_counts(normalize=True))

print('Top female topics:')
print(female_categorized_speeches.top_topic.value_counts(normalize=True))

# create a dataframe with the topic distrobutions for men and women to visualize in Tableau
topic_distro = pd.DataFrame({'men': full_m.top_topic.value_counts(normalize=True), 'women': full_f.top_topic.value_counts(normalize=True)})

# export for visualization
topic_distro.to_csv('topic_distro_gender.csv')
