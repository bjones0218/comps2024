from pymongo import MongoClient
from scipy.spatial.distance import cosine


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

client = MongoClient(CONNECTION_STRING)

dict2vec_db = client["dict2vec"]

dict2vec_collection = dict2vec_db["dict2vec_collection"]


word_1 = "man"
vec1 = dict2vec_collection.find_one({"word": "boat"}).get("vector")

max_dist = 0
min_dist = .5
close_words = []
for word_2 in dict2vec_collection.find():

	if cosine(vec1, word_2.get("vector")) > max_dist:
		max_dist = cosine(vec1, word_2.get("vector"))
		max_word = word_2.get("word")
	if cosine(vec1, word_2.get("vector")) < min_dist:
		close_words.append((word_2.get("word"), cosine(vec1, word_2.get("vector"))))
		

print(max_word)
print(max_dist)
print("----------------")
print(close_words)
print(min_dist)