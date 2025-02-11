from pymongo import MongoClient


# EVERYTHING FROM DICT2VEC GOES IN. THEN, IF IT DOESN'T HAVE A VECTOR IT GOES IN WITH NONE IN VECTOR
# IF IT WENT IN WITH A VECTOR AND DOESN'T HAVE A COUNT THE COUNT DEFAULTS TO 0

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

client = MongoClient(CONNECTION_STRING)

freq_and_vec_db = client["freq_and_vec"]

# Don't want to drop the collection here because this script runs after the dict2vec one
# if freq_and_vec_db["freq_and_vec"] is not None:
#     freq_and_vec_db.drop_collection("freq_and_vec_collection")

freq_and_vec_collection = freq_and_vec_db["freq_and_vec_collection"]

not_found = []
with open("enwiki-2023-04-13.txt", "r") as wiki_freq_file:
	for line in wiki_freq_file:
		temp = line.split(" ")
		word = temp[0]
		num_occurences = int(temp[1])
		if freq_and_vec_collection.find_one({"word": word.upper()}):
			print("FOUND:", word)
			freq_and_vec_collection.update_one({"word": word.upper()}, {"$set": {"count": num_occurences}})
		else:
			not_found.append(word)
			freq_and_vec_collection.insert_one({"word": word.upper(), "vector": None, "count": num_occurences})

print("COULDN'T FIND THESE WORDS IN DB:", not_found)