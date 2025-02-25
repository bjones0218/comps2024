from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cosine

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

def get_word_vectors(client, words):
    """Fetch word vectors from MongoDB for given words."""
    dict2vec_collection = client["dict2vec"]["dict2vec_collection"]
    word_vectors = {
        word: doc["vector"] for word in words
        if (doc := dict2vec_collection.find_one({"word": word}))
    }
    return word_vectors

def split_board(board, team):
    """Split the board into good words (team's words) and bad words (all other words)."""
    good_words = []
    bad_words = []
    for card_list in board.board:
        for card in card_list:
            if card.color == team and not card.guessed:
                good_words.append(card.word)
            elif not card.guessed:
                bad_words.append(card.word)
    return (good_words, bad_words)

def find_closest_word_pairs(word_vectors, good_words, num_pairs=78):
    """Find the closest word pairs for the team using cosine similarity."""
    if len(good_words) < 2:
        return []
    
    word_pairs = [
        (w1, w2, cosine(np.array(word_vectors[w1]), np.array(word_vectors[w2])))
        for i, w1 in enumerate(good_words) for w2 in good_words[i+1:]
    ]
    
    return sorted(word_pairs, key=lambda x: x[2])[:num_pairs]

def find_closest_opposing_word(word_vectors, bad_words, midpoint_vec):
    """Find the closest opposing team's word to the given midpoint vector."""
    if not bad_words:
        return None, float('inf')
    
    closest_word = min(
        ((word, cosine(np.array(word_vectors[word]), midpoint_vec)) for word in bad_words if word in word_vectors),
        key=lambda x: x[1], default=(None, float('inf'))
    )
    
    return closest_word

def compute_best_pair(word_vectors, good_words, bad_words):
    """Compute the best word pair for the AI's clue generation."""
    word_pairs = find_closest_word_pairs(word_vectors, good_words)
    if not word_pairs:
        return None
    
    best_score, best_pair = float('-inf'), None
    for w1, w2, dist in word_pairs:
        midpoint_vec = (np.array(word_vectors[w1]) + np.array(word_vectors[w2])) / 2
        opp_word, dist_opp = find_closest_opposing_word(word_vectors, bad_words, midpoint_vec)
        
        if opp_word is None:
            dist_opp = 1.0  # Default value if no opposing word is found
        
        score = dist_opp - (dist / 2)
        print(f"Pair: ({w1}, {w2}), Score: {score:.4f}, Opposing Word: {opp_word}, Distance to Opposing: {dist_opp:.4f}")
        if score > best_score:
            best_score, best_pair = score, (w1, w2)
    
    return best_pair

def get_clue(words_obj, given_clues, board):
    """Main function to find and return the best AI-generated clue given the board."""
    print("Current Board:")
    for row in board.board:
        print(" | ".join(card.word for card in row))
    print("\n")
    
    good_words, bad_words = words_obj
    all_words = good_words + bad_words
    print(f"Good Words: {good_words}")
    print(f"Bad Words: {bad_words}")
    
    client = MongoClient(CONNECTION_STRING)
    word_vectors = get_word_vectors(client, all_words)
    client.close()
    
    print(f"Fetched {len(word_vectors)} word vectors.")
    best_pair = compute_best_pair(word_vectors, good_words, bad_words)
    if not best_pair:
        print("No valid word pair found.")
        return "No valid clue found", 1
    
    w1, w2 = best_pair
    print(f"Selected Best Pair: {w1}, {w2}")
    midpoint_vec = (np.array(word_vectors[w1]) + np.array(word_vectors[w2])) / 2
    
    client = MongoClient(CONNECTION_STRING)
    dict2vec_collection = client["dict2vec"]["dict2vec_collection"]
    
    best_clue, min_distance = None, float('inf')
    print(f"Computing best clue for words: {w1}, {w2}")
    for doc in dict2vec_collection.find():
        word, vector = doc["word"], np.array(doc["vector"])
        if word in {w1, w2} or any(w in word for w in {w1, w2}):
            continue
        
        distance = cosine(vector, midpoint_vec)
        if distance < min_distance and len(word) > 1:
            min_distance, best_clue = distance, word
            print(f"New Best Clue: {best_clue}, Distance: {min_distance:.4f}")
    
    client.close()
    
    if not best_clue or len(best_clue) < 2:
        print("Invalid clue generated, returning fallback.")
        return "No valid clue found", 1
    
    print(f"Final Best Clue: {best_clue}")
    return best_clue, 2
