import requests
import json
import babelnet as bn
from babelnet.language import Language
from babelnet import BabelSynsetID
from babelnet.data.relation import BabelPointer
from pymongo import MongoClient


# Set up the BabelNet API endpoint and API key
API_KEY = 'f0e09cff-8d83-4c31-94eb-65f86fa0e43f' #Blake Key
# API_KEY = '3a8b4b6b-59c4-491c-a1ed-e1d7d74a634b' #Luke Key
# API_KEY = 'f316c32c-f2af-46d3-9112-a809c5e4138d' #Marc Key
# API_KEY = 'c51ec8b8-c993-47c9-86aa-b78e9a4a0cf8' #Sam Key


CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"
client = MongoClient(CONNECTION_STRING)
codenames_db = client["codenames_db"]  

if codenames_db["codenames_clues"] is not None:
    codenames_db.drop_collection("codenames_clues")

codenames_clues_collection = codenames_db["codenames_clues"]


# Takes a word as input and returns the babelnet synsets for that word
def get_synsets(word: str, lang='EN'):
	synsets = bn.get_synsets(word, from_langs=[Language.EN])

	return synsets


# Takes in a list of words, gets the synsets for the word and stores the synsets in a dictionary 
# where the given word is the key
def map_synsets_to_words(words: list) -> dict:
	word_synsets = dict()

	for word in words:
		curr_synsets = get_synsets(word)
		word_synsets[word] = curr_synsets

	return word_synsets

# For a given synset id, gets the outgoing edges, the type and the level of the edge
def get_outgoing_edges(synsetId, edgeNum, edgeType, edgesSoFar):
	if type(synsetId) == str:
		synsetId = BabelSynsetID(synsetId)

	by = bn.get_synset(synsetId)

	if by:
		edges = by.outgoing_edges()

		synsetArray = []
		for result in edges:
			if result.language == Language.EN:
				target = result.target
				pointer = result.pointer
				rel_type = pointer.short_name
				group = pointer.relation_group

				if pointer.is_automatic == False and target not in edgesSoFar:
					#Gets all synsets from initial edge
					if edgeNum == 0:
						synsetArray.append((result, 0))
						edgesSoFar.add(target)

						edgeOne = get_outgoing_edges(target, 1, rel_type, edgesSoFar)
						synsetArray.extend(edgeOne)
					# Gets only hypernyms for second edge
					elif edgeNum == 1:
						# print("look here the group: " + group)
						if group.ordinal == 0: # and (type == 'subclass_of' or type == 'is-a')

							synsetArray.append((result, 1))
							edgesSoFar.add(target)
								
							edgeTwo = get_outgoing_edges(target, 2, rel_type, edgesSoFar)
							synsetArray.extend(edgeTwo)
					#Gets same types of words for third edges
					elif edgeNum == 2:
						if rel_type == edgeType:
							synsetArray.append((result, 2))
							edgesSoFar.add(target)
		return synsetArray

	return None
	
def get_single_word_clues(synsetArray, singleWordLabels):
	W1 = 1.0
	W2 = 1.1
	W3 = 1.1
	W4 = 1.2

	for synset in synsetArray:
		synsetId = synset[0].target
		if type(synsetId) == str:
			synsetId = BabelSynsetID(synset[0].target)

		by = bn.get_synset(synsetId)

		main_sense = by.main_sense(Language.EN)
		senses = by.senses(Language.EN)

		if senses:
			split_main_sense = main_sense.full_lemma.split("_")

			if len(split_main_sense) == 1 and split_main_sense[0] not in singleWordLabels and split_main_sense[0].isalpha() and split_main_sense[0].isascii():
				singleWordLabels[split_main_sense[0]] = (W1, synset[1])
			else:
				for word in split_main_sense:
					if word not in singleWordLabels and word.isalpha() and word.isascii():
						singleWordLabels[word] = (W2, synset[1])
			
			for sense in senses:
				split_other_sense = sense.full_lemma.split("_")
				if len(split_other_sense) == 1 and split_other_sense[0] not in singleWordLabels and split_other_sense[0].isalpha() and split_other_sense[0].isascii():
					singleWordLabels[split_other_sense[0]] = (W3, synset[1])
				else:
					for word in split_other_sense:
						if word not in singleWordLabels and word.isalpha() and word.isascii():
							singleWordLabels[word] = (W4, synset[1])
	return singleWordLabels

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
	return word

def dist(word1, word2):
	# This is the cosine distance between the dict to vec word embeddings for each word
	# Need to figure out how to access dict to vec

	return distance






with open("word_list.txt", 'r') as file:
    lines = file.readlines()
	
# Get synsets for the word
for line in lines:
	line = line.strip()

	synsets = get_synsets(line)

	singleWordLabels = {}

	edgesFoundSet = set()


	for synset in synsets:
		array = get_outgoing_edges(synset.id, 0, "", edgesFoundSet)
		singleWordLabels = get_single_word_clues(array, singleWordLabels)

	existing_entry = codenames_clues_collection.find_one({"codenames_word": line})
	if existing_entry:
		codenames_clues_collection.update_one(
			{"codenames_word": line},
			{"$set": {"single_word_clues": singleWordLabels}}
		)
	else:
		codenames_clues_collection.insert_one({
			"codenames_word": line,
			"single_word_clues": singleWordLabels
		})
	print(f"Clues for '{line}' have been stored in the database.")


