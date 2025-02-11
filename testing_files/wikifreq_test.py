import matplotlib.pyplot as plt
import numpy as np

# https://github.com/IlyaSemenov/wikipedia-word-frequency/blob/master/results/enwiki-2023-04-13.txt

word_array = []
with open("enwiki-2023-04-13.txt", "r") as wiki_freq_file:
	for line in wiki_freq_file:
		temp = line.split(" ")
		word = temp[0]
		num_occurances = int(temp[1])
		word_array.append((word, num_occurances))



def freq(num) -> float:
	# Calculate document frequency of word which was done in paper from what number of cleaned wikipedia articles the word was found in
	# Empirically calculated alpha to be 1/1667 in paper
	alpha = 1/1667 # This might have to change if we arent getting enough common words

	if (1/num) >= alpha:
		return -(1/num)
	else:
		return -1
	

x_vals = np.array([word[1] for word in word_array])
y_vals = np.array([freq(word[1]) for word in word_array])

plt.plot(x_vals, y_vals, "o")
plt.xlim(1, 2000)
plt.savefig('plot.png')  # Save as PNG