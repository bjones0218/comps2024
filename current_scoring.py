from orig_scoring import original_scoring
from detect import detect

good_words = ["germany", "car", "change", "glove", "needle", "robin", "belt",
"board", "africa", "gold"]
bad_words = ["pipe", "kid", "key", "boom", "satellite", "tap", "nurse", "pyramid", "rock", "bark"]
clue1 = "oil"
clue2 = "europe"

print(original_scoring(clue1, good_words, bad_words) + detect(clue1, good_words, bad_words))
print(original_scoring(clue2, good_words, bad_words) + detect(clue2, good_words, bad_words))
