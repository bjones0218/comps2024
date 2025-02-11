from nltk.stem import WordNetLemmatizer, PorterStemmer, LancasterStemmer

import spacy  

lemmatizer2 = WordNetLemmatizer()

stemmer = PorterStemmer()
stemmer2 = LancasterStemmer()

print(stemmer2.stem("teaching"))
print(stemmer2.stem("teacher"))
print(stemmer2.stem("knife"))
print(stemmer2.stem("knives"))


print(lemmatizer2.lemmatize("teaching"))
print(lemmatizer2.lemmatize("teacher"))

nlp = spacy.load("en_core_web_sm")


text = "spine, spinal, dogs, dog, knives, knife, HOTELS, HOTEL, hotel, hotels, teaching, teacher, TEACHING, TEACHER"

# Process the text with spaCy
doc = nlp(text)

# Extract the lemmatized form of each token
for token in doc:
    print(token.lemma_)