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
    
    def create_cards(self, words):

        unvisited = set(range(len(words)))
        for i in range(len(words)):
            if i % 2 == 0: #this cause red to have one more in odd num sized boards
                color = "red"
            else:
                color = "blue"

            index = random.choice(list(unvisited))
            new_card = Card(words[index].strip(), color)
            words[index] = new_card
            unvisited.remove(index)
        
        return words

    def init_board(self, words):
        curr = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                self.board[i][j] = words[curr]
                curr += 1

    def print_board_color(self):
        RED = "\033[31m"
        BLUE = "\033[34m"
        DEFAULT = "\033[0m"
        line = ""

        for row in self.board:
            for col in row:
                if col.color == "blue":
                    line += BLUE + col.word + " "
                elif col.color == "red":
                    line += RED + col.word + " "
            print(line + DEFAULT) #adding default resets to normal color afterwards for following prints
            line = ""

    def print_board_plain(self):
        line = ""

        for row in self.board:
            for col in row:
                line += col.word + " "
            print(line)
            line = ""

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
    card_list = codenames.create_cards(board_words)

    codenames.init_board(card_list)

    codenames.print_board_color()
    codenames.print_board_plain()

if __name__ == "__main__":
    main()