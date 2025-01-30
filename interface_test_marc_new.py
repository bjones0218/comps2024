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
	
# SMALLER VALUE MEANS CLOSER SO IF WE MAKE IT NEGATIVE AND THEN ADD TO DETECT AND ORIG FURTHER WORDS ARE PUNISHED MORE
# WE MAYBE WANT TO MAKE IT SO IT ENCOURAGES BOTH TO BE CLOSE TO EACH OTHER NOT JUST ONE BEING REALLY CLOSE
def additional_closeness(clue, connecting_words, good_words_dv_obj):
	clue_db_obj = freq_and_vec_collection2.find_one({"word": clue})
	if clue_db_obj:
		clue_vec = clue_db_obj.get("vector")
	else:
		clue_vec = None

	word1_vec = good_words_dv_obj.get(connecting_words[0]).get("vector")
	word2_vec = good_words_dv_obj.get(connecting_words[1]).get("vector")

	score = dist(clue_vec, word1_vec)**2 + dist(clue_vec, word2_vec)**2
	# print(dist(clue_vec, word1_vec))
	# print(dist(clue_vec, word2_vec))


	return 4/score

def additional_badness(clue, bad_words_dv_obj):
	#print(bad_words_dv_obj)
	#bad_score_array = [bad_word_obj for bad_word_obj in bad_words_dv_obj]
	clue_db_obj = freq_and_vec_collection2.find_one({"word": clue})
	if clue_db_obj:
		clue_vec = clue_db_obj.get("vector")
	else:
		clue_vec = None
	bad_score_array = [dist(clue_vec,bad_words_dv_obj.get(bad_word_obj).get("vector")) for bad_word_obj in bad_words_dv_obj]

	# bad_score_array = [1 / ((bad_word_obj.get('single_word_clues').get(clue)[0] * bad_word_obj.get('single_word_clues').get(clue)[1]) + 1) if bad_word_obj.get('single_word_clues').get(clue) else 0 for bad_word_obj in bad_words_obj_bbn.values()]
	bad_score = max(bad_score_array)

	return 2/bad_score



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


	# print(clue)

	clue_db_obj = freq_and_vec_collection2.find_one({"word": clue})
	if clue_db_obj:
		clue_vec = clue_db_obj.get("vector")
		frequency = clue_db_obj.get("count")
	else:
		clue_vec = None
		frequency = 0

	alpha = 1800000

	if frequency < alpha: # Word is too rare
		if frequency < 30: # WORD IS WAYYYYY TOO RARE
			freq_val = -2
		else:
			freq_val = -(30/frequency)
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

	good_words_obj_cc = get_good_word_obj_bbn(good_words)
	bad_words_obj_cc = get_bad_word_obj_bbn(bad_words)
	
	good_words_obj_dvf = get_good_word_obj_dv(good_words)
	bad_words_obj_dvf = get_bad_word_obj_dv(bad_words)

	# print(additional_badness("AFRICA", bad_words_obj_dvf))

	# None[0]


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


	# I THINK OUR INTERSECTION IS TOO GENERAL!!!!!!!
	# BECAUSE WE GET TOO MANY OF THE SAME THINGS

	# WE NEED SOMETHING SOMEWHERE OR ARE MISSING SOMETHING THAT EMPHASIZES CLOSENESS TO THE TWO WORDS THAT IT IS TRYING TO CONNECT
	# THIS SHOULD BE THE INTERSECTION BUT THE INTERSECTION IS SO GENERAL THAT IT RUNS INTO PROBLEMS

	all_max_scores = []
	top_scores = []
	for word_choice in all_possible_combos:
		print(word_choice)

		# print(good_words)
		# print(bad_words)

		# print(additional_closeness("DOG", word_choice, good_words_obj_dvf))
		# print(additional_closeness("JACKET", word_choice, good_words_obj_dvf))
		# print(additional_closeness("RAMPAGE", word_choice, good_words_obj_dvf))
		# print(additional_closeness("SYNTHESIS", word_choice, good_words_obj_dvf))

		word1_candidates = {key for key in list(codenames_clues_collection.find_one({"codenames_word": word_choice[0]}).get("single_word_clues").keys())}
		word2_candidates = {key for key in list(codenames_clues_collection.find_one({"codenames_word": word_choice[1]}).get("single_word_clues").keys())}

		

		# print(list(word1_candidates)[0:10])
		# print(list(word2_candidates)[0:10])

		intersection_set = word1_candidates & word2_candidates
		# NOTE: These are called angry words because they make me angry (⩺_⩹)
		# NOTE: SHOULD FIND MORE EFFICIENT WAY TO DO THIS (prob keeping it in a set until I remove the things I don't want)
		angry_words = ["WBM", "WAYBACK", "WAYBACKMACHINE", "ISBN", "ISBNS", "EISBN", "ESBN", "WAYBACKED", "GB", "P", "W"]
		for angry_word in angry_words:
			intersection_set.discard(angry_word)
		

		all_board_words = good_words + bad_words
		# print(all_board_words)
		# ALSO WE NEED TO GET RID OF ANYTHIGN THAT CONTAINS A BOARD WORd

		intersection_set_2 = {candidate_clue for candidate_clue in intersection_set if not any(board_word in candidate_clue or board_word == candidate_clue for board_word in all_board_words)}

		# for board_word_good in good_words:
		# 	intersection_set.discard(board_word_good)

		# for board_word_bad in bad_words:
		# 	intersection_set.discard(board_word_bad)

		intersection = list(intersection_set_2)


# .2 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + 2 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) 
		#score_list = [(candidate_clue, .2 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + 2 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) + 4 * additional_closeness(candidate_clue, word_choice, good_words_obj_dvf), .2 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc), 2 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf), 4 * additional_closeness(candidate_clue, word_choice, good_words_obj_dvf)) for candidate_clue in intersection]
		score_list = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness(candidate_clue, word_choice, good_words_obj_dvf)) for candidate_clue in intersection]
		#score_list = [(candidate_clue, additional_closeness(candidate_clue, word_choice, good_words_obj_dvf)) for candidate_clue in intersection]



		# score_list_that_answers_all_questions = [(candidate_clue, .1 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + 3 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf)) for candidate_clue in intersection]
		# score_list = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc), detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf)) for candidate_clue in intersection]

		score_list.sort(key= lambda x: x[1], reverse=True)
		# print(score_list2[0:5])
		# print("SORTED BY ORIG:", score_list2[0:5])
		# print("SORTED BY DETECT:", score_list3[0:5])
		# print("--------------")
		# score_list4 = score_list_that_answers_all_questions.copy()
		# score_list4.sort(key=lambda x: x[1], reverse=True)
		# print(score_list4[0:5])
		# print(sorted(score_list2, key=lambda x: x[1], reverse = True)[0:5])

		# GET THE TOP 5 FOR EACH WORD
		print(score_list[0:5])
		all_max_scores.append((word_choice, score_list[0:5]))
		top_scores.append((word_choice, score_list[0]))

		# STILL END UP WITH THINGS LIKE "SPINAL" AS A CLUE FOR "SPINE" AND STUFF LIKE THAT WHICH WE NEED TO FIX

	
	print(all_max_scores)

	print(top_scores)
	top_scores.sort(key = lambda x: x[1][1], reverse = True)
	print(top_scores)
	print(f"The best clue is {top_scores[0][1][0]} with a score of {top_scores[0][1][1]} which connects the words {top_scores[0]}")
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