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

def get_good_word_obj_dv(good_words):
	return {word: freq_and_vec_collection2.find_one({"word": word}) for word in good_words}

def get_bad_word_obj_dv(bad_words):
	return {word: freq_and_vec_collection2.find_one({"word": word}) for word in bad_words}

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

	return 4/score

def additional_badness(clue, bad_words_dv_obj):
	clue_db_obj = freq_and_vec_collection2.find_one({"word": clue})
	if clue_db_obj:
		clue_vec = clue_db_obj.get("vector")
	else:
		clue_vec = None
	bad_score_array = [dist(clue_vec, bad_word_obj.get("vector")) for bad_word_obj in bad_words_dv_obj.values()]
	bad_score = max(bad_score_array)

	return -4/bad_score



def original_scoring(clue, good_words_obj_bbn: dict, bad_words_obj_bbn: dict):
	lambda_good = 1
	lambda_bad = 0.5

	good_score_array = [get_score(good_word_obj.get('single_word_clues').get(clue)) for good_word_obj in good_words_obj_bbn.values()]
	good_score = sum(good_score_array)

	bad_score_array = [get_score(bad_word_obj.get('single_word_clues').get(clue)) for bad_word_obj in bad_words_obj_bbn.values()]
	bad_score = max(bad_score_array)

	clue_score = (lambda_good * good_score) - (lambda_bad * bad_score)

	return clue_score


def detect(clue: str, good_words_obj_dv: dict, bad_words_obj_dv: dict) -> float:
	lambda_f = 2 # We will have to figre out good values for this
	lambda_d = 2 # And this

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
	good_words_val = sum(good_word_distances)

	bad_word_distances = [1 - dist(clue_vec, bad_word.get("vector")) for bad_word in bad_words_obj_dv.values()]
	bad_words_val = max(bad_word_distances)

	dict_val = lambda_d * (good_words_val - bad_words_val)

	return freq_score + dict_val


def dist(word1_vec: list, word2_vec: list) -> float:
	if word1_vec and word2_vec:
		return cosine(word1_vec, word2_vec)
	else:
		return 2
	

