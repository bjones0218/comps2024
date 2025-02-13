# THIS FILE WE SHOULD PUT THE CODE TO ACTUALLY FIND THE CLUES.
# THIS SHOULD BE ONE BIG FUNCTION WHICH JUST RETURNS THE CLUE
# THIS WAY WE CAN JUST CALL THIS FUNCTION FROM THE codenames.py AND IT WILL GIVE BACK THE CLUE


from database_access import words_collection, get_word_obj_bbn, get_word_obj_dv, get_single_dv_obj, check_top_clues, get_dv_objs, client
from scoring_functions import original_scoring, detect, additional_badness, additional_closeness
from itertools import combinations
import time
from nltk import LancasterStemmer
from multiprocessing import Pool

stemmer = LancasterStemmer()

def score_word(candidate_clue, word_choice, good_words_obj_clues, bad_words_obj_clues, good_words_obj_dvf, bad_words_obj_dvf):
	orig_scoring_coef = 0.1
	detect_coef = 1
	additional_closeness_coef = 6
	additional_badness_coef = 4

	candidate_clue_dv_obj = get_single_dv_obj(candidate_clue)
	score = orig_scoring_coef * original_scoring(candidate_clue, good_words_obj_clues, bad_words_obj_clues) + detect_coef * detect(candidate_clue_dv_obj, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness_coef * additional_closeness(candidate_clue_dv_obj, word_choice, good_words_obj_dvf) + additional_badness_coef * additional_badness(candidate_clue_dv_obj, bad_words_obj_dvf)
	
	return ((word_choice[0], word_choice[1]), (candidate_clue, score))

# Will need to change this to take in all the words on the board and split them up probably
# def get_clue(board_words, team):
def get_clue(good_words, bad_words):
	# start_time = time.time()
	# Check each word: if it has not been guessed and is the same color as the guessing team add it to good words and if it is not the same color add it to bad words
	# good_words = []
	# bad_words = []
	all_board_words = good_words + bad_words # THIS SHOULD BE JUST A LIST OF WORDS

	stemmed_board_words = [(stemmer.stem(board_word.lower()).upper(), board_word) for board_word in all_board_words]

	# bad_words = ['AZTEC', 'APPLE', 'NURSE', 'SCIENTIST', 'FACE', 'FILM', 'PIN', 'CENTAUR']
	# good_words = ['PARACHUTE', 'DICE', 'HOTEL', 'TAIL', 'FLUTE', 'MODEL', 'WASHINGTON', 'HOLLYWOOD']

	all_possible_combos = list(combinations(good_words, r=2))

	good_words_obj_clues = get_word_obj_bbn(good_words)
	bad_words_obj_clues = get_word_obj_bbn(bad_words)

	good_words_obj_dvf = get_word_obj_dv(good_words)
	bad_words_obj_dvf = get_word_obj_dv(bad_words)

	# NEED TO ADD CODE TO CHECK IF THERE IS ONLY ONE WORD LEFT AND GIVE A CLUE FOR THAT ONE WORD

	top_scores = []
	for word_choice in all_possible_combos:
		word1_candidates = {key for key in list(words_collection.find_one({"codenames_word": word_choice[0]}).get("single_word_clues").keys())}
		word2_candidates = {key for key in list(words_collection.find_one({"codenames_word": word_choice[1]}).get("single_word_clues").keys())}

		intersection_set = word1_candidates & word2_candidates

		intersection_set = {candidate_clue for candidate_clue in intersection_set if not any(stemmed_board_word_obj[0] in candidate_clue or stemmed_board_word_obj[1] == candidate_clue for stemmed_board_word_obj in stemmed_board_words)}

		intersection_list = list(intersection_set)

		intersection_list_of_lists = [intersection_list[i:i + 500] for i in range(0, len(intersection_list), 500)]

		# print(len(intersection_list))

		# intersection_list_orig_scoring = [(intersection_clue, good_words_obj_clues, bad_words_obj_clues) for intersection_clue in intersection_list]

		# IDEA: GO TO THE DB ALL AT THE SAME TIME INSTEAD OF LOTS OF DIFFERENT TIMES?

		orig_scoring_coef = 0.1
		detect_coef = 1
		additional_closeness_coef = 6
		additional_badness_coef = 4

		score_list = []

		# THIS IS WHAT NEEDS TO BE MULTITHREADED
		# list_w_objects = get_dv_objs(intersection_list)

		start_db = time.time()
		with Pool() as pool:
			try: 
				list_w_objects = pool.map(get_dv_objs, intersection_list_of_lists)
			finally:
				pool.close()

		# print("DONE WITH POOL")

		# HERE WE CALCULATE ORIGINAL SCORING SCORE FOR ALL AT ONCE

		# orig_scoring_list = 

		overall_list = []
		for list_try in list_w_objects:
			overall_list = overall_list + list_try


		
		end_db = time.time()
		start_calculation = time.time()

		# DO OUR CHUNKING AGAIN

		# orig_scoring_intersection_list = [(clue, good_words_obj_clues, bad_words_obj_clues) for clue in intersection_list]

		orig_scoring_list_of_lists = [(intersection_list[i:i + 500], good_words_obj_clues, bad_words_obj_clues) for i in range(0, len(intersection_list), 500)]
		
		detect_list_of_lists = [(overall_list[i:i + 500], good_words_obj_dvf, bad_words_obj_dvf) for i in range(0, len(overall_list), 500)]

		additional_closeness_list_of_lists = [(overall_list[i:i + 500], word_choice, good_words_obj_dvf) for i in range(0, len(overall_list), 500)]

		additional_badness_list_of_lists = [(overall_list[i:i + 500], bad_words_obj_dvf) for i in range(0, len(overall_list), 500)]


		with Pool() as pool2:
			try: 
				orig_scoring_vals = pool2.starmap(original_scoring, orig_scoring_list_of_lists)
				detect_scoring_vals = pool2.starmap(detect, detect_list_of_lists)
				additional_closeness_vals = pool2.starmap(additional_closeness, additional_closeness_list_of_lists)
				additional_badness_vals = pool2.starmap(additional_badness, additional_badness_list_of_lists)
			finally:
				pool2.close()

		combined_orig_scoring_vals = {}
		combined_detect_vals = {}
		combined_additional_closeness_vals = {}
		combined_additional_badness_vals = {}

		for orig_dict in orig_scoring_vals:
			combined_orig_scoring_vals.update(orig_dict)

		for detect_dict in detect_scoring_vals:
			combined_detect_vals.update(detect_dict)

		for additional_closeness_dict in additional_closeness_vals:
			combined_additional_closeness_vals.update(additional_closeness_dict)

		for additional_badness_dict in additional_badness_vals:
			combined_additional_badness_vals.update(additional_badness_dict)

		all_words = list(combined_orig_scoring_vals.keys())


		score_list = []
		for word in all_words:
			if combined_orig_scoring_vals.get(word) and combined_detect_vals.get(word) and combined_additional_closeness_vals.get(word) and combined_additional_badness_vals.get(word):
				orig_score = orig_scoring_coef * combined_orig_scoring_vals.get(word)
				detect_score = detect_coef * combined_detect_vals.get(word)
				additional_closeness_score = additional_closeness_coef * combined_additional_closeness_vals.get(word)
				additional_badness_score = additional_badness_coef * combined_additional_badness_vals.get(word)

				score = orig_score + detect_score + additional_closeness_score + additional_badness_score

				score_list.append(((word_choice[0], word_choice[1]), (word, score)))


		
		end_calculation = time.time()

		print("-----------------------")
		print("DBTIMING", end_db - start_db)
		print("CALCULATIONTIMING", end_calculation - start_calculation)
		print("-----------------------")

		# # print(list_w_objects[0][0])
		# for candidate_clue_obj in overall_list:
		# 	candidate_clue = candidate_clue_obj[0]
		# 	candidate_clue_dv_obj = candidate_clue_obj[1]
		# 	score = orig_scoring_coef * original_scoring(candidate_clue, good_words_obj_clues, bad_words_obj_clues) + detect_coef * detect(candidate_clue_dv_obj, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness_coef * additional_closeness(candidate_clue_dv_obj, word_choice, good_words_obj_dvf) + additional_badness_coef * additional_badness(candidate_clue_dv_obj, bad_words_obj_dvf)
		# 	score_list.append(((word_choice[0], word_choice[1]), (candidate_clue, score)))

		# # print("DONE WITH CALCULATIONS")
		# # new_intersection_list = []
		# # for clue in intersection_list:
		# # 	new_intersection_list.append((clue, word_choice, good_words_obj_clues, bad_words_obj_clues, good_words_obj_dvf, bad_words_obj_dvf))

		# print("DB ACCESS TOOK", end_db - start_db)
		# print("Calculation took", end_calculation - start_calculation)

		# score_list = []

		# with Pool() as pool:
		# 	try:
		# 	#map score onto the tuples in new_intersection reading each as the args.
		# 		score_list = pool.starmap(score_word, new_intersection_list)
		# 	finally:
		# 		# Close worker connections after pool is done
		# 		pool.close()
		# 		pool.join()

		# for candidate_clue in intersection_list:
		# 	candidate_clue_dv_obj = get_single_dv_obj(candidate_clue)
		# 	score = orig_scoring_coef * original_scoring(candidate_clue, good_words_obj_clues, bad_words_obj_clues) + detect_coef * detect(candidate_clue_dv_obj, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness_coef * additional_closeness(candidate_clue_dv_obj, word_choice, good_words_obj_dvf) + additional_badness_coef * additional_badness(candidate_clue_dv_obj, bad_words_obj_dvf)
		# 	score_list.append(((word_choice[0], word_choice[1]), (candidate_clue, score)))
		score_list.sort(key= lambda x: x[1][1], reverse=True)
		top_scores.append(check_top_clues(score_list))

	top_scores.sort(key = lambda x: x[1][1], reverse = True)

	# print(top_scores)
	# print(time.time() - start_time)
	# Will need to change to just return the clue but for simulation this is what we want
	return top_scores[0]

