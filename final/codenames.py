import random
import os
from ai_cluegiver import get_clue, split_board

# TODO: NOTES TO FIX: 
# IF YOU DONT SAY YES BUT WANT TO GUESS AGAIN WEIRD THINGS AHPPEN 



class Card:
    def __init__(self, word, color):
        self.word = word
        self.color = color
        self.guessed = False

    def guess_card(self):
        self.guessed = True
        return self.color()

    def get_color(self):
        return self.color
    
    def get_word(self):
        return self.word

class Board:
    card_locations = {}

    def __init__(self, cols, rows):
        self.num_words = cols * rows
        self.cols = cols
        self.rows = rows
        self.word_list_file = "word_list_copy.txt"
        self.valid_words = set()
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

    def init_board(self, cards):
        curr = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                self.board[i][j] = cards[curr]
                self.valid_words.add(cards[curr].word)
                self.card_locations[cards[curr].word] = (i, j)
                curr += 1

    def print_board_color(self):
        RED = "\033[31m"
        BLUE = "\033[34m"
        BOLD = "\u001b[1m"
        DEFAULT = "\033[0m"
        STRIKE = "\33[9m"
        

        longest_word = self.get_longest_word()

        row_sep = ""
        for _ in range((longest_word + 3) * self.cols + 1):
            row_sep += "-"
        
        for row in self.board:
            line = "|"
            print(row_sep)
            for col in row:
                extra_space_length = longest_word + 2 - len(col.word)
                before_space = ""
                after_space = ""
                if extra_space_length % 2 == 0:
                    for _ in range(int(extra_space_length/2)):
                        before_space += " "
                        after_space += " "
                else:
                    for _ in range(int((extra_space_length-1)/2)):
                        before_space += " "
                        after_space += " "
                    before_space += " "

                if col.color == "blue":
                    if col.guessed == True:
                        line += before_space + STRIKE + BOLD + BLUE + col.word + DEFAULT + after_space + "|"
                    else:
                        line += before_space + BLUE + col.word + DEFAULT + after_space + "|"
                elif col.color == "red":
                    if col.guessed == True:
                        line += before_space + STRIKE + BOLD + RED + col.word + DEFAULT + after_space + "|"
                    else:
                        line += before_space + RED + col.word + DEFAULT + after_space + "|"

            print(line + DEFAULT) #adding default resets to normal color afterwards for following prints
            line = ""
        print(row_sep)
        print()

    # Returns a tuple of the lenght of the longest word in the board, and the longest row in the board
    def get_longest_word(self):
        longest_word = 0
        for row in self.board:
            current_row = 0
            for card in row:
                current_row += len(card.get_word())
                if len(card.get_word()) > longest_word:
                    longest_word = len(card.get_word())
        return longest_word


    def print_board_plain(self):
        line = ""
        DEFAULT = "\033[0m"
        BOLD = "\u001b[1m"
        RED = "\033[31m"
        BLUE = "\033[34m"
        STRIKE = "\33[9m"

        longest_word = self.get_longest_word()

        row_sep = ""
        for _ in range((longest_word + 3) * self.cols + 1):
            row_sep += "-"

        for row in self.board:
            line = "|"
            print(row_sep)
            for col in row:
                extra_space_length = longest_word + 2 - len(col.word)
                before_space = ""
                after_space = ""
                if extra_space_length % 2 == 0:
                    for _ in range(int(extra_space_length/2)):
                        before_space += " "
                        after_space += " "
                else:
                    for _ in range(int((extra_space_length-1)/2)):
                        before_space += " "
                        after_space += " "
                    before_space += " "
                if col.guessed == True:
                    if col.color == "red":
                        line += before_space + STRIKE + BOLD + RED + col.word + DEFAULT + after_space + "|"
                    else:
                        line += before_space + STRIKE + BOLD + BLUE + col.word + DEFAULT + after_space + "|"
                else:
                    line += before_space + col.word + after_space + "|"

            print(line + DEFAULT)
            line = ""
        print(row_sep)
        print()

