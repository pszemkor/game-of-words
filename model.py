import csv
import string
# import io
# import shutil
import controller_events as events
from enum import Enum
import config
import controller
from validator import Validator


# todo -> algo do "AI"
# todo ->

# introduced because Board and Tilebox share some methods
class FieldsContainer:
    def __init__(self):
        self.active_field = None

    def set_active_field(self, field):
        if field is None:
            if self.active_field is not None:
                self.active_field.is_active = False
        else:
            if self.active_field is not None:
                self.active_field.is_active = False
            field.is_active = True
            self.active_field = field


class Board(FieldsContainer):
    def __init__(self, ev_manager):
        # board with zeros
        super().__init__()
        self.fields = [[Field(1) for i in range(config.BOARD_SIZE)] for j in range(config.BOARD_SIZE)]
        self.ev_manager = ev_manager
        self.ev_manager.register(self)

        event_to_send = events.BoardBuildEvent(self)
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

    def __letters_left(self):
        return sum(self.available_letters.values())

    def __get_random_letter(self):
        import random
        keys = list(map(lambda tuple: tuple[0], filter(lambda item: item[1] != 0, self.available_letters.items())))
        index = random.randint(0, len(keys) - 1)
        self.available_letters[keys[index]] -= 1
        return keys[index]

    def get_new_letters(self, amount):
        left = self.__letters_left()
        upper_limit = amount if left > amount else left
        new_letters = []
        for i in range(upper_limit):
            new_letters.append(self.__get_random_letter())
        return new_letters


# game has 2 players, board, possible_words  and validator
class Game:
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register(self)

        self.board = Board(self.ev_manager)
        self.players = []
        self.active_player = None
        self.dictionary = Dictionary()
        self.bags_of_letters = BagOfLetters()
        self.turn = None
        self.validator = Validator(ev_manager, self.dictionary.possible_words)
        ev = events.DrawGameButtonsEvent()
        self.ev_manager.post(ev)

    def __str__(self):
        return self.board.__str__()

    def init_player_boxes(self):
        pass

    def notify(self, event):
        # handle board active field selection
        if isinstance(event, events.SelectFieldEvent) and event.field_group == FieldGroup.BOARD:
            field = event.field
            if field.is_active:
                self.board.set_active_field(None)
                # tilebox has active field -> will swap tiles
                if self.active_player.tilebox.active_field is not None:
                    self.active_player.tilebox.active_field.tile, field.tile = field.tile, self.active_player.tilebox.active_field.tile
                    self.active_player.tilebox.active_field.state, field.state = field.state, self.active_player.tilebox.active_field.state
                    self.active_player.tilebox.set_active_field(None)
                    self.board.set_active_field(None)
                # todo VALIDATION - tiles have just been swapped!!
            else:
                self.board.set_active_field(field)
            ev = events.UpdateFieldEvent(field)
            self.ev_manager.post(ev)
        # handle tilebox active field selection
        elif isinstance(event, events.SelectFieldEvent) and event.field_group == FieldGroup.TILEBOX:
            field = event.field
            if field.is_active:
                self.active_player.tilebox.set_active_field(None)
                # tilebox has active field -> will swap tiles
                if self.board.active_field is not None:
                    self.board.active_field.tile, field.tile = field.tile, self.board.active_field.tile
                    self.board.active_field.state, field.state = field.state, self.board.active_field.state
                    self.active_player.tilebox.set_active_field(None)
                    self.board.set_active_field(None)
                # todo VALIDATION - tiles have just been swapped!!
            else:
                self.active_player.tilebox.set_active_field(field)
            ev = events.UpdateFieldEvent(field)
            self.ev_manager.post(ev)
        elif isinstance(event, events.ConfirmButtonPressedEvent):
            print('Clicked that MAGIC BUTTON!!!')
            # validation
            try:
                self.active_player.score += self.validator.verify_board(self.board)
            except Exception as e:
                print(str(e))
                self.ev_manager.post(events.MoveRejectedEvent())
                return
            # ai move
            self.ev_manager.post(events.AIPlayerMoveStartedEvent())
            # todo -> AI move
            import time
            time.sleep(3)
            self.ev_manager.post(events.AIPlayerMoveEndedEvent())

            # getting letters from bag-of-letters:
            # todo -> keep track of used letters ???

    def set_active_player(self, player):
        if player in self.players:
            self.active_player = player
        else:
            raise Exception("Chosen player is not in game!")


class FieldGroup(Enum):
    BOARD = 0
    TILEBOX = 1


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
        self.character = self.character.lower()

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


class TileBox(FieldsContainer):
    def __init__(self):
        super().__init__()
        self.fields = [Field(0) for i in range(config.TILEBOX_SIZE)]

    def get_field_from_coords(self, coords):
        return self.fields[coords[0]]


class Player:
    def __init__(self):
        self.score = 0
        self.tilebox = TileBox()
        self.pass_strike = 0


class AIPlayer(Player):
    def __init__(self):
        super().__init__()

    def make_turn(self):
        pass
