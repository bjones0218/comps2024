import requests

# Set up the BabelNet API endpoint and API key
API_KEY = 'f0e09cff-8d83-4c31-94eb-65f86fa0e43f' 
BASE_URL = 'https://babelnet.io/v6/getSynsetIds'

# Function to get synsets for a given word
def get_synsets(word, lang='EN'):
    # Prepare parameters for the API request
    params = {
        'lemma': word,
        'searchLang': lang,
        'key': API_KEY
    }

    # Make the request to BabelNet
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        synsets = response.json()  # Parse the JSON response
        return synsets
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None

# Get synsets for the word
synsets = get_synsets('boat')

# Print the synsets
if synsets:
    print(f"Found {len(synsets)} synsets for the word 'boat':")
    for synset in synsets:
        print(synset)
else:
    print("No synsets found.")
