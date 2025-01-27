from pymongo import MongoClient
from orig_scoring import original_scoring, get_good_word_obj_bbn, get_bad_word_obj_bbn
from detect import detect, get_good_word_obj_dv, get_bad_word_obj_dv
import random
import time
from multiprocessing import Pool
from itertools import combinations

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"


# FIRST GET THE OBJECTS FOR GOOD WORDS AND BAD WORDS



def score(word, good_words, bad_words):
	return (word, original_scoring(word, get_good_word_obj_bbn(good_words), get_good_word_obj_bbn(bad_words)) + detect(word, good_words, bad_words))

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
	client = MongoClient(CONNECTION_STRING)
	codenames_db = client["codenames_db"]
	codenames_clues_collection = codenames_db["codenames_clues"]
	board_words = get_random_strings()
	good_words = []
	bad_words = []

	split_words(board_words, good_words, bad_words)

	print(good_words)
	print(bad_words)

	all_possible_combos = list(combinations(good_words, r=2))

	good_words_obj_cc = get_good_word_obj_bbn(good_words)
	bad_words_obj_cc = get_bad_word_obj_bbn(bad_words)
	
	good_words_obj_dvf = get_good_word_obj_dv(good_words)
	bad_words_obj_dvf = get_bad_word_obj_dv(bad_words)

	all_max_scores = []
	for word_choice in all_possible_combos:
		print(word_choice)

		word1_candidates = {key for key in list(codenames_clues_collection.find_one({"codenames_word": word_choice[0]}).get("single_word_clues").keys())}
		word2_candidates = {key for key in list(codenames_clues_collection.find_one({"codenames_word": word_choice[1]}).get("single_word_clues").keys())}


		intersection = list(word1_candidates & word2_candidates)

		score_list = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf)) for candidate_clue in intersection]

		# GET THE TOP 5 FOR EACH WORD
		all_max_scores.append((word_choice, sorted(score_list, key=lambda x: x[1], reverse = True)[0:5]))

	print(all_max_scores)
	print(time.time() - start_time)
	#print(word_choices)
	#print(sorted(score_list, key=lambda x: x[1], reverse = True)[0:10])
	# MIGHT ACTUALLY MAKE MORE SENSE TO NOT EVEN DO IT BECAUSE OF THE TIME REQUIRED TO HIT THE DB EACH TIME SINCE IT MIGHT NOT ACTUALLY CUT DOWN A LOT OF WORDS BECAUSE THEY COME OUT IN THE INTERSECTION
	#new_intersection = [word for word in intersection if get_frequency(word) > 30]

	#print(new_intersection)
	#print(len(new_intersection))

	# intersection2 = [(word, good_words, bad_words) for word in intersection]

	# #This does the multiprocessing stuff
	# with Pool(initializer= open_mongo_connection) as pool:
	# 	try:
	# 		#map score onto the tuples in new_intersection reading each as the args.
	# 		with_scores = pool.starmap(score, intersection2)

			
	# 		# with_scores = [(word, score(word, good_words, bad_words)) for word in new_intersection]
	# 		sorted_list_with_scores = sorted(with_scores, key=lambda x: x[1])
	# 		print(sorted_list_with_scores)

	# 		end_time = time.time()
	# 		num_mins = (end_time - start_time)/60

	# 		print(f"--- {num_mins} minutes ---")
	# 	finally:
    #         # Close worker connections after pool is done
	# 		pool.close()
	# 		pool.join()
	# 		close_mongo_connection() 