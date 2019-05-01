import csv
import string
import io
import shutil


class Validator:

    def check_word(self, word, dictionary):
        return True if word in dictionary else False

    def verify_board(self, board):
        pass


class Board:

    def __init__(self):
        # board with zeros
        self.board = [[Field() for i in range(15)] for j in range(15)]

    def __str__(self):
        string = ""
        for row in self.board:
            for el in row:
                if el.tile is not None:
                    if el is row[0]:
                        string = string + '|' + el.tile.__str__() + "|"
                    else:
                        string = string + el.tile.__str__() + "|"
                else:
                    if el is row[0]:
                        string = string + '|' + el.__str__() + '|'
                    else:
                        string = string + el.__str__() + '|'

            string += '\n'
        return string


# TO DO -> CHECK WHETHER EVERYTHING IS IN PROGRAM MEMORY EVERY TIME (101 358 words is probably enough to play XD)
class Dictionary:
    def __init__(self):
        self.possible_words = set()
        for c in string.ascii_uppercase:
            file = c + "word.csv"
            with open(file, 'r', encoding='ISO-8859-1', newline='') as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    self.possible_words.add(row[0].strip())
        # print(self.possible_words)
        print(len(self.possible_words))


# game has 2 players, board, possible_words  and validator
class Game:

    def __init__(self):
        self.board = Board()
        self.human_player = Player()
        self.cpu_player = Player()
        self.dictionary = Dictionary()

    def __str__(self):
        return self.board.__str__()


# board consists of Fields, and every field can have some tile or just be empty
class Field:
    def __init__(self):
        self.tile = None

    def __str__(self):
        # if there is no tile on a field:
        if self.tile is None:
            return "$"
        else:
            return self.tile.__str__()


class Tile:
    def __init__(self):
        self.character = '0'

    def __str__(self):
        return self.character


class Player:
    pass


if __name__ == "__main__":
    game = Game()
    print(game.__str__())
