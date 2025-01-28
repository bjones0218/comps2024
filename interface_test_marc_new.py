from pymongo import MongoClient
import random
import time
from multiprocessing import Pool
from itertools import combinations
from scipy.spatial.distance import cosine


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"
client = MongoClient(CONNECTION_STRING)
db = client["codenames_db"]
words_collection = db["codenames_clues"]
freq_and_vec_db2 = client["freq_and_vec2"]
freq_and_vec_collection2 = freq_and_vec_db2["freq_and_vec_collection2"]

# FIRST GET THE OBJECTS FOR GOOD WORDS AND BAD WORDS

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

def get_good_word_obj_bbn(good_words):
	return {word: words_collection.find_one({"codenames_word": word}) for word in good_words}

def get_bad_word_obj_bbn(bad_words):
	return {word: words_collection.find_one({"codenames_word": word}) for word in bad_words}

def get_score(clue_obj):
	if clue_obj:
		return 1 / (clue_obj[0] * (clue_obj[1] + 1))
	else: 
		return 0
	

def original_scoring(clue, good_words_obj_bbn: dict, bad_words_obj_bbn: dict):
	lambda_good = 1
	lambda_bad = 0.5

	# MAYBE SHOULD ADD 1 INSIDE BUT NOT SURE WE SHOULD CHECK ON THAT BECAUSE IT DEPENDS ON HOW PAPER IS INTERPRETED
	
	# CURRENT PROBLEM: WE HAVE A TON OF CANDIDATE CLUES THAT DO NOT EXIST FOR EVERY WORD ON THE BOARD IN THE DB BECAUSE THEY ARE TOO FAR AWAY SO RN IT CRASHES
	# SOLUTION? Maybe we just make that a big value if it doesn't exist in the db? 
	# FOR EXAMPLE: Candidate clue of "DOG" with a board word of "CHRISTMAS" and "DOG" is not within 3 edges of "CHRISTMAS" so in the db you cannot find "DOG" attached to "CHRISTMAS"

	# BUT THEN WHY WAS IT WORKING BEFORE AND JUST TAKIgNG A LONG TIME???
	# MAYBE JUST THE IF STATEMENT ERROR CHECKING FROM BEFORE I REWROTE THE CODE BUT THATS THE WRONG WAY TO DO IT
	# BECAUSE THEN IF A WORD IS SUPER UNRELATED IT DOESNT EXIST WITHIN 3 LEVELS OF THE GRAPH SO IT GETS A SCORE OF 0 AND THEN GETS A 1/1 SO NEED TO JUST PUT 0 IN
	
	#print(good_words_obj_bbn.values())

	good_score_array = [get_score(good_word_obj.get('single_word_clues').get(clue)) for good_word_obj in good_words_obj_bbn.values()]
	# good_score_array = [1 / ((good_word_obj.get('single_word_clues').get(clue)[0] * good_word_obj.get('single_word_clues').get(clue)[1]) + 1) if good_word_obj.get('single_word_clues').get(clue) else 0 for good_word_obj in good_words_obj_bbn.values()]
	good_score = sum(good_score_array)
	# good_score = 0



	bad_score_array = [get_score(bad_word_obj.get('single_word_clues').get(clue)) for bad_word_obj in bad_words_obj_bbn.values()]
	# bad_score_array = [1 / ((bad_word_obj.get('single_word_clues').get(clue)[0] * bad_word_obj.get('single_word_clues').get(clue)[1]) + 1) if bad_word_obj.get('single_word_clues').get(clue) else 0 for bad_word_obj in bad_words_obj_bbn.values()]
	bad_score = max(bad_score_array)
	#print(bad_score_array)

	clue_score = (lambda_good * good_score) - (lambda_bad * bad_score)

	return clue_score


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

	alpha = 1/1800000

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

	# good_words = ['GRACE', 'CENTER', 'COPPER', 'SINK', 'MOUNT', 'DRESS', 'WAKE', 'TOWER', 'ANGEL', 'BARK', 'ROSE', 'CARD', 'DICE']
	# bad_words = ['WITCH', 'WHALE', 'RULER', 'OLYMPUS', 'DEGREE', 'SPINE', 'CRANE', 'SHAKESPEARE', 'NET', 'BATTERY', 'TRIP', 'WHIP']

	all_possible_combos = list(combinations(good_words, r=2))
	print(len(all_possible_combos))

	good_words_obj_cc = get_good_word_obj_bbn(good_words)
	bad_words_obj_cc = get_bad_word_obj_bbn(bad_words)
	
	good_words_obj_dvf = get_good_word_obj_dv(good_words)
	bad_words_obj_dvf = get_bad_word_obj_dv(bad_words)

	# word1_candidates2 = {key for key in list(codenames_clues_collection.find_one({"codenames_word": "GRACE"}).get("single_word_clues").keys())}
	# word2_candidates2 = {key for key in list(codenames_clues_collection.find_one({"codenames_word": "ANGEL"}).get("single_word_clues").keys())}

	# intersection2 = list(word1_candidates2 & word2_candidates2)
	# print(len(intersection2))

	# score_list_that_answers_all_questions2 = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf)) for candidate_clue in intersection2]

	# print(len(score_list_that_answers_all_questions2))
	# print(good_words)
	# print(bad_words)

	# score_list5 = score_list_that_answers_all_questions2.copy()
	# score_list5.sort(key=lambda x: x[1], reverse=True)
	# print(score_list5[0:5])


	all_max_scores = []
	for word_choice in all_possible_combos:
		print(word_choice)
		print(get_score([1.2, 2]))

		word1_candidates = {key for key in list(codenames_clues_collection.find_one({"codenames_word": word_choice[0]}).get("single_word_clues").keys())}
		word2_candidates = {key for key in list(codenames_clues_collection.find_one({"codenames_word": word_choice[1]}).get("single_word_clues").keys())}

		

		# print(list(word1_candidates)[0:10])
		# print(list(word2_candidates)[0:10])

		intersection = list(word1_candidates & word2_candidates)
		# NOTE: These are called angry words because they make me angry (⩺_⩹)
		angry_words = ["WBM", "WAYBACK", "WAYBACKMACHINE", "ISBN", "ISBNS", "EISBN", "ESBN", "WAYBACKED"]
		for angry_word in angry_words:
			if angry_word in intersection:
				intersection.remove(angry_word)

		score_list_that_answers_all_questions = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf)) for candidate_clue in intersection]
		score_list = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc), detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf)) for candidate_clue in intersection]

		score_list2 = score_list.copy()
		score_list3 = score_list.copy()
		score_list2.sort(key= lambda x: x[1], reverse=True)
		score_list3.sort(key= lambda x: x[2], reverse=True)
		print("SORTED BY ORIG:", score_list2[0:5])
		print("SORTED BY DETECT:", score_list3[0:5])
		print("--------------")
		score_list4 = score_list_that_answers_all_questions.copy()
		score_list4.sort(key=lambda x: x[1], reverse=True)
		print(score_list4[0:5])
		#print(sorted(score_list2, key=lambda x: x[1], reverse = True)[0:5])

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