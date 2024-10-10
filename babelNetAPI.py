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

def get_outgoing_edges(synsetId):
	SERVICE_URL = 'https://babelnet.io/v9/getOutgoingEdges'

	params = {
		'id' : synsetId,
		'key'  : API_KEY
	}

	response = requests.get(SERVICE_URL, params=params)

	if response.status_code == 200:
		edges = response.json()

		# retrieving Edges data
		for result in edges:
			if result['language'] == 'EN':
				target = result.get('target')
				language = result.get('language')

				# retrieving BabelPointer data
				pointer = result['pointer']
				relation = pointer.get('name')
				group = pointer.get('relationGroup')

				print(language \
				+ "\t" + str(target) \
				+ "\t" + str(relation) \
				+ "\t" + str(group))
		
		return edges
	else:
		print(f"Error: Unable to fetch data. Status code: {response.status_code}")
		return None

# Get synsets for the word
synsets = get_synsets('boat')

if synsets:
	for synset in synsets:
		print(synset['id'] + "woohoo")
		get_outgoing_edges(synset['id'])

# Print the synsets
if synsets:
    print(f"Found {len(synsets)} synsets for the word 'boat':")
    for synset in synsets:
        print(synset)
else:
    print("No synsets found.")
