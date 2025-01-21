from pymongo import MongoClient


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"
client = MongoClient(CONNECTION_STRING)
db = client["codenames_db"]
words_collection = db["codenames_clues"]

def original_scoring(clue, good_words, bad_words):
	lambda_good = 1
	lambda_bad = 0.5
	cur_score = 0
	clue_score = 0
	
	#find all words on good board where clue is candidate clue and calculates score
	for word in good_words:
		cur_dict = words_collection.find_one({"codenames_word":word})
		if (cur_dict):
			cur_weights = cur_dict.get('single_word_clues').get(clue)
			if cur_weights:
				print(clue, cur_weights)
				cur_score += 1/((cur_weights[1]+1) * cur_weights[0])
				print(cur_score)
	max_bad = origional_scoring_max(clue, bad_words)
	clue_score = lambda_good*cur_score - lambda_bad*max_bad
	

	return clue_score
		
# finds max negative score to penalize original scoring function with			
def origional_scoring_max(clue, bad_words):
	cur_max = 0
	for word in bad_words:
		cur_dict = words_collection.find_one({"codenames_word":word})
		if (cur_dict):
			cur_weights = cur_dict.get('single_word_clues').get(clue)
			if cur_weights:
				print(clue, cur_weights)
				cur_score = 1/((cur_weights[1]+1) * cur_weights[0])
				if cur_score > cur_max:
					cur_max = cur_score
	return cur_max


	
# original_scoring('Teen', ["AFRICA"], ["BOAT"])