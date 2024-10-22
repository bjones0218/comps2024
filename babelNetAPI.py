import requests

# Set up the BabelNet API endpoint and API key
API_KEY = 'f0e09cff-8d83-4c31-94eb-65f86fa0e43f' 


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

def get_outgoing_edges(synsetId, edgeNum, edgeType):
	SERVICE_URL = 'https://babelnet.io/v9/getOutgoingEdges'
	params = {
		'id' : synsetId,
		'key'  : API_KEY
	}

	response = requests.get(SERVICE_URL, params=params)

	if response.status_code == 200:
		edges = response.json()

		# if edgeNum == 0:
		# 	hypernyms = [
		# 		relation for relation in edges['relations']
		# 		if relation['relationType'] == 'HYPERNYM']

		# 	for result in hypernyms:
		# 		if result['language'] == 'EN':
		# 			target = result.get('target') #Target synset
		# 			language = result.get('language') 

		# 			# retrieving BabelPointer data
		# 			pointer = result['pointer']
		# 			relation = pointer.get('name') # hypernym hyponym etc
		# 			type = pointer.get('shortName') #is-a, part-of, etc.
		# 			group = pointer.get('relationGroup') #HYPERNYM, HYPONYM, etc.

		# 			print(language \
		# 			+ "\t" + str(target) \
		# 			+ "\t" + str(relation) \
		# 			+ "\t" + str(type) \
		# 			+ "\t" + str(group))
			

		# retrieving Edges data

		#CRETAE ARRAY WHERE EVERYTHING IS STORED, TALK WITH BLAKE ABOUT HOW

		#IF EDGE NUM IS 0, COPY THE ENTIRE EDGES TO ARRAY
		synsetArray = []


		for result in edges:
			if result['language'] == 'EN':
				target = result.get('target') #Target synset
				language = result.get('language') 

				# retrieving BabelPointer data
				pointer = result['pointer']
				relation = pointer.get('name') # hypernym hyponym etc
				type = pointer.get('shortName') #is-a, part-of, etc.
				group = pointer.get('relationGroup') #HYPERNYM, HYPONYM, etc.

				#Gets all synsets from initial edge
				if edgeNum == 0:
					synsetArray.append(result)
					print("HYPERNYM GROUP WITH EDGE 0")
					edgeOne = get_outgoing_edges(target, 1, type)
					synsetArray.extend(edgeOne)
				#Gets only hypernyms for first edge
				elif edgeNum == 1:
					if group == 'HYPERNYM':
						synsetArray.append(result)
						print("same edge type")
						edgeTwo = get_outgoing_edges(target, 2, type)
						synsetArray.extend(edgeTwo)
				#Gets same types of words for second edges
				elif edgeNum == 2:
					if type == edgeType:
						synsetArray.append(result)
						print("same edge type")
						edgeThree = get_outgoing_edges(target, 3, type)
						synsetArray.extend(edgeThree)
				#Stops at third edge but must be same type
				elif edgeNum == 3:
					if type == edgeType:
						synsetArray.append(result)
						print("same edge type")

				print(language \
				+ "\t" + str(target) \
				+ "\t" + str(relation) \
				+ "\t" + str(type) \
				+ "\t" + str(group))
		
		return synsetArray
	else:
		print(f"Error: Unable to fetch data. Status code: {response.status_code}")
		return None

word = "boat"
# Get synsets for the word
synsets = get_synsets(word)

if synsets:
	for synset in synsets:
		print(synset['id'] + "woohoo")
		get_outgoing_edges(synset['id'], 0, "")

# Print the synsets
if synsets:
    print(f"Found {len(synsets)} synsets for the word '" + word + "':")
    for synset in synsets:
        print(synset)
else:
    print("No synsets found.")
