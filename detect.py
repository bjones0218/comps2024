from scipy.spatial.distance import cosine
from pymongo import MongoClient


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"
client = MongoClient(CONNECTION_STRING)

dict2vec_db = client["dict2vec"]
dict2vec_collection = dict2vec_db["dict2vec_collection"]

wiki_freq_db = client["wiki_freq"]
wiki_freq_collection = wiki_freq_db["wiki_freq_collection"]

def detect(clue: str, good_words: list, bad_words: list) -> float:
	lambda_f = 2 # We will have to figre out good values for this
	lambda_d = 2 # And this

	freq_val = lambda_f * freq(clue) # Penalizes overly frequent words more and very rare words more

	good_words_val = 0
	for good_word in good_words:
		good_words_val = good_words_val + 1 - dist(clue, good_word)
	bad_words_val = 0
	for bad_word in bad_words:
		current_val = 1 - dist(clue, bad_word)
		if current_val > bad_words_val:
			bad_words_val = current_val
	dict_val = lambda_d * (good_words_val - bad_words_val)

	return freq_val + dict_val



def freq(word: str) -> float:
	# Calculate document frequency of word which was done in paper from what number of cleaned wikipedia articles the word was found in
	# Empirically calculated alpha to be 1/1667 in paper
	alpha = 1/1667 # This might have to change if we arent getting enough common words and I think it should change
	frequency = get_frequency(word)
	if frequency == 0: # Word is way too rare so penalize a lot
		return -1
	else: 
		if (1/frequency) >= alpha: # Word is too rare
			return -(1/frequency)
		else: # Word is too common
			return -1

def get_frequency(word):
	# Queries the database of frequencies of words and returns the value

	wiki_freq_db_obj = wiki_freq_collection.find_one({"word": word})
	if wiki_freq_db_obj:
		return wiki_freq_db_obj.get("count")
	else:
		return 0


def dist(word1: str, word2: str) -> float:
	# This is the cosine distance between the dict to vec word embeddings for each word


	vec1_obj = dict2vec_collection.find_one({"word": word1})
	vec2_obj = dict2vec_collection.find_one({"word": word2})

	if vec1_obj and vec2_obj:
		vec1 = vec1_obj.get("vector")
		vec2 = vec2_obj.get("vector")
		return cosine(vec1, vec2)
	else:
		return 2