if __name__ == "__main__":
	start_time = time.time()
	client = MongoClient(CONNECTION_STRING)
	codenames_db = client["codenames_db"]
	codenames_clues_collection = codenames_db["codenames_clues"]
	for _ in range(20):
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



		top_scores_all = []
		top_scores_paper = []
		top_scores_no_paper = []
		top_scores_all2 = []
		top_scores_all3 = []


		for word_choice in all_possible_combos:
			# print(word_choice)

			word1_candidates = {key for key in list(codenames_clues_collection.find_one({"codenames_word": word_choice[0]}).get("single_word_clues").keys())}
			word2_candidates = {key for key in list(codenames_clues_collection.find_one({"codenames_word": word_choice[1]}).get("single_word_clues").keys())}


			intersection_set = word1_candidates & word2_candidates
			# NOTE: These are called angry words because they make me angry (⩺_⩹)
			angry_words = ["WBM", "WAYBACK", "WAYBACKMACHINE", "ISBN", "ISBNS", "EISBN", "ESBN", "WAYBACKED", "GB", "P", "W"]
			for angry_word in angry_words:
				intersection_set.discard(angry_word)
			
			all_board_words = good_words + bad_words


			intersection_set_2 = {candidate_clue for candidate_clue in intersection_set if not any(board_word in candidate_clue or board_word == candidate_clue for board_word in all_board_words)}

			intersection = list(intersection_set_2)

			# orig_scoring_vals = [original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) for candidate_clue in intersection]
			# detect_vals =  [detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) for candidate_clue in intersection]
			# additional_closeness_vals = [additional_closeness(candidate_clue, word_choice, good_words_obj_dvf) for candidate_clue in intersection]
			# additional_badness_vals = [additional_badness(candidate_clue, word_choice, bad_words_obj_dvf) for candidate_clue in intersection]

			# .2 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + 2 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) 
			#score_list = [(candidate_clue, .2 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + 2 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) + 4 * additional_closeness(candidate_clue, word_choice, good_words_obj_dvf), .2 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc), 2 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf), 4 * additional_closeness(candidate_clue, word_choice, good_words_obj_dvf)) for candidate_clue in intersection]
			# score_list = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness(candidate_clue, word_choice, good_words_obj_dvf)) for candidate_clue in intersection]
			#score_list = [(candidate_clue, additional_closeness(candidate_clue, word_choice, good_words_obj_dvf)) for candidate_clue in intersection]

			# score_list_all = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness(candidate_clue, word_choice, good_words_obj_dvf) + additional_badness(candidate_clue, bad_words_obj_dvf)) for candidate_clue in intersection]
			# score_list_paper = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf)) for candidate_clue in intersection]
			# score_list_no_paper = [(candidate_clue, 3 * additional_closeness(candidate_clue, word_choice, good_words_obj_dvf) + additional_badness(candidate_clue, bad_words_obj_dvf)) for candidate_clue in intersection]
			orig_scale_1 = 0.1
			orig_scale_2 = 0.1
			detect_scale_1 = 1
			detect_scale_2 = 1
			additional_closeness_scale_1 = 5
			additional_closeness_scale_2 = 3
			additional_badness_scale_1 = 3
			additional_badness_scale_2 = 1

			score_list_all2 = [(candidate_clue, orig_scale_1 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + detect_scale_1 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness_scale_1 * additional_closeness(candidate_clue, word_choice, good_words_obj_dvf) + additional_badness_scale_1 * additional_badness(candidate_clue, bad_words_obj_dvf)) for candidate_clue in intersection]
			score_list_all3 = [(candidate_clue, orig_scale_2 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + detect_scale_2 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf) + additional_closeness_scale_2 * additional_closeness(candidate_clue, word_choice, good_words_obj_dvf) + additional_badness_scale_2 * additional_badness(candidate_clue, bad_words_obj_dvf)) for candidate_clue in intersection]


			# score_list_that_answers_all_questions = [(candidate_clue, .1 * original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc) + 3 * detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf)) for candidate_clue in intersection]
			# score_list = [(candidate_clue, original_scoring(candidate_clue, good_words_obj_cc, bad_words_obj_cc), detect(candidate_clue, good_words_obj_dvf, bad_words_obj_dvf)) for candidate_clue in intersection]

			# score_list_all.sort(key= lambda x: x[1], reverse=True)
			# score_list_paper.sort(key= lambda x: x[1], reverse=True)
			# score_list_no_paper.sort(key= lambda x: x[1], reverse=True)
			score_list_all2.sort(key= lambda x: x[1], reverse=True)
			score_list_all3.sort(key= lambda x: x[1], reverse=True)




			# GET THE TOP 5 FOR EACH WORD
			# print(score_list_all[0:5])
			# print(score_list_paper[0:5])
			# print(score_list_no_paper[0:5])

			# print(score_list_all2[0:5])
			# print(score_list_all3[0:5])




			# top_scores_all.append((word_choice, score_list_all[0]))
			# top_scores_paper.append((word_choice, score_list_paper[0]))
			# top_scores_no_paper.append((word_choice, score_list_no_paper[0]))
			top_scores_all2.append((word_choice, score_list_all2[0]))
			top_scores_all3.append((word_choice, score_list_all3[0]))



			# STILL END UP WITH THINGS LIKE "SPINAL" AS A CLUE FOR "SPINE" AND STUFF LIKE THAT WHICH WE NEED TO FIX

		

		# top_scores_all.sort(key = lambda x: x[1][1], reverse = True)
		# top_scores_paper.sort(key = lambda x: x[1][1], reverse = True)
		# top_scores_no_paper.sort(key = lambda x: x[1][1], reverse = True)
		top_scores_all2.sort(key = lambda x: x[1][1], reverse = True)
		top_scores_all3.sort(key = lambda x: x[1][1], reverse = True)



		# print(top_scores_all)
		# print(top_scores_paper)
		# print(top_scores_no_paper)
		# print(top_scores_all2)
		# print(top_scores_all3)



		# print(f"The best clue is {top_scores_all[0][1][0]} with a score of {top_scores_all[0][1][1]} which connects the words {top_scores_all[0]}")
		# print(f"The best clue is {top_scores_paper[0][1][0]} with a score of {top_scores_paper[0][1][1]} which connects the words {top_scores_paper[0]}")
		# print(f"The best clue is {top_scores_no_paper[0][1][0]} with a score of {top_scores_no_paper[0][1][1]} which connects the words {top_scores_no_paper[0]}")
		print(f"The best clue is {top_scores_all2[0][1][0]} with a score of {top_scores_all2[0][1][1]} which connects the words {top_scores_all2[0]}")
		print(f"The best clue is {top_scores_all3[0][1][0]} with a score of {top_scores_all3[0][1][1]} which connects the words {top_scores_all3[0]}")
		
		random.shuffle(all_board_words)		

		with open("testing_documentation_form.txt", "a") as output_file:
			output_file.write(f"The board words are: {all_board_words}\n")
			output_file.write(f"The good words are: {good_words}\n")
			output_file.write(f"The bad words are: {bad_words}\n")
			output_file.write(f"The weights for the first function are: orig scoring: {orig_scale_1}, detect: {detect_scale_1}, closeness: {additional_closeness_scale_1}, badness: {additional_badness_scale_1} \n")
			output_file.write(f"The best clue is {top_scores_all2[0][1][0]} with a score of {top_scores_all2[0][1][1]} which connects the words {top_scores_all2[0]} \n")
			output_file.write(f"The weights for the second function are: orig scoring: {orig_scale_2}, detect: {detect_scale_2}, closeness: {additional_closeness_scale_2}, badness: {additional_badness_scale_2} \n")
			output_file.write(f"The best clue is {top_scores_all3[0][1][0]} with a score of {top_scores_all3[0][1][1]} which connects the words {top_scores_all3[0]} \n")
			output_file.write("--------------------------\n")
		print(time.time() - start_time)
