from pymongo import MongoClient
import spacy


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"
client_global = MongoClient(CONNECTION_STRING)

codenames_db_global = client_global["codenames_db"]
words_collection_global = codenames_db_global["codenames_clues"]

freq_and_vec_db_global = client_global["freq_and_vec2"]
freq_and_vec_collection_global = freq_and_vec_db_global["freq_and_vec_collection2"]

nlp = spacy.load("en_core_web_sm")

def get_words_collection(client, both_words):
	codenames_db = client["codenames_db"]
	words_collection = codenames_db["codenames_clues"]
	first_word_list = list(words_collection.find_one({"codenames_word": both_words[0]}).get("single_word_clues").keys())
	second_word_list = list(words_collection.find_one({"codenames_word": both_words[1]}).get("single_word_clues").keys())

	return (first_word_list, second_word_list)


def get_word_obj_bbn(words):
	return {word: words_collection_global.find_one({"codenames_word": word}) for word in words}

def get_single_bbn_obj(word):
	return words_collection_global.find_one({"codenames_word": word})

def get_word_obj_dv(words):
	return {word: freq_and_vec_collection_global.find_one({"word": word}) for word in words}

def get_single_dv_obj(client, word):
	freq_and_vec_db = client["freq_and_vec2"]
	freq_and_vec_collection = freq_and_vec_db["freq_and_vec_collection2"]

	return freq_and_vec_collection.find_one({"word": word})


def get_dv_objs(client, words):
	freq_and_vec_db = client["freq_and_vec2"]
	freq_and_vec_collection = freq_and_vec_db["freq_and_vec_collection2"]

	to_return = []
	for word in words:
		to_return.append((word, freq_and_vec_collection.find_one({"word": word})))

	return to_return


# TEST THIS SOME MORE
def check_top_clues(clue_list):
	bad_top_word = True
	cur_word_index = 0
	while bad_top_word:
		top_word_doc = nlp(clue_list[cur_word_index][1][0].lower())
		top_word_lemma = top_word_doc[0].lemma_

		first_word_doc = nlp(clue_list[cur_word_index][0][0].lower())
		second_word_doc = nlp(clue_list[cur_word_index][0][1].lower())
		first_word_lemma = first_word_doc[0].lemma_
		second_word_lemma = second_word_doc[0].lemma_
		if top_word_lemma == first_word_lemma or top_word_lemma == second_word_lemma:
			cur_word_index += 1
		else:
			bad_top_word = False
	
	return clue_list[cur_word_index]