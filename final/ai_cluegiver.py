# THIS FILE WE SHOULD PUT THE CODE TO ACTUALLY FIND THE CLUES.
# THIS SHOULD BE ONE BIG FUNCTION WHICH JUST RETURNS THE CLUE
# THIS WAY WE CAN JUST CALL THIS FUNCTION FROM THE codenames.py AND IT WILL GIVE BACK THE CLUE


from database_access import get_words_collection, get_word_obj_bbn, get_word_obj_dv, get_single_dv_obj, check_top_clues, client_global
from scoring_functions import original_scoring, detect, additional_badness, additional_closeness
from itertools import combinations
import time
from nltk import LancasterStemmer
from multiprocessing import Pool
from pymongo import MongoClient

stemmer = LancasterStemmer()

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

def calculate_best_clue(all_possible_combos, good_words_obj_clues, bad_words_obj_clues, good_words_obj_dvf, bad_words_obj_dvf, stemmed_board_words, previous_words):
	client = MongoClient(CONNECTION_STRING)
	
	top_scores = []
	for word_choice in all_possible_combos:
		words_candidates = get_words_collection(client, word_choice)

		intersection_set = {key for key in words_candidates[0]} & {key for key in words_candidates[1]}

		intersection_set = {candidate_clue for candidate_clue in intersection_set if not any(stemmed_board_word_obj[0] in candidate_clue or stemmed_board_word_obj[1] == candidate_clue for stemmed_board_word_obj in stemmed_board_words)}

		intersection_list = list(intersection_set)

		orig_scoring_coef = 0.1
		detect_coef = 1
		additional_closeness_coef = 6
		additional_badness_coef = 3

		score_list = []
		start_time = time.time()
		for candidate_clue in intersection_list:
			candidate_clue_dv_obj = get_single_dv_obj(client, candidate_clue)
			score = orig_scoring_coef * original_scoring(candidate_clue, good_words_obj_clues, bad_words_obj_clues) + detect_coef * detect(candidate_clue_dv_obj, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness_coef * additional_closeness(candidate_clue_dv_obj, word_choice, good_words_obj_dvf) + additional_badness_coef * additional_badness(candidate_clue_dv_obj, bad_words_obj_dvf)
			score_list.append(((word_choice[0], word_choice[1]), (candidate_clue, score)))
		end_time = time.time()

		print(end_time - start_time)

		score_list.sort(key= lambda x: x[1][1], reverse=True)

		top_scores.append(check_top_clues(score_list, previous_words))

	client.close()
	
	return top_scores



def split_board(board, team):
	good_words = []
	bad_words = []
	print(board.board)
	for card_list in board.board:
		for card in card_list:
			# print(team)
			# print(card.color)
			if card.color == team and card.guessed == False:
				good_words.append(card.word)
			elif card.guessed == False:
				bad_words.append(card.word)
		
	return (good_words, bad_words)

	# print(board.board)

# BASICALLY THE IDEA HERE IS THAT I WILL USE MULTIPROCESSING FOR EACH PAIR OF BOARD WORDS AND RUN THAT IN PARALLEL

# Will need to change this to take in all the words on the board and split them up probably
# def get_clue(board_words, team):
def get_clue(words_obj, given_clues):
	good_words = words_obj[0]
	bad_words = words_obj[1]
	start_time = time.time()
	# time.sleep(160)
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


	# top_scores = calculate_best_clue(all_possible_combos, good_words_obj_clues, bad_words_obj_clues, good_words_obj_dvf, bad_words_obj_dvf, stemmed_board_words)
	# NEED TO ADD CODE TO CHECK IF THERE IS ONLY ONE WORD LEFT AND GIVE A CLUE FOR THAT ONE WORD
	start_time = time.time()
	calculate_best_clue_list_of_lists = [(all_possible_combos[i:i+4], good_words_obj_clues, bad_words_obj_clues, good_words_obj_dvf, bad_words_obj_dvf, stemmed_board_words, given_clues) for i in range(0, len(all_possible_combos), 4)]
	with Pool() as pool:
		try:
			top_scores = pool.starmap(calculate_best_clue, calculate_best_clue_list_of_lists)
		finally:
			pool.close()
	end_time = time.time()

	overall_scores_list = []
	for temp_list in top_scores:
		overall_scores_list = overall_scores_list + temp_list

	overall_scores_list.sort(key = lambda x: x[1][1], reverse = True)


	# print(top_scores)
	print("-------------------")
	print(end_time - start_time)
	print(overall_scores_list[0][1][0])
	# Will need to change to just return the clue but for simulation this is what we want
	return overall_scores_list[0]

