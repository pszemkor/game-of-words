import csv
import string
import io
import shutil
from enum import Enum


# todo -> napisac validator
# todo -> ogarnac tileboxy
# todo -> algo do "AI"
# todo -> poprawić dostępne litery na angielski
# todo -> ogarnąć eventy

class Validator:

    def check_word(self, word, dictionary):
        return True if word in dictionary else False

    def verify_board(self, board):
        pass


class Board:
    def __init__(self):
        # board with zeros
        self.board = [[Field(0) for i in range(15)] for j in range(15)]

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
            file = "words/" + c + "word.csv"
            with open(file, 'r', encoding='ISO-8859-1', newline='') as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    self.possible_words.add(row[0].strip())
        # print(self.possible_words)
        print(len(self.possible_words))


class BagOfLetters:
    def __init__(self):
        # '?' is blank tile
        # count of letters that are still in game
        self.available_letters = {'a': 9, "e": 7, "i": 8, "n": 5, "o": 6, "r": 4, "s": 4, "w": 4, "z": 5, "c": 3,
                                  "d": 3, "k": 3, "l": 3, "m": 3, "p": 3, "t": 3, "y": 4, "b": 3, "g": 2, "h": 2,
                                  "j": 2, "u": 2, "ł": 2, "ą": 5, "ę": 1, "f": 1, "ó": 1, "ś": 1, "ż": 1, "ć": 1,
                                  "ń": 1, "ź": 1, "?": 2}


# game has 2 players, board, possible_words  and validator
class Game:
    def __init__(self):
        self.board = Board()
        self.players = []
        self.dictionary = Dictionary()
        self.bags_of_letters = BagOfLetters()
        self.turn = None

    def __str__(self):
        return self.board.__str__()

    def init_player_boxes(self):
        pass


class FieldState(Enum):
    EMPTY = 0
    TEMPORARY = 1
    FIXED = 2


# board consists of Fields, and every field can have some tile or just be empty
class Field:
    def __init__(self, bonus):
        self.tile = None
        self.state = FieldState.EMPTY
        self.bonus = bonus

    def __str__(self):
        # if there is no tile on a field:
        if self.tile is FieldState.EMPTY:
            return "$"
        else:
            return self.tile.__str__()

    def place_tile(self, tile):
        pass

    def confirm_tile(self):
        self.state = FieldState.FIXED


class Tile:
    def __init__(self):
        self.character = '0'

    def __str__(self):
        return self.character

    def get_value(self):
        # TO DO -> handle '?' tiles
        if self.character in "aeinorswz":
            return 1
        elif self.character in "cdklmpty":
            return 2
        elif self.character in "bghjłu":
            return 3
        elif self.character in "ąęfóśż":
            return 5
        elif self.character in "ć":
            return 6
        elif self.character in "ń":
            return 7
        elif self.character in "ź":
            return 9
        else:
            return -1


class TileBox:
    def __init__(self):
        pass


class Player:
    def __init__(self):
        self.score = 0
        self.owned_tilebox = TileBox()


class AIPlayer(Player):
    def __init__(self):
        super().__init__()

    def make_turn(self):
        pass


if __name__ == "__main__":
    game = Game()
    print(game.__str__())
