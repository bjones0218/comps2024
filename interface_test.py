from pymongo import MongoClient
from orig_scoring import original_scoring
from detect import detect, get_frequency
import random
import time
from multiprocessing import Pool

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"
client = MongoClient(CONNECTION_STRING)
codenames_db = client["codenames_db"]

def score(word, good_words, bad_words):
	return (word, original_scoring(word, good_words, bad_words) + detect(word, good_words, bad_words))

def get_random_strings():
	with open("word_list_copy.txt", 'r') as file:
		lines = file.readlines()
	return random.sample(lines, 25)

def split_words(words, good_words, bad_words):

	unvisited = set(range(len(words)))
	for i in range(len(words)):
		index = random.choice(list(unvisited))
		word = words[index].strip()
		if i % 2 == 0: #this cause red to have one more in odd num sized boards
			good_words.append(word)
		else:
			bad_words.append(word)
		unvisited.remove(index)

if __name__ == "__main__":
	start_time = time.time()
	codenames_clues_collection = codenames_db["codenames_clues"]
	board_words = get_random_strings()
	good_words = []
	bad_words = []

	split_words(board_words, good_words, bad_words)

	print(good_words)
	print(bad_words)

	word_choices = random.sample(good_words, 2)
	print(word_choices)

	#this takes a while... multiprocessing as well??
	word1_candidates = [key for key in codenames_clues_collection.find_one({"codenames_word": word_choices[0]}).get("single_word_clues").keys()]
	word2_candidates = [key for key in codenames_clues_collection.find_one({"codenames_word": word_choices[1]}).get("single_word_clues").keys()]

	intersection = list(set(word1_candidates) & set(word2_candidates))
	new_intersection = []

	for word in intersection:
		if get_frequency(word) > 30:
			#puts as a tuple so pool.starmap reads in as multiple args
			new_intersection.append((word, good_words, bad_words))

	# print(new_intersection)
	print(len(new_intersection))

	#This does the multiprocessing stuff
	with Pool() as pool:
		#map score onto the tuples in new_intersection reading each as the args.
		with_scores = pool.starmap(score, new_intersection)

	
	# with_scores = [(word, score(word, good_words, bad_words)) for word in new_intersection]
	sorted_list_with_scores = sorted(with_scores, key=lambda x: x[1])
	print(sorted_list_with_scores)

	end_time = time.time()
	num_mins = (end_time - start_time)/60

	print(f"--- {num_mins} minutes ---")