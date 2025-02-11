from scipy.spatial.distance import cosine
from pymongo import MongoClient


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"
client = MongoClient(CONNECTION_STRING)
freq_and_vec_db2 = client["freq_and_vec2"]
freq_and_vec_collection2 = freq_and_vec_db2["freq_and_vec_collection2"]

def get_good_word_obj_dv(good_words):
	return {word: freq_and_vec_collection2.find_one({"word": word}) for word in good_words}

def get_bad_word_obj_dv(bad_words):
	return {word: freq_and_vec_collection2.find_one({"word": word}) for word in bad_words}


# SHOULD MAYBE OPTIMIZE THIS TO TAKE IN ALL OF THE CANDIDATE CLUES
def detect(clue: str, good_words_obj_dv: dict, bad_words_obj_dv: dict) -> float:
	lambda_f = 2 # We will have to figre out good values for this
	lambda_d = 2 # And this

	client = MongoClient(CONNECTION_STRING)
	freq_and_vec_db2 = client["freq_and_vec2"]
	freq_and_vec_collection2 = freq_and_vec_db2["freq_and_vec_collection2"]

	# print(clue)

	clue_db_obj = freq_and_vec_collection2.find_one({"word": clue})
	if clue_db_obj:
		clue_vec = clue_db_obj.get("vector")
		frequency = clue_db_obj.get("count")
	else:
		clue_vec = None
		frequency = 0

	alpha = 1/300000 # NEEDS TO CHANGE

	if frequency == 0: # Word is way too rare so penalize a lot
		freq_val = -1
	else: 
		if (1/frequency) >= alpha: # Word is too rare
			freq_val = -(1/frequency)
		else: # Word is too common
			freq_val = -1

	freq_score = lambda_f * freq_val # Penalizes overly frequent words more and very rare words more

	good_word_distances = [1 - dist(clue_vec, good_word.get("vector")) for good_word in good_words_obj_dv.values()]
	# print(good_word_distances)
	bad_word_distances = [1 - dist(clue_vec, bad_word.get("vector")) for bad_word in bad_words_obj_dv.values()]
	# print(bad_word_distances)
	good_words_val = sum(good_word_distances)
	bad_words_val = max(bad_word_distances)

	dict_val = lambda_d * (good_words_val - bad_words_val)

	return freq_score + dict_val


def dist(word1_vec: list, word2_vec: list) -> float:
	# This is the cosine distance between the dict to vec word embeddings for each word
	if word1_vec and word2_vec:
		return cosine(word1_vec, word2_vec)
	else:
		return 2


