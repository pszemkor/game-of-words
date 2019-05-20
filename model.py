import csv
import string
# import io
# import shutil
import controller_events as events
from enum import Enum
import config
import controller
from validator import Validator
from lexpy.dawg import DAWG
from collections import Counter


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
        #
        # event_to_send = events.BoardBuildEvent(self)
        # self.ev_manager.post(event_to_send)

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

    def fix_all(self):
        for i in range(config.BOARD_SIZE):
            for j in range(config.BOARD_SIZE):
                if self.fields[i][j].state == FieldState.TEMPORARY:
                    self.fields[i][j].state = FieldState.FIXED


# TO DO -> CHECK WHETHER EVERYTHING IS IN PROGRAM MEMORY EVERY TIME (101 358 words is probably enough to play XD)
class Dictionary:
    def __init__(self):
        possible_words_set = set()
        for c in string.ascii_uppercase:
            file = "words/" + c + "word.csv"
            with open(file, 'r', encoding='ISO-8859-1', newline='') as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    possible_words_set.add(row[0].strip())
        # print(self.possible_words)
        self.possible_words = DAWG().add_all(list(possible_words_set).sort())
        print(len(possible_words_set))

    def prefix_exists(self, prefix):
        return True if self.possible_words.search_with_prefix(prefix) is not [] else False


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
        limit = amount if left > amount else left
        new_letters = []
        for i in range(limit):
            new_letters.append(self.__get_random_letter())
        return new_letters


# game has 2 players, board, possible_words  and validator
class Game:
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register(self)
        self.main_player = None
        self.board = Board(self.ev_manager)
        self.players = []
        self.active_player = None
        self.dictionary = Dictionary()
        self.bags_of_letters = BagOfLetters()
        self.turn = None
        self.validator = Validator(ev_manager, self.dictionary.possible_words)
        # ev = events.DrawGameButtonsEvent()
        # self.ev_manager.post(ev)

    def __str__(self):
        return self.board.__str__()

    def get_index_of_active_player(self):
        for i, p in enumerate(self.players):
            if p == self.active_player:
                return i

    def index_of_next_player(self):
        return (self.get_index_of_active_player() + 1) % len(self.players)

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
                if field.state is not FieldState.FIXED:
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
                if field.state is not FieldState.FIXED:
                    self.active_player.tilebox.set_active_field(field)
            ev = events.UpdateFieldEvent(field)
            self.ev_manager.post(ev)
        elif isinstance(event, events.ConfirmButtonPressedEvent):
            print('Clicked that MAGIC BUTTON!!!')
            # validation
            try:
                self.active_player.score += self.validator.verify_board(self.board)
                print(self.active_player.score)
            except Exception as e:
                print(str(e))
                self.ev_manager.post(events.MoveRejectedEvent())
                return
            # todo -> AI move

            self.set_active_player(self.players[self.index_of_next_player()])
            self.board.fix_all()
            self.ev_manager.post(events.NextPlayerMoveStartedEvent(self))

        elif isinstance(event, events.NextPlayerMoveStartedEvent):
            self.board = event.game.board
            self.players = event.game.players
            self.active_player = event.game.active_player

            if event.game.active_player == self.main_player:
                try:
                    self.active_player.refill_tilebox()
                    print("refiled")
                except Exception as e:
                    # todo end game
                    print(str(e))
                    pass

                self.ev_manager.post(events.DrawGameButtonsEvent())
                self.ev_manager.post(events.BoardBuildEvent(self.board))
                self.ev_manager.post(events.TileBoxBuildEvent(self.active_player.tilebox))
                # todo -> scoreboard build event

            else:
                # todo -> turn information
                self.ev_manager.post(events.OtherPlayerTurnEvent(self.active_player))
                if isinstance(self.active_player, AIPlayer):
                    self.active_player.refill_tilebox()
                    self.active_player.make_turn()
                    self.board.fix_all()
                    self.set_active_player(self.players[self.index_of_next_player()])
                    self.ev_manager.post(events.NextPlayerMoveStartedEvent(self))
                pass

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
    def __init__(self, game):
        self.score = 0
        self.tilebox = TileBox()
        self.pass_strike = 0
        self.name = "Default"
        self.game = game

    def refill_tilebox(self):

        bag_of_letter = self.game.bags_of_letters
        wanted_letter_amount = self.get_empty_fields_count()
        new_tiles = bag_of_letter.get_new_letters(wanted_letter_amount)
        if len(new_tiles) == 0 and wanted_letter_amount == config.TILEBOX_SIZE:
            raise Exception("END OF GAME")

        j = 0
        for i, field in enumerate(self.tilebox.fields):
            if field.state == FieldState.EMPTY:
                if len(new_tiles) - j <= 0:
                    return
                # field.tile = Tile(new_tiles[i])
                self.tilebox.fields[i].tile = Tile(new_tiles[j])
                self.tilebox.fields[i].state = FieldState.TEMPORARY
                j += 1

    def get_empty_fields_count(self):
        count = 0
        for field in self.tilebox.fields:
            if field.state == FieldState.EMPTY:
                count += 1
        return count

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def pass_turn(self):
        pass


