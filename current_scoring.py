from orig_scoring import original_scoring
from detect import detect

good_words = ["GERMANY", "CAR", "CHANGE", "GLOVE", "NEEDLE", "ROBIN", "BELT",
"BOARD", "AFRICA", "GOLD"]
bad_words = ["PIPE", "KID", "KEY", "BOOM", "SATELLITE", "TAP", "NURSE", "PYRAMIDS", "ROCK", "BARK"]
clue2 = "EUROPE"


print("The words for your team are:", good_words)
print("The words for the other team are:", bad_words)
clue = input("Your clue is: ").upper()

print("Your clue score is:", original_scoring(clue, good_words, bad_words) + detect(clue, good_words, bad_words))
print("The clue given in the paper for these words is:", clue2)
print("The score for that word is:", original_scoring(clue2, good_words, bad_words) + detect(clue2, good_words, bad_words))