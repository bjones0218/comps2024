from pymongo import MongoClient

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

client = MongoClient(CONNECTION_STRING)

freq_and_vec_db = client["freq_and_vec"]

if freq_and_vec_db["freq_and_vec"] is not None:
    freq_and_vec_db.drop_collection("freq_and_vec_collection")

freq_and_vec_collection = freq_and_vec_db["freq_and_vec_collection"]

with open("dict2vec-300d.vec", "r") as vector_file:
	next(vector_file) # skip first line
	for line in vector_file:
		temp = line.split(" ")
		word = temp[0]
		vector_vals = [float(num) for num in temp[1: 301]]
		vector = tuple(vector_vals)
		freq_and_vec_collection.insert_one({"word": word.upper(), "vector": vector, "count": 0})

print("DONE WITH VECTORS")

with open("enwiki-2023-04-13.txt", "r") as wiki_freq_file:
	for line in wiki_freq_file:
		temp = line.split(" ")
		word = temp[0]
		num_occurences = int(temp[1])
		if freq_and_vec_collection.find_one({"word": word.upper()}):
			freq_and_vec_collection.update_one({"word": word.upper()}, {"$set": {"count": num_occurences}})
		else:
			freq_and_vec_collection.insert_one({"word": word.upper(), "vector": None, "count": num_occurences})
