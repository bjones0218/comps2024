from pymongo import MongoClient


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

client = MongoClient(CONNECTION_STRING)

wiki_freq_db = client["wiki_freq"]

if wiki_freq_db["wiki_freq_collection"] is not None:
    wiki_freq_db.drop_collection("wiki_freq_collection")

dict2vec_collection = wiki_freq_db["wiki_freq_collection"]


with open("enwiki-2023-04-13.txt", "r") as wiki_freq_file:
	for line in wiki_freq_file:
		temp = line.split(" ")
		word = temp[0]
		num_occurances = int(temp[1])
		dict2vec_collection.insert_one({"word": word, "count": num_occurances})
