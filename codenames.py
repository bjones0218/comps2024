import random

class Game:
    def __init__(self, cols, rows):
        self.num_words = cols * rows
        self.word_list_file = "word_list.txt"
        self.board = [["" for _ in range(cols)] for _ in range(rows)]

    def get_random_strings(self):
        with open(self.word_list_file, 'r') as file:
            lines = file.readlines()
        return random.sample(lines, self.num_words)
    
    def init_board(self, words):
        curr = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                self.board[i][j] = words[curr].strip()
                curr += 1

    def print_board(self):
        for row in self.board:
            print(row)

class Card:
    def __init__(self, word, color):
        self.word = word
        self.color = color

    def get_color(self):
        return self.color
    
    def get_word(self):
        return self.word


def main():
    codenames = Game(5, 5)
    board_words = codenames.get_random_strings()

    codenames.init_board(board_words)

    codenames.print_board()

if __name__ == "__main__":
    main()
