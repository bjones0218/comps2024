from nltk.stem import WordNetLemmatizer

import spacy  

lemmatizer2 = WordNetLemmatizer()

print(lemmatizer2.lemmatize("SPINAL"))
print(lemmatizer2.lemmatize("SPINE"))

nlp = spacy.load("en_core_web_sm")


text = "spine, spinal, dogs, dog, knives, knife, HOTELS, HOTEL"

# Process the text with spaCy
doc = nlp(text)

# Extract the lemmatized form of each token
for token in doc:
    print(token.lemma_)