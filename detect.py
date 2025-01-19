

def detect(clue, team):
	lambda_f = 2 # WILL CHANGE PROB
	lambda_d = 2 # WILL CHANGE PROB

	freq_val = lambda_f * freq(clue)
	good_words_val = 0
	# HERE WE NEED TO GET TEAM WORDS
	for good_word in team_words:
		good_words_val = good_words_val + 1 - dist(clue, word)
	bad_words_val = 0
	for bad_word in other_team_words:
		current_val = 1 - dist(clue, bad_word)
		if current_val > bad_words_val:
			bad_words_val = current_val
	dict_val = lambda_d * (good_words_val - bad_words_val)

	return freq_val + dict_val



def freq(word):
	# Calculate document frequency of word which was done in paper from what number of cleaned wikipedia articles the word was found in
	# Empirically calculated alpha to be 1/1667 in paper
	alpha = 1/1667
	frequency = get_frequency(word)
	if (1/frequency) >= alpha:
		return -(1/frequency)
	else:
		return -1

def get_frequency(word):
	# Queries the database of frequencies of words and returns the value
	# Need to figure out how to access wikipedia info

	return frequency

def dist(word1, word2):
	# This is the cosine distance between the dict to vec word embeddings for each word

	vec1 = dict2vec_collection.find_one({"word": word1}).get("vector")
	vec2 = dict2vec_collection.find_one({"word": word2}).get("vector")
	distance = cosine(vec1, vec2)

	return distance

