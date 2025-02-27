from scipy.spatial.distance import cosine


'''
Additional function created by us to score potential clues based on how close they are to the words 
they are trying to connect and to deal with scoring for only one clue
'''
def additional_closeness(clue_obj, connecting_words, good_words_dv_obj):
	# Check to make sure the clue object from the database exists
	if clue_obj:
		clue_vec = clue_obj.get("vector")
	else:
		clue_vec = None

	# To deal with clues for only one word
	if len(connecting_words) == 1:
		word1_vec = good_words_dv_obj.get(connecting_words[0]).get("vector")
		word1_freq = good_words_dv_obj.get(connecting_words[0]).get("count")

		# Alpha constant for frequency
		alpha = 1800000

		# Word is too rare
		if word1_freq < alpha: 
			# Word is way too rare
			if word1_freq < 30:
				freq_val = -3
			else:
				freq_val = -.5
		# Word is too common
		else:
			freq_val = -1

		# Return 1/ the value because we want to make smaller cosine distances return larger values
		return 1/(dist(clue_vec, word1_vec)**3) + freq_val
	
	# LEGACY CODE for 3 word clues
	# elif len(connecting_words) == 3:
	# 	word1_vec = good_words_dv_obj.get(connecting_words[0]).get("vector")
	# 	word2_vec = good_words_dv_obj.get(connecting_words[1]).get("vector")
	# 	word3_vec = good_words_dv_obj.get(connecting_words[2]).get("vector")

	# 	distOne = dist(clue_vec, word1_vec)
	# 	distTwo = dist(clue_vec, word2_vec)
	# 	distThree = dist(clue_vec, word3_vec)

	# 	array = [] 
	# 	array.extend([distOne,distTwo,distThree])
	# 	array.sort()
	# 	score = array[0]**3 + array[1]**3 + array[2]**4

	# 	# score = dist(clue_vec, word1_vec)**4 + dist(clue_vec, word2_vec)**4 + dist(clue_vec, word3_vec)**4

	# 	return 17/score

	# For clues for two words
	else:
		word1_vec = good_words_dv_obj.get(connecting_words[0]).get("vector")
		word2_vec = good_words_dv_obj.get(connecting_words[1]).get("vector")

		# Get cosine distances for the clue to each word it's trying to connect
		score = dist(clue_vec, word1_vec)**3 + dist(clue_vec, word2_vec)**3
		
		# Return 10/ the value because we want to make smaller cosine distances return larger values
		return 10/score


'''
Function to calculate a penalty for potential clues that are too close to the bad words
'''
def additional_badness(clue_obj, bad_words_dv_obj):
	# Check the clue information exists in the database
	if clue_obj:
		clue_vec = clue_obj.get("vector")
	else:
		clue_vec = None

	bad_score_array = [dist(clue_vec, bad_word_obj.get("vector")) for bad_word_obj in bad_words_dv_obj.values()]
	bad_score_array.sort(reverse=True)
	
	# Depending on the number of bad words we get the top 3 if possible or fewer if that's all we have
	if len(bad_score_array) >= 3:
		bad_score = bad_score_array[0]**2 + bad_score_array[1]**2 + bad_score_array[2]**2
	elif len(bad_score_array) == 2:
			bad_score = bad_score_array[0]**2 + bad_score_array[1]**2
	else:
		bad_score = bad_score_array[0]**2

	# Return 6/ the value because we want to make smaller cosine distances return larger values
	return -6/bad_score

'''
Implementation of the original scoring function from the paper using 1 and 0.5 as lambda values
'''
def original_scoring(clue, good_words_obj_bbn, bad_words_obj_bbn):
	lambda_good = 1
	lambda_bad = 0.5

	# Calculate score for each good word and take the sum as the good score
	good_score_array = [get_score(good_word_obj.get('single_word_clues').get(clue)) for good_word_obj in good_words_obj_bbn.values()]
	good_score = sum(good_score_array)

	# Calculate score for each bad word adn take the max as the bad score
	bad_score_array = [get_score(bad_word_obj.get('single_word_clues').get(clue)) for bad_word_obj in bad_words_obj_bbn.values()]
	bad_score = max(bad_score_array)

	clue_score = (lambda_good * good_score) - (lambda_bad * bad_score)

	return clue_score

'''
Implementation of the detect function from the paper with slight difference of the removal of distance from 
bad words since that is already included in additiona badness function
'''
def detect(clue_obj, good_words_obj_dv):
	lambda_f = 2 
	lambda_d = 1.5 

	# Check that the the clue exists
	if clue_obj:
		clue_vec = clue_obj.get("vector")
		frequency = clue_obj.get("count")
	else:
		clue_vec = None
		frequency = 0

	# Alpha constant for frequency
	alpha = 1800000

	# Word is too rare
	if frequency < alpha: 
		# Word is way too rare
		if frequency < 30: 
			freq_val = -2
		else:
			freq_val = -(30/frequency)
	# Word is too common
	else:
		freq_val = -1

	# Get frequency score
	freq_score = lambda_f * freq_val 

	# Get closeness score
	good_word_distances = [1 - dist(clue_vec, good_word.get("vector")) for good_word in good_words_obj_dv.values()]
	good_words_val = sum(good_word_distances)

	dict_val = lambda_d * good_words_val

	return freq_score + dict_val


'''
Function to calculate the cosine distance between two word vectors which will be between 0 and 2 where 
smaller numbers mean the words are closer together. If either vector doesn't exist then return 2
'''
def dist(word1_vec, word2_vec):
	if word1_vec and word2_vec:
		return cosine(word1_vec, word2_vec)
	else:
		return 2

'''
Function to calculate the score for a given candidate clue from weight based on edge type and number of edges away with 
a score of 0 if the clue doesn't exist
'''
def get_score(clue_obj):
	if clue_obj:
		return 1 / (clue_obj[0] * (clue_obj[1] + 1))
	else: 
		return 0