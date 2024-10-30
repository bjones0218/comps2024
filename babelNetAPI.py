import requests
import json

# Set up the BabelNet API endpoint and API key
# API_KEY = 'f0e09cff-8d83-4c31-94eb-65f86fa0e43f' #Blake Key
API_KEY = '3a8b4b6b-59c4-491c-a1ed-e1d7d74a634b' #Luke Key
# API_KEY = 'f316c32c-f2af-46d3-9112-a809c5e4138d' #Marc Key
# API_KEY = 'c51ec8b8-c993-47c9-86aa-b78e9a4a0cf8' #Sam Key


# Function to get synsets for a given word
def get_synsets(word: str, lang='EN'):
	SERVICE_URL = 'https://babelnet.io/v6/getSynsetIds'

	# Prepare parameters for the API request
	params = {
		'lemma': word,
		'searchLang': lang,
		'key': API_KEY
    }

	# Make the request to BabelNet
	response = requests.get(SERVICE_URL, params=params)
    
	if response.status_code == 200:
		synsets = response.json()  # Parse the JSON response
		return synsets
	else:
		print(f"Error: Unable to fetch data. Status code: {response.status_code}")
		return None
    
def map_synsets_to_words(words: list) -> dict:
	word_synsets = dict()

	for word in words:
		curr_synsets = get_synsets(word)
		word_synsets[word] = curr_synsets

	return word_synsets

def get_outgoing_edges(synsetId, edgeNum, edgeType, edgesSoFar):
	SERVICE_URL = 'https://babelnet.io/v9/getOutgoingEdges'
	params = {
		'id' : synsetId,
		'key'  : API_KEY
	}

	response = requests.get(SERVICE_URL, params=params)

	if response.status_code == 200:
		edges = response.json()
		# retrieving Edges data

		synsetArray = []

		for result in edges:
			if result['language'] == 'EN':
				target = result.get('target') #Target synset

				# retrieving BabelPointer data
				pointer = result['pointer']
				type = pointer.get('shortName') #is-a, part-of, etc.
				group = pointer.get('relationGroup') #HYPERNYM, HYPONYM, etc.

				if pointer.get('isAutomatic') == False and target not in edgesSoFar:
					#Gets all synsets from initial edge
					if edgeNum == 0:
						synsetArray.append(result)
						edgesSoFar.add(target)

						edgeOne = get_outgoing_edges(target, 1, type, edgesSoFar)
						synsetArray.extend(edgeOne)

						with open('edgesdata'+ str(edgeNum) +'.json', 'w') as edges_stuff:
							json.dump(result, edges_stuff)
					#Gets only hypernyms for second edge
					elif edgeNum == 1:
						if group == 'HYPERNYM' and (type == 'subclass_of' or type == 'is-a'):
							synsetArray.append(result)
							edgesSoFar.add(target)

							with open('edgesdata'+ str(edgeNum) +'.json', 'w') as edges_stuff:
								json.dump(result, edges_stuff)	
								
							edgeTwo = get_outgoing_edges(target, 2, type, edgesSoFar)
							synsetArray.extend(edgeTwo)
					#Gets same types of words for third edges
					elif edgeNum == 2:
						if type == edgeType:
							synsetArray.append(result)
							edgesSoFar.add(target)

							with open('edgesdata'+ str(edgeNum) +'.json', 'w') as edges_stuff:
								json.dump(result, edges_stuff)

		return synsetArray
	else:
		print(f"Error: Unable to fetch data. Status code: {response.status_code}")
		return None
	
def get_single_word_clues(synsetArray, singleWordLabels):
	W1 = 1.0
	W2 = 1.1
	W3 = 1.1
	W4 = 1.2

	for synset in synsetArray:
		SYNSET_INFO_URL = 'https://babelnet.io/v9/getSynset'
		synsetParams = {
			'id' : synset['target'],
			'key'  : API_KEY
		}
		synsetResponse = requests.get(SYNSET_INFO_URL, params=synsetParams)

		if synsetResponse.status_code == 200:
			senses = synsetResponse.json()
			senses = senses.get('senses', [])

		if senses:
			main_sense = senses[0]  # The first sense is usually considered the main sense
			other_senses = senses[1:]  # The rest are other senses

			split_main_sense = main_sense.get('properties', {}).get('fullLemma').split("_")

			if len(split_main_sense) == 1 and split_main_sense[0] not in singleWordLabels:
				singleWordLabels[split_main_sense[0]] = W1
			else:
				for word in split_main_sense:
					if word not in singleWordLabels:
						singleWordLabels[word] = W2
			
			for sense in other_senses:
				split_other_sense = sense.get('properties', {}).get('fullLemma').split("_")
				if len(split_other_sense) == 1 and split_other_sense[0] not in singleWordLabels:
					singleWordLabels[split_other_sense[0]] = W3
				else:
					for word in split_other_sense:
						if word not in singleWordLabels:
							singleWordLabels[word] = W4

			# Extract and print main sense
			# main_sense_lemma = main_sense.get('properties', {}).get('fullLemma')
			# main_sense_language = main_sense.get('properties', {}).get('language')
			# main_sense_source = main_sense.get('source')

			# print(f"Main Sense:\nLemma: {main_sense_lemma}\nLanguage: {main_sense_language}\nSource: {main_sense_source}\n")

			# Extract and print other senses
			# print("Other Senses:")
			# for sense in other_senses:
			# 	lemma = sense.get('properties', {}).get('fullLemma')
			# 	language = sense.get('properties', {}).get('language')
			# 	source = sense.get('source')
			# 	print(f"Lemma: {lemma}\tLanguage: {language}\tSource: {source}\n")
	return singleWordLabels

word = "boat"
# Get synsets for the word
synsets = get_synsets(word)

synset_we_want = None
for synset in synsets:
	if synset['id'] == 'bn:00011674n':
		synset_we_want = synset

singleWordLabels = {}

edgesFoundSet = set()
if synset_we_want:
	array = get_outgoing_edges(synset_we_want['id'], 0, "", edgesFoundSet)
	print("The length of edge array: " + str(len(array)))

# with open('synsetArray.json', 'w') as f:
#     for item in array:
#         json.dump(item, f)
# with open("synsetArray.txt", 'r') as f:
#         lines = f.readlines()


# for line in lines:
# 	data.append(json.loads(line))

singleWordLabels = get_single_word_clues(array, singleWordLabels)


# print("The len of single word labels: " + str(len(singleWordLabels)))


with open('singleWordLabels.txt', 'w') as lf:
	for key, value in singleWordLabels.items():
		lf.write(key, ":", str(value) + '\n')

