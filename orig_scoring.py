from pymongo import MongoClient


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"
client = MongoClient(CONNECTION_STRING)

def original_scoring(clue, team):
	lambda_b = 1
	lambda_r = 0.5
	blue_words = []
	red_words = []
	cur_score= 0
	if team == "B":
		#find all words on blue board where clue is candidate clue
		for word in blue_words:
			#check mongoDB and retrieve data if candidate clue exists
			cur_score += 1/((mongoResult[1][1]+1) *mongoResult[1][0])
		max_red = origional_scoring_max(clue, red_words)
		clue_score = lambda_b*cur_score - lambda_r*max_red
	elif team == "R":
		#find all words on blue board where clue is candidate clue
		for word in red_words:
			#check mongoDB and retrieve data if candidate clue exists
			cur_score += 1/((mongoResult[1][1]+1) *mongoResult[1][0])
		max_blue = origional_scoring_max(clue, blue_words)
		clue_score = lambda_r*cur_score - lambda_b*max_blue

	return clue_score
		
					
def origional_scoring_max(clue, words):
	cur_max = 0
	for word in words:
		#check mongoDB and retrieve data if candidate clue exists
		cur_score += 1/((mongoResult[1][1]+1) *mongoResult[1][0])
		if cur_score > cur_max:
			cur_max = cur_score
	return cur_max
	