from nltk.stem import WordNetLemmatizer, PorterStemmer, LancasterStemmer

import spacy  

stemmer = LancasterStemmer()
nlp = spacy.load("en_core_web_sm")

original_text = ["teach", "teacher", "teaching", "knife", "knives", "speak", "spoken", "speaker"]

stemmed_text = [stemmer.stem(word) for word in original_text]

process = nlp(" ".join(original_text))
lemmatized_text = [word.lemma_ for word in process]
print("The original words are: ", original_text)
print("The stemmed words are: ", stemmed_text)
print("The lemmatized words are: ", lemmatized_text)