class Game():
    playing = False
    turn = "Red"

    def __init__(self, board_cols, board_rows):
        self.board = Board(board_cols, board_rows)
        board_words = self.board.get_random_strings()
        card_list = self.board.create_cards(board_words)
        self.board.init_board(card_list)

        if self.board.num_words % 2 == 0:
            self.red_words_left = self.board.num_words // 2
        else:
            self.red_words_left = (self.board.num_words // 2) + 1
        
        self.blue_words_left = self.board.num_words // 2

    # Returns a number based on what is wrong with the clue
    def check_clue(self, clue):
        if " " in clue:
            return 1
        elif clue.upper() in self.board.valid_words:
            return 2
        else:
            return 0

    def start_game(self):
        #clear terminal
        if os.name == 'nt': #For Windows
            os.system('cls')
        else:  # For macOS and Linux
            os.system('clear')


        print("Welcome to our implementation of Codenames")
        print()
        print("This program was created by Blake Jones, Marc Eidelhoch, Luke Wharton and Sam Zacks")
        print()
        ai_status_str_red = input("Red Team, would you like to play with an AI cluegiver? Enter \"yes\" or \"no\": ")
        while ai_status_str_red != "yes" and ai_status_str_red != "no":
            ai_status_str_red = input("Please enter \"yes\" or \"no\": ")
        
        if ai_status_str_red == "yes":
            ai_status_red = True
        else:
            ai_status_red = False

        ai_status_str_blue = input("Blue Team, would you like to play with an AI cluegiver? Enter \"yes\" or \"no\": ")
        while ai_status_str_blue != "yes" and ai_status_str_blue != "no":
            ai_status_str_blue = input("Please enter \"yes\" or \"no\": ")
        
        if ai_status_str_blue == "yes":
            ai_status_blue = True
        else:
            ai_status_blue = False

        print("Red Team will go first:")
        print()


        self.playing = True

        red_given_clues = []
        blue_given_clues = []

        ready = ""
        clue = ""
        while self.playing:
            if self.turn == "Red":
                if ai_status_red:
                    clue_obj = get_clue(split_board(self.board, self.turn.lower()), red_given_clues)
                    clue = clue_obj[1][0]
                    prompted_words = clue_obj[0]
                else: 
                    #cluegiver stage
                    ready = input(self.turn + " Team, is you cluegiver ready to see the board? Enter \"yes\" when ready: ")
                    print()

                    while ready.lower() != "yes":
                        ready = input("When ready, please enter yes: ") 
                        print()

                    #clear terminal
                    if os.name == 'nt': #For Windows
                        os.system('cls')
                    else:  # For macOS and Linux
                        os.system('clear')
                    self.board.print_board_color()
                    clue = input(self.turn + " Team please enter your clue: ")
                    print()
                    
                    while self.check_clue(clue) != 0:
                        clue_status = self.check_clue(clue)
                        if clue_status == 1:
                            clue = input(self.turn + " Team, please ensure that your clue is one word: ")
                            print()
                        elif clue_status == 2:
                            clue = input(self.turn + " Team, please ensure that your clue is not a word on the board: ")
                            print()
                red_given_clues.append(clue)
            else:
                if ai_status_blue:
                    clue_obj = get_clue(split_board(self.board, self.turn.lower()), blue_given_clues)
                    clue = clue_obj[1][0]
                    prompted_words = clue_obj[0]
                else: 
                    #cluegiver stage
                    ready = input(self.turn + " Team, is you cluegiver ready to see the board? Enter \"yes\" when ready: ")
                    print()

                    while ready.lower() != "yes":
                        ready = input("When ready, please enter yes: ") 
                        print()

                    #clear terminal
                    if os.name == 'nt': #For Windows
                        os.system('cls')
                    else:  # For macOS and Linux
                        os.system('clear')
                    self.board.print_board_color()
                    clue = input(self.turn + " Team please enter your clue: ")
                    print()
                    
                    while self.check_clue(clue) != 0:
                        clue_status = self.check_clue(clue)
                        if clue_status == 1:
                            clue = input(self.turn + " Team, please ensure that your clue is one word: ")
                            print()
                        elif clue_status == 2:
                            clue = input(self.turn + " Team, please ensure that your clue is not a word on the board: ")
                            print()
                blue_given_clues.append(clue)

            #clear terminal
            if os.name == 'nt': #For Windows
                os.system('cls')
            else:  # For macOS and Linux
                os.system('clear')

            #guesser stage
            turn_complete = False
            num_guesses = 0
            while not turn_complete:
                #clear terminal
                if os.name == 'nt': #For Windows
                    os.system('cls')
                else:  # For macOS and Linux
                    os.system('clear')

                self.board.print_board_plain()
                print("The clue your teammate gave is \"" + clue + "\"\n")

                guess = input(self.turn + " Team's Guesser, what word would you like to guess: ").upper()
                print()
                if guess not in self.board.valid_words:
                    while guess not in self.board.valid_words:
                        guess = input(self.turn + " Team's Guesser, please enter a word on the board: ").upper()
                        print()
                    
                num_guesses += 1
                guess_location = self.board.card_locations[guess]
                guessed_card = self.board.board[guess_location[0]][guess_location[1]]
                guessed_card.guessed = True

                #clear terminal
                if os.name == 'nt': #For Windows
                    os.system('cls')
                else:  # For macOS and Linux
                    os.system('clear')

                if guessed_card.color == "red":
                    self.red_words_left -= 1
                    self.board.print_board_plain()
                    if self.turn == "Blue" and self.red_words_left != 0:
                        print("You guessed the other team's word. Your turn is now over. \n")
                        print("The clue was prompting for: ", prompted_words)
                        turn_complete = True
                        self.turn = "Red"
                    else:
                        print("Well done, you guessed correctly!")
                        print()
                else:
                    self.blue_words_left -= 1
                    self.board.print_board_plain()
                    print("You guessed a blue word. \n")
                    if self.turn == "Red" and self.blue_words_left != 0:
                        print("You guessed the other team's word. Your turn is now over. \n")
                        print("The clue was prompting for: ", prompted_words)
                        turn_complete = True
                        self.turn = "Blue"
                    else:
                        print("Well done, you guessed correctly")
                        print()
                
                if self.red_words_left == 0:
                    print("Red Team wins!")
                    turn_complete = True
                    self.playing = False
                elif self.blue_words_left == 0:
                    print("Blue Team wins!")
                    turn_complete = True
                    self.playing = False
                else:
                    if num_guesses < 2 and turn_complete == False:
                        guess_again = input(self.turn + " Team, would you like to guess another word? (Enter \"yes\" if so, \"no\" if not): ")
                        print()

                        while guess_again != "no" and guess_again != "yes":
                            guess_again = input(self.turn + " Team, would you like to guess another word? (Enter \"yes\" if so, \"no\" if not): ")
                            print()
                    
                        if guess_again.lower() == "yes":
                            turn_complete = False

                        else:
                            turn_complete = True
                            if self.turn == "Red":
                                self.turn = "Blue"
                            else:
                                self.turn = "Red"
                    else:
                        if turn_complete == False:
                            print(self.turn + " Team, you have now guessed twice. Your turn is over. \n")
                            print("The clue was prompting for: ", prompted_words)
                            turn_complete = True

                            if self.turn == "Red":
                                self.turn = "Blue"
                            else:
                                self.turn = "Red"

def main():
    game = Game(5,4)
    game.start_game()

if __name__ == "__main__":
    main()
