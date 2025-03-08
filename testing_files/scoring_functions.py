# THIS FILE WE SHOULD PUT ALL OF THE SCORING FUNCTIONS IN 

from scipy.spatial.distance import cosine


# HERE WE GO TO THE DB FOR THE CLUE OBJECT MULTIPLE TIMES. WE CAN DO THAT ONLY ONCE AND PASS A CLUE OBJECT INTO THE FUNCTION RATHER THAN THE STRING


# SMALLER VALUE MEANS CLOSER SO IF WE MAKE IT NEGATIVE AND THEN ADD TO DETECT AND ORIG FURTHER WORDS ARE PUNISHED MORE
# WE MAYBE WANT TO MAKE IT SO IT ENCOURAGES BOTH TO BE CLOSE TO EACH OTHER NOT JUST ONE BEING REALLY CLOSE
def additional_closeness(clue_objs, connecting_words, good_words_dv_obj):
	to_return = {}
	for clue_obj in clue_objs:
		clue_obj = clue_obj[1]
		if clue_obj:
			clue_vec = clue_obj.get("vector")

			word1_vec = good_words_dv_obj.get(connecting_words[0]).get("vector")
			word2_vec = good_words_dv_obj.get(connecting_words[1]).get("vector")

			score = dist(clue_vec, word1_vec)**2 + dist(clue_vec, word2_vec)**2
			score = 4/score

			to_return.update({clue_obj.get("word"): score})

	return to_return



# IDEA: WE GET LIKE THE TOP 3 BAD WORDS OR SOMETHING
def additional_badness(clue_objs, bad_words_dv_obj):
	# print(clue_obj)

	to_return = {}
	for clue_obj in clue_objs:
		clue_obj = clue_obj[1]

		if clue_obj:
			clue_vec = clue_obj.get("vector")

			bad_score_array = [dist(clue_vec, bad_word_obj.get("vector")) for bad_word_obj in bad_words_dv_obj.values()]
			bad_score_array.sort(reverse=True)
			bad_score = bad_score_array[0]**2 + bad_score_array[1]**2 + bad_score_array[2]**2

			bad_score = -6/bad_score

			to_return.update({clue_obj.get("word"): bad_score})

	return to_return


def original_scoring(clues, good_words_obj_bbn: dict, bad_words_obj_bbn: dict):
	lambda_good = 1
	lambda_bad = 0.5

	to_return = {}

	for clue in clues:

		good_score_array = [get_score(good_word_obj.get('single_word_clues').get(clue)) for good_word_obj in good_words_obj_bbn.values()]
		good_score = sum(good_score_array)

		bad_score_array = [get_score(bad_word_obj.get('single_word_clues').get(clue)) for bad_word_obj in bad_words_obj_bbn.values()]
		bad_score = max(bad_score_array)

		clue_score = (lambda_good * good_score) - (lambda_bad * bad_score)

		to_return.update({clue: clue_score})

	return to_return


def detect(clue_objs, good_words_obj_dv: dict, bad_words_obj_dv: dict) -> float:
	lambda_f = 3 # We will have to figre out good values for this
	lambda_d = 0.75 # And this

	to_return = {}
	for clue_obj in clue_objs:
		clue_obj = clue_obj[1]
		# print(clue_obj)

		if clue_obj:
			clue_vec = clue_obj.get("vector")
			frequency = clue_obj.get("count")
	

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

			# bad_word_distances = [1 - dist(clue_vec, bad_word.get("vector")) for bad_word in bad_words_obj_dv.values()]
			# bad_words_val = max(bad_word_distances)

			# dict_val = lambda_d * (good_words_val - bad_words_val)

			dict_val = lambda_d * good_words_val
			

			to_return.update({clue_obj.get("word"): dict_val + freq_score})

	return to_return



def dist(word1_vec: list, word2_vec: list) -> float:
	if word1_vec and word2_vec:
		return cosine(word1_vec, word2_vec)
	else:
		return 2


def get_score(clue_obj):
	if clue_obj:
		return 1 / (clue_obj[0] * (clue_obj[1] + 1))
	else: 
		return 0