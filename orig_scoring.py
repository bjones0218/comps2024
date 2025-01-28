from pymongo import MongoClient


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"
client = MongoClient(CONNECTION_STRING)
db = client["codenames_db"]
words_collection = db["codenames_clues"]

def get_good_word_obj_bbn(good_words):
	return {word: words_collection.find_one({"codenames_word": word}) for word in good_words}

def get_bad_word_obj_bbn(bad_words):
	return {word: words_collection.find_one({"codenames_word": word}) for word in bad_words}

def get_score(clue_obj):
	if clue_obj:
		return 1 / (clue_obj[0] * (clue_obj[1] + 1))
	else: 
		return 0


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
	print(clue, good_score)
	# good_score = 0



	bad_score_array = [get_score(bad_word_obj.get('single_word_clues').get(clue)) for bad_word_obj in bad_words_obj_bbn.values()]
	# bad_score_array = [1 / ((bad_word_obj.get('single_word_clues').get(clue)[0] * bad_word_obj.get('single_word_clues').get(clue)[1]) + 1) if bad_word_obj.get('single_word_clues').get(clue) else 0 for bad_word_obj in bad_words_obj_bbn.values()]
	bad_score = max(bad_score_array)
	#print(bad_score_array)

	clue_score = (lambda_good * good_score) - (lambda_bad * bad_score)

	return clue_score

# good_words = ['KNIGHT', 'KNIFE', 'NAIL', 'CENTAUR', 'SHOT', 'MAMMOTH', 'RAY', 'BOMB', 'PARK', 'LIGHT', 'MISSILE', 'BACK', 'PIN']
# bad_words = ['TELESCOPE', 'LINE', 'YARD', 'RACKET', 'COTTON', 'DRAFT', 'RABBIT', 'SUIT', 'PASS', 'OLYMPUS', 'KING', 'BOTTLE']

# original_scoring("WEAPON", get_good_word_obj_bbn(good_words), get_bad_word_obj_bbn(bad_words))
# original_scoring("DOG", get_good_word_obj_bbn(good_words), get_bad_word_obj_bbn(bad_words))


# 	for good_word_obj in good_words_obj:
# 		if good_word_obj:
# 			clue_info = good_word_obj.get('single_word_clues').get(clue)
# 			if clue_info:
# 				score = 

	
# 	#find all words on good board where clue is candidate clue and calculates score
# 	for word in good_words:
# 		cur_dict = words_collection.find_one({"codenames_word": word})
# 		if (cur_dict):
# 			cur_weights = cur_dict.get('single_word_clues').get(clue)
# 			if cur_weights:
# 				print(clue, cur_weights)
# 				cur_score += 1/((cur_weights[1]+1) * cur_weights[0])
# 				#print(cur_score)
# 	max_bad = original_scoring_max(clue, bad_words)
# 	clue_score = lambda_good*cur_score - lambda_bad*max_bad
	

# 	return clue_score
		
# # finds max negative score to penalize original scoring function with			
# def original_scoring_max(clue, bad_words):
# 	cur_max = 0
# 	for word in bad_words:
# 		cur_dict = words_collection.find_one({"codenames_word":word})
# 		if (cur_dict):
# 			cur_weights = cur_dict.get('single_word_clues').get(clue)
# 			if cur_weights:
# 				#print(clue, cur_weights)
# 				cur_score = 1/((cur_weights[1]+1) * cur_weights[0])
# 				if cur_score > cur_max:
# 					cur_max = cur_score
# 	return cur_max


	
# original_scoring('Teen', ["AFRICA"], ["BOAT"])