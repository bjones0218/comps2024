import random
import time
from ai_cluegiver_orig import get_clue

def get_random_strings():
	with open("../codenames_game_files/word_list_copy.txt", 'r') as file:
		lines = file.readlines()
	return random.sample(lines, 25)

def split_words(words, good_words, bad_words):
	unvisited = set(range(len(words)))
	for i in range(len(words)):
		index = random.choice(list(unvisited))
		word = words[index].strip()
		if i % 2 == 0: #this cause red to have one more in odd num sized boards
			good_words.append(word)
		else:
			bad_words.append(word)
		unvisited.remove(index)



if __name__ == "__main__":
	for _ in range(40):
		board_words = get_random_strings()
		good_words = []
		bad_words = []

		split_words(board_words, good_words, bad_words)

		all_words = good_words + bad_words
		random.shuffle(all_words)

		start_time = time.time()
		clue_obj = get_clue(good_words, bad_words)
		end_time = time.time()
		with open("../clue_output_files/final_test3.txt", "a") as output_file:
			output_file.write(f"The good words are: {good_words}\n")
			output_file.write(f"The bad words are: {bad_words}\n")
			output_file.write(f"All the board words are: {all_words}\n")
			output_file.write(f"The best clue is {clue_obj[1][0]} with a score of {clue_obj[1][1]} which connects {clue_obj[0]}\n")
			output_file.write(f"The time it took to generate this clue was: {end_time - start_time} seconds\n")
			output_file.write(f"---------------------------\n")
