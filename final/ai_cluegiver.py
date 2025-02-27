from database_access import get_words_collection, get_word_obj_bbn, get_word_obj_dv, get_single_dv_obj, check_top_clues, get_single_bbn_obj, client_global
from scoring_functions import original_scoring, detect, additional_badness, additional_closeness
from itertools import combinations
import time
from nltk import LancasterStemmer
from multiprocessing import Pool
from pymongo import MongoClient
import math

stemmer = LancasterStemmer()

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

'''
Function that takes in all information from the board and generates returns the scores for the given possible combinations
of board words that we are creating clues for.
'''
def calculate_best_clue(all_possible_combos, good_words_obj_clues, bad_words_obj_clues, good_words_obj_dvf, bad_words_obj_dvf, stemmed_board_words, previous_words):
	client = MongoClient(CONNECTION_STRING)
	
	top_scores = []
	for word_choice in all_possible_combos:
		# LEGACY CODE FROM ATTEMPT TO GENERATE CLUES FOR THREE WORDS

		# if len(word_choice) == 3:
		# 	words_candidates = get_words_collection(client, word_choice)

		# 	intersection_set = {key for key in words_candidates[0]} & {key for key in words_candidates[1]} & {key for key in words_candidates[2]}

		# 	intersection_set = {candidate_clue for candidate_clue in intersection_set if not any(stemmed_board_word_obj[0] in candidate_clue or stemmed_board_word_obj[1] == candidate_clue for stemmed_board_word_obj in stemmed_board_words)}

		# 	intersection_list = list(intersection_set)

		# 	orig_scoring_coef = 0.1
		# 	detect_coef = 1
		# 	additional_closeness_coef = 4
		# 	additional_badness_coef = 3

		# 	score_list = []
		# 	for candidate_clue in intersection_list:
		# 		candidate_clue_dv_obj = get_single_dv_obj(client, candidate_clue)
		# 		score = orig_scoring_coef * original_scoring(candidate_clue, good_words_obj_clues, bad_words_obj_clues) + detect_coef * detect(candidate_clue_dv_obj, good_words_obj_dvf) + additional_closeness_coef * additional_closeness(candidate_clue_dv_obj, word_choice, good_words_obj_dvf) + additional_badness_coef * additional_badness(candidate_clue_dv_obj, bad_words_obj_dvf)
		# 		score_list.append(((word_choice[0], word_choice[1], word_choice[2]), (candidate_clue, score)))

		# 	score_list.sort(key= lambda x: x[1][1], reverse=True)

		# 	top_scores.append(check_top_clues(score_list, previous_words))
		# else: 

		# Get all the words connected to each word we are trying to connect
		words_candidates = get_words_collection(client, word_choice)

		# Generate a set of candidate clues as the intersection of the words associated with the words we are trying to connect from babelnet
		intersection_set = {key for key in words_candidates[0]} & {key for key in words_candidates[1]}

		# Check the stems of our candidate clues to make sure we are only giving valid clues
		intersection_set = {candidate_clue for candidate_clue in intersection_set if not any(stemmed_board_word_obj[0] in candidate_clue or stemmed_board_word_obj[1] == candidate_clue for stemmed_board_word_obj in stemmed_board_words)}

		intersection_list = list(intersection_set)

		# Coeficients for our scoring function
		orig_scoring_coef = 0.1
		detect_coef = 1
		additional_closeness_coef = 4
		additional_badness_coef = 3

		# Calculate the score for each word in our list
		score_list = []
		for candidate_clue in intersection_list:
			candidate_clue_dv_obj = get_single_dv_obj(client, candidate_clue)
			score = orig_scoring_coef * original_scoring(candidate_clue, good_words_obj_clues, bad_words_obj_clues) + detect_coef * detect(candidate_clue_dv_obj, good_words_obj_dvf) + additional_closeness_coef * additional_closeness(candidate_clue_dv_obj, word_choice, good_words_obj_dvf) + additional_badness_coef * additional_badness(candidate_clue_dv_obj, bad_words_obj_dvf)
			score_list.append(((word_choice[0], word_choice[1]), (candidate_clue, score)))

		score_list.sort(key= lambda x: x[1][1], reverse=True)

		top_scores.append(check_top_clues(score_list, previous_words))

	client.close()
	
	return top_scores


'''
Function that takes in the board and the team who's turn it is and returns a tuple containing the list 
of good word and te list of bad words
'''
def split_board(board, team):
	good_words = []
	bad_words = []
	for card_list in board.board:
		for card in card_list:
			if card.color == team and card.guessed == False:
				good_words.append(card.word)
			elif card.guessed == False:
				bad_words.append(card.word)
		
	return (good_words, bad_words)


'''
For two words on the board use multiprocessing to get the score for every candidate clue and then return the 
best clue.
'''
def get_clue(words_obj, given_clues):
	good_words = words_obj[0]
	bad_words = words_obj[1]

	all_board_words = good_words + bad_words 

	# Use stemmer to generate stemmed board words
	stemmed_board_words = [(stemmer.stem(board_word.lower()).upper(), board_word) for board_word in all_board_words]

	# Retrieve information about words from mongodb databases
	good_words_obj_clues = get_word_obj_bbn(good_words)
	bad_words_obj_clues = get_word_obj_bbn(bad_words)

	good_words_obj_dvf = get_word_obj_dv(good_words)
	bad_words_obj_dvf = get_word_obj_dv(bad_words)

	# If there is only one word for your team on the board give a clue only based on vectors
	if len(good_words) == 1:
		client = MongoClient(CONNECTION_STRING)

		word_for_clue = good_words[0]

		candidate_clues = get_single_bbn_obj(word_for_clue).get("single_word_clues")

		intersection_set = {key for key in candidate_clues}

		intersection_list = [candidate_clue for candidate_clue in intersection_set if not any(stemmed_board_word_obj[0] in candidate_clue or stemmed_board_word_obj[1] == candidate_clue for stemmed_board_word_obj in stemmed_board_words)]

		# Score list for candidate clues
		score_list = []
		for candidate_clue in intersection_list:
			candidate_clue_dv_obj = get_single_dv_obj(client, candidate_clue)
			score = additional_closeness(candidate_clue_dv_obj, [word_for_clue], good_words_obj_dvf)
			score_list.append(((word_for_clue), (candidate_clue, score)))

		score_list.sort(key= lambda x: x[1][1], reverse=True)

		return check_top_clues(score_list, given_clues)

	# Try to connect two words
	else:
		# Get all of the possible combinations of words to connect
		all_possible_combos = list(combinations(good_words, r=2))

		# Split the list of combinations so we can use multiprocessing
		num_per_pool = math.ceil(len(all_possible_combos)/20)
		calculate_best_clue_list_of_lists = [(all_possible_combos[i:i+num_per_pool], good_words_obj_clues, bad_words_obj_clues, good_words_obj_dvf, bad_words_obj_dvf, stemmed_board_words, given_clues) for i in range(0, len(all_possible_combos), num_per_pool)]
		# Multiprocess the list
		with Pool() as pool:
			try:
				top_scores = pool.starmap(calculate_best_clue, calculate_best_clue_list_of_lists)
			finally:
				pool.close()

		# Put lists back together to find overall best clue
		overall_scores_list = []
		for temp_list in top_scores:
			overall_scores_list = overall_scores_list + temp_list

		overall_scores_list.sort(key = lambda x: x[1][1], reverse = True)

		return overall_scores_list[0]

