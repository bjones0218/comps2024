from pymongo import MongoClient


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

client = MongoClient(CONNECTION_STRING)

dict2vec_db = client["dict2vec"]

if dict2vec_db["dict2vec_collection"] is not None:
    dict2vec_db.drop_collection("dict2vec_collection")

dict2vec_collection = dict2vec_db["dict2vec_collection"]

with open("dict2vec-300d.vec", "r") as vector_file:
	next(vector_file) # skip first line
	for line in vector_file:
		temp = line.split(" ")
		word = temp[0]
		vector_vals = [float(num) for num in temp[1: 301]]
		vector = tuple(vector_vals)
		dict2vec_collection.insert_one({"word": word.upper(), "vector": vector})


