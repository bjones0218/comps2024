# THIS FILE WE SHOULD PUT THE CODE TO ACTUALLY FIND THE CLUES.
# THIS SHOULD BE ONE BIG FUNCTION WHICH JUST RETURNS THE CLUE
# THIS WAY WE CAN JUST CALL THIS FUNCTION FROM THE codenames.py AND IT WILL GIVE BACK THE CLUE


from database_access import words_collection, get_word_obj_bbn, get_word_obj_dv, get_single_dv_obj, check_top_clues
from scoring_functions import original_scoring, detect, additional_badness, additional_closeness
from itertools import combinations
import time
from nltk import LancasterStemmer

stemmer = LancasterStemmer()


# Will need to change this to take in all the words on the board and split them up probably
# def get_clue(board_words, team):
def get_clue(good_words, bad_words):
	start_time = time.time()
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

		orig_scoring_coef = 0.1
		detect_coef = 1
		additional_closeness_coef = 6
		additional_badness_coef = 4

		score_list = []
		for candidate_clue in intersection_list:
			candidate_clue_dv_obj = get_single_dv_obj(candidate_clue)
			score = orig_scoring_coef * original_scoring(candidate_clue, good_words_obj_clues, bad_words_obj_clues) + detect_coef * detect(candidate_clue_dv_obj, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness_coef * additional_closeness(candidate_clue_dv_obj, word_choice, good_words_obj_dvf) + additional_badness_coef * additional_badness(candidate_clue_dv_obj, bad_words_obj_dvf)
			score_list.append(((word_choice[0], word_choice[1]), (candidate_clue, score)))
		
		score_list.sort(key= lambda x: x[1][1], reverse=True)

		top_scores.append(check_top_clues(score_list))

	top_scores.sort(key = lambda x: x[1][1], reverse = True)

	# print(top_scores)
	# print(time.time() - start_time)
	# Will need to change to just return the clue but for simulation this is what we want
	return top_scores[0]