class PlacementType(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class AIWord:
    def __init__(self, word, score, placement_type, pos_letter_dict):
        self.word = word
        self.score = score
        self.placement_type = placement_type
        self.pos_letter_dict = pos_letter_dict


class AIPlayer(Player):
    def __init__(self, game):
        super().__init__(game)
        # cells at the edges have empty cross checks (thus config.BOARD_SIZE + 1, not only config.BOARD_SIZE)
        self.cross_checks_board = [[{} for i in range(config.BOARD_SIZE + 1)] for j in range(config.BOARD_SIZE + 1)]
        self.tilebox_list = None

    def make_turn(self):
        import time
        time.sleep(5)
        all_possible_words = self.get_all_possible_words()
        if all_possible_words is not []:
            pass
        else:
            pass

    #         todo -> POST PASS

    def get_all_possible_words(self):

        pass

    def __can_be_anchor(self, coords):
        (x, y) = coords
        if self.game.board.fields[x][y].FieldState == FieldState.FIXED:
            return False
        x_dirs = [1, 0, -1, 0]
        y_dirs = [0, 1, 0, -1]
        for i in range(len(x_dirs)):
            x_neigh = x + x_dirs[i]
            y_neigh = y + y_dirs[i]
            if config.BOARD_SIZE > x_neigh >= 0 and config.BOARD_SIZE > y_neigh >= 0 and \
                    self.game.board.fields[x_neigh][y_neigh].FieldState == FieldState.FIXED:
                return True
            else:
                return False

    def __get_anchors(self):
        anchors = []
        for i in range(config.BOARD_SIZE):
            for j in range(config.BOARD_SIZE):
                if self.__can_be_anchor((i, j)):
                    anchors.append((i, j))

    def __left_part(self, partial_word, limit, anchor_coords, placement_type):
        self.__extend_right_part(partial_word, anchor_coords, anchor_coords, placement_type)
        if limit > 0:
            for i, l in enumerate(self.tilebox_list()):
                if self.game.dictionary.prefix_exists(partial_word + l):
                    del self.tilebox_list[i]
                    self.__left_part(partial_word + l, limit - 1, anchor_coords, placement_type)
                    self.tilebox_list.insert(i, l)

    def __extend_right_part(self, partial_word, field_coords, anchor_coords, placement_type):
        if self.game.board.fields[field_coords].state == FieldState.EMPTY \
                or (placement_type == PlacementType.HORIZONTAL and field_coords[1] == config.BOARD_SIZE) \
                or (placement_type == PlacementType.VERTICAL and field_coords[0] == config.BOARD_SIZE):
            if partial_word in self.game.dictionary.possible_words and field_coords is not anchor_coords:
                self.legal_move(partial_word, field_coords, placement_type)
            for i, e in enumerate(self.tilebox_list):
                if e in self.cross_checks_board[field_coords]:
                    del self.tilebox_list[i]
                    next_field_coords = (
                    field_coords[0], field_coords[1] + 1) if placement_type == PlacementType.HORIZONTAL else (
                    field_coords[0] + 1, field_coords[1])
                    self.__extend_right_part(partial_word + e, next_field_coords, anchor_coords, placement_type)
                    self.tilebox_list.insert(i, e)

    def legal_move(self, word, field_coords, placement_type):
        pass


    def place_tiles(self, ai_word):
        self.score += ai_word.score
        for k, v in ai_word.pos_letter_dict.items():
            self.game.board.fields[k].place_tile(Tile(k))
            self.game.board.fields[k].confirm_tile()

