from pymongo import MongoClient

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

client = MongoClient(CONNECTION_STRING)

freq_and_vec_db2 = client["freq_and_vec2"]

# if freq_and_vec_db2["freq_and_vec2"] is not None:
#     freq_and_vec_db2.drop_collection("freq_and_vec_collection2")

freq_and_vec_collection2 = freq_and_vec_db2["freq_and_vec_collection2"]

# Sort vector file
# with open("dict2vec-300d.vec", "r") as vector_file:
# 	lines_v = vector_file.readlines()
# 	lines_v = lines_v[1:]
# 	lines_v.sort(key=lambda x: x.split(" ")[0])
# 	with open("dict_to_vec_output.txt", "w") as output_file_v:
# 		output_file_v.writelines(lines_v)
	
# # Sort freq file
# with open("enwiki-2023-04-13.txt", "r") as wiki_freq_file:
# 	lines_wf = wiki_freq_file.readlines()
# 	lines_wf.sort(key=lambda x: x.split(" ")[0])
# 	with open("frequency_output.txt", "w") as output_file_wf:
# 		output_file_wf.writelines(lines_wf)


with open("frequency_output.txt", "r") as freq_file, open("dict_to_vec_output.txt", "r") as vec_file:
	freq_line = freq_file.readline().strip()
	vec_line = vec_file.readline().strip()

	while freq_line or vec_line:
		temp_freq = freq_line.split(" ")
		temp_vec = vec_line.split(" ")
		freq_word = temp_freq[0]
		vec_word = temp_vec[0]
		count = int(temp_freq[1])
		vector_vals = [float(num) for num in temp_vec[1: 301]]
		vector = tuple(vector_vals)

		
		if not freq_word.isascii():
			print("FREQ WORD:", freq_word)
		if not vec_word.isascii():
			print("VEC WORD:", vec_word)


		if freq_word and vec_word:
			if freq_word < vec_word:
				# Only exists in frequency
				if freq_word.isascii():
					freq_and_vec_collection2.insert_one({"word": freq_word.upper(), "vector": None, "count": count})
				freq_line = freq_file.readline().strip()
			elif vec_word < freq_word:
				# Only exists in vector
				if vec_word.isascii():
					freq_and_vec_collection2.insert_one({"word": vec_word.upper(), "vector": vector, "count": 0})
				vec_line = vec_file.readline().strip()
			elif freq_word == vec_word:
				# Exists in both
				# Just check vecword but should be the same
				if vec_word.isascii():
					freq_and_vec_collection2.insert_one({"word": vec_word.upper(), "vector": vector, "count": count})
				freq_line = freq_file.readline().strip()
				vec_line = vec_file.readline().strip()
			else: 
				# Should never happen
				print("THIS SHOULDN'T HAPPEN 1")
		else:
			if freq_word:
				# Only exists in frequency
				if freq_word.isascii():
					freq_and_vec_collection2.insert_one({"word": freq_word.upper(), "vector": None, "count": count})
				freq_line = freq_file.readline().strip()
			elif vec_word:
				# Only exists in vector
				if vec_word.isascii():
					freq_and_vec_collection2.insert_one({"word": vec_word.upper(), "vector": vector, "count": 0})
				vec_line = vec_file.readline().strip()
			else:
				# Should never happen
				print("THIS SHOULDN'T HAPPEN 2")



		# 	# MIGHT NEED TO CHANGE LOGIC
		# 	if not freq_word.isascii():
		# 		freq_line = freq_file.readline().strip()
		# 	elif not vec_word.isascii():
		# 		vec_line = vec_file.readline().strip()
		# 	else: 
		# 		if freq_word.isascii() and vec_word.isascii():
		# 			if freq_word < vec_word:
		# 				# Only exists in frequency
		# 				freq_and_vec_collection2.insert_one({"word": freq_word.upper(), "vector": None, "count": count})
		# 				freq_line = freq_file.readline().strip()
		# 			elif vec_word < freq_word:
		# 				# Only exists in vector
		# 				freq_and_vec_collection2.insert_one({"word": vec_word.upper(), "vector": vector, "count": 0})
		# 				vec_line = vec_file.readline().strip()
		# 			elif freq_word == vec_word:
		# 				# Exists in both
		# 				freq_and_vec_collection2.insert_one({"word": vec_word.upper(), "vector": vector, "count": count})
		# 				freq_line = freq_file.readline().strip()
		# 				vec_line = vec_file.readline().strip()
		# 			else: 
		# 				# Should never happen
		# 				print("THIS SHOULDN'T HAPPEN 1")
		# else:
		# 	if freq_word:
		# 		if not freq_word.isascii():
		# 			freq_line = freq_file.readline().strip()
		# 		else:
		# 			# Only exists in frequency
		# 			freq_and_vec_collection2.insert_one({"word": freq_word.upper(), "vector": None, "count": count})
		# 			freq_line = freq_file.readline().strip()
		# 	elif vec_word:
		# 		if not vec_word.isascii():
		# 			vec_line = vec_file.readline().strip()
		# 		else:
		# 			# Only exists in vector
		# 			freq_and_vec_collection2.insert_one({"word": vec_word.upper(), "vector": vector, "count": 0})
		# 			vec_line = vec_file.readline().strip()
		# 	else:
		# 		# Should never happen
		# 		print("THIS SHOULDN'T HAPPEN 2")


# with open("enwiki-2023-04-13.txt", "r") as wiki_freq_file, open("dict2vec-300d.vec", "r") as vector_file:
# 	next(vector_file)
# 	for line_v in vector_file:
# 		temp_v = line_v.split(" ")
# 		word_v = temp_v[0]
# 		vector_vals = [float(num) for num in temp_v[1: 301]]
# 		vector = tuple(vector_vals)
# 		for line_wf in wiki_freq_file:
# 			temp_wf = line_wf.split(" ")
# 			word_wf = temp_wf[0]
# 			num_occurences = int(temp_wf[1])
# 			# Word exists in both db's
# 			if word_v == word_wf:
# 				freq_and_vec_collection2.insert_one({"word": word_v.upper(), "vector": vector, "count": num_occurences})
# 		# Word only exists in vector so no count
# 		freq_and_vec_collection2.insert_one({"word": word_v.upper(), "vector": vector, "count": 0})
