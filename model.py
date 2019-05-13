import csv
import string
import io
import shutil
from enum import Enum

import config
import controller


# todo -> ogarnac tileboxy
# todo -> algo do "AI"
# todo -> poprawić dostępne litery na angielski
# todo -> ogarnąć eventy
# todo -> dodać rundy - w każdej rundzie wywoływane jest wyświetlenie ustawień (punktacja, tilebox)
# todo    dla każdego z graczy, na razie nie ma rund


class Validator:

    def __init__(self, ev_manager, dictionary):
        self.event_manager = ev_manager
        self.dictionary = dictionary

    def check_word(self, word):
        return True if word in self.dictionary else False

    def check_if_one_line(self, board, first_coords, current_coords):
        (x, y) = first_coords
        (a, b) = current_coords
        if x != a and y != b:
            raise Exception("Tiles are not in one line!")

    def get_behind_temp_horizontal(self, board, y):
        letters_behind = ""
        for i in range(y - 1, -1, -1):
            if board.fields[i][y].state == FieldState.EMPTY:
                return letters_behind
            else:
                letters_behind += board.fields[i][y].tile.character

        return letters_behind[::-1]

    def get_behind_temp_vertical(self, board, x):
        letters_behind = ""
        for i in range(x - 1, -1, -1):
            if board.fields[x][i].state == FieldState.EMPTY:
                return letters_behind
            else:
                letters_behind += board.fields[x][i].tile.character

        return letters_behind[::-1]

    def get_after_temp_horizontal(self, board, y):
        letters_after = ""
        for i in range(y, config.BOARD_SIZE, 1):
            if board.fields[i][y].state == FieldState.EMPTY:
                return letters_after
            else:
                letters_after += board.fields[i][y]
        return letters_after

    def get_after_temp_vertical(self, board, x):
        letters_after = ""
        for i in range(x, config.BOARD_SIZE, 1):
            if board.fields[x][i].state == FieldState.EMPTY:
                return letters_after
            else:
                letters_after += board.fields[x][i]
        return letters_after

    # method return length of new word (just for a while)
    def verify_board(self, board):

        first_temp = False
        first_temp_coord = (-1, -1)
        temps = []

        # getting temporary tiles coordinates
        for i in range(config.BOARD_SIZE):
            for j in range(config.BOARD_SIZE):
                if board.fields[i][j].state == FieldState.TEMPORARY:
                    if first_temp:
                        self.check_if_one_line(board, first_temp_coord, (i, j))
                    temps.append((i, j))

        horizontal_sorted = sorted(temps, key=lambda x: x[1])
        vertical_sorted = None
        if len(horizontal_sorted) > 1 and horizontal_sorted[0][1] == horizontal_sorted[1][1]:
            vertical_sorted = sorted(temps, key=lambda x: x[0])

        word_to_check = ""
        if vertical_sorted is None:
            x = horizontal_sorted[0][0]
            word_to_check += self.get_behind_temp_horizontal(board, horizontal_sorted[0][1])
            for y in range(horizontal_sorted[0][1], horizontal_sorted[len(horizontal_sorted) - 1][1]):
                if board.fields[x][y].state == FieldState.EMPTY:
                    raise Exception("Tiles not in one word")
                word_to_check += board.fields[x][y].tile.character
            word_to_check += self.get_after_temp_horizontal(board, horizontal_sorted[0][1])
        else:
            y = vertical_sorted[0][1]
            word_to_check += self.get_behind_temp_vertical(board, vertical_sorted[0][0])
            for x in range(vertical_sorted[0][0], vertical_sorted[len(vertical_sorted) - 1][0]):
                if board.fields[x][y].state == FieldState.EMPTY:
                    raise Exception("Tiles not in one word")
                word_to_check += board.fields[x][y].tile.character
            word_to_check += self.get_after_temp_vertical(board, vertical_sorted[0][0])
        if self.check_word(word_to_check):
            return len(word_to_check)

    def notify(self, board):
        return self.verify_board(board)


class Board:
    def __init__(self, ev_manager):
        # board with zeros
        self.fields = [[Field(0) for i in range(config.BOARD_SIZE)] for j in range(config.BOARD_SIZE)]
        self.ev_manager = ev_manager
        self.ev_manager.register(self)
        self.active_field = None

        event_to_send = controller.BoardBuildEvent(self)
        self.ev_manager.post(event_to_send)

    def __str__(self):
        string = ""
        for row in self.fields:
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

    def notify(self, event):
        pass

    def set_active_field(self, field):
        if field is None:
            if self.active_field is not None:
                self.active_field.is_active = False
        else:
            if self.active_field is not None:
                self.active_field.is_active = False
            field.is_active = True
            self.active_field = field

    def get_field_from_coords(self, coords):
        return self.fields[coords[1]][coords[0]]


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
        self.available_letters = {'a': 9, "e": 12, "i": 8, "n": 6, "o": 8, "r": 6, "s": 4, "w": 2, "z": 1, "c": 2,
                                  "d": 4, "k": 1, "l": 4, "m": 2, "p": 2, "t": 6, "y": 2, "b": 2, "g": 3, "h": 2,
                                  "j": 1, "u": 4, "f": 2, "q": 1, "x": 1, "v": 2, "?": 2}

    # game has 2 players, board, possible_words  and validator


class Game:
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register(self)

        self.board = Board(self.ev_manager)
        self.players = []
        self.dictionary = Dictionary()
        self.bags_of_letters = BagOfLetters()
        self.turn = None

    def __str__(self):
        return self.board.__str__()

    def init_player_boxes(self):
        pass

    def notify(self, event):
        if isinstance(event, controller.SelectBoardFieldEvent):
            self.board.set_active_field(self.board.get_field_from_coords(event.coords))
            ev = controller.BoardBuildEvent(self.board)
            self.ev_manager.post(ev)

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
        self.is_active = False

    def __str__(self):
        # if there is no tile on a field:
        if self.state is FieldState.EMPTY:
            return "$"
        else:
            return self.tile.__str__()

    def place_tile(self, tile):
        self.tile = tile
        self.state = FieldState.TEMPORARY
        pass

    def confirm_tile(self):
        self.state = FieldState.FIXED


class Tile:
    def __init__(self, character):
        self.character = character

    def __str__(self):
        return self.character

    def get_value(self):
        # TO DO -> handle '?' tiles
        if self.character in "eaionrtlsu":
            return 1
        elif self.character in "dg":
            return 2
        elif self.character in "bcmp":
            return 3
        elif self.character in "fhvwy":
            return 4
        elif self.character in "k":
            return 5
        elif self.character in "jx":
            return 8
        elif self.character in "qz":
            return 10
        else:
            return -1


class TileBox:
    def __init__(self):
        self.fields = [Field(0) for i in range(config.TILEBOX_SIZE)]
        self.active_field = None

    def set_active_field(self, field):
        if field is None:
            if self.active_field is not None:
                self.active_field.is_active = False
        else:
            self.active_field.is_active = False
            field.is_active = True
            self.active_field = field


class Player:
    def __init__(self):
        self.score = 0
        self.tilebox = TileBox()


class AIPlayer(Player):
    def __init__(self):
        super().__init__()

    def make_turn(self):
        pass
