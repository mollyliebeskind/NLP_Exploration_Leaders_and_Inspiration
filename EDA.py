# Find the number of words in each document
# Start with full document
def length_of_speeches(data):
    """creates new column with speech length for each speech"""

    data['speech_len'] = data.speech.apply(lambda x: x.split())
    data['speech_len'] = data.speech_len.apply(lambda x: len(x))

    return data

speeches = length_of_speeches(speeches)

# quickly visualize the distrobution
plt.hist(speeches.speech_len, bins=50)
plt.title('Distrobution of Speech Lengths')
plt.xaxis('Speech Length')
plt.yaxis('Count');

# find the longest, shortest, and average speech length
print("Min", np.min(speeches.speech_len))
print("Max", np.max(speeches.speech_len))
print("Mean", np.mean(speeches.speech_len))

speeches.speech_len.describe([.03, .25, .75])

# Remove speeches that are less than 500 words (errors in scraping)
speeches = speeches[speeches.speech_len > 500]

print(speeches.speech_len.describe())

# Explore length of speech for each gender
# Create Male only DF
males = speeches[speeches.gender == '0']

# Create femail only DF
female = speeches[speeches.gender == '1']

print(f"There are {len(males)} males and {len(female)} females in the dataset")

# plot a histogram of the length of speeches for males and females

plt.hist(female.speech_length, bins=50, alpha=.3, label='female')
plt.hist(males.speech_length, bins=50, alpha=.4, label='male')
plt.xaxis('Speech Length')
plt.yaxis('Count')
plt.title('Length of Speeches for Males and Females')
plt.legend();

print('Average speech length for females:', np.mean(female.speech_length))
print('Average speech length for males:', np.mean(males.speech_length))


# Identify most commonly used words
# first overall for full dataset

#Create simple document-term matrix to explore common words
def simple_doc_term():
    cv = CountVectorizer(stop_words='english', ngram_range=(1,1))
    data_cv = cv.fit_transform(speeches.speech)
    data_dtm = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names())
    data_dtm.index = speeches.index
    return data_dtm

data_dtm = simple_doc_term()

#top 20 most commonly said words
np.sum(data_dtm, axis=0).sort_values(ascending=False)[:20]

# most of these are not meaningful and will be added to stop words list
# view the next set of 20 for more information
np.sum(data_dtm, axis=0).sort_values(ascending=False)[20:40]

# gender specific
female_dtm = simple_doc_term(female)
male_dtm = simple_doc_term(males)

top_female_words = np.sum(female_dtm, axis=0).sort_values(ascending=False)[:20]
top_male_words = np.sum(male_dtm, axis=0).sort_values(ascending=False)[:20]

print("Top female words:")
print(top_female_words)

print("Top male words:")
print(top_male_words)
