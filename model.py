import csv
import string
# import io
# import shutil
import controller_events as events
from enum import Enum, IntEnum
import config
import controller
from validator import Validator
# from lexpy.dawg import DAWG
# from lexpy.trie import Trie
from collections import Counter
import itertools
import dawg


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


class Bonus(IntEnum):
    NO_BONUS = 1
    BONUS_2L = 2
    BONUS_3L = 3
    BONUS_3W = 4
    BONUS_2W = 5


class ScoreBoard:
    def __init__(self, players):
        self.shape = config.SCOREBOARD_SHAPE
        self.players = players


class Board(FieldsContainer):
    def __init__(self, ev_manager):
        # board with zeros
        super().__init__()
        self.fields = [[Field(Bonus.NO_BONUS) for i in range(config.BOARD_SIZE)] for j in range(config.BOARD_SIZE)]
        self.ev_manager = ev_manager
        self.ev_manager.register(self)
        #
        # event_to_send = events.BoardBuildEvent(self)
        # self.ev_manager.post(event_to_send)

    # todo -> default file -> board.txt
    def get_board_from_file(self):
        row = 0
        with open("board.txt", "r+") as f:
            lines = f.readlines()
            for line in lines:
                line = line.split(", ")
                line_iter = 0
                for field in self.fields[row]:
                    if line[line_iter].strip() == "2W":
                        field.bonus = Bonus.BONUS_2W
                    elif line[line_iter].strip() == "3W":
                        field.bonus = Bonus.BONUS_3W
                    elif line[line_iter].strip() == "2L":
                        field.bonus = Bonus.BONUS_2L
                    elif line[line_iter].strip() == "3L":
                        field.bonus = Bonus.BONUS_3L

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


class Dictionary:
    def __init__(self):
        possible_words_set = set()
        for c in string.ascii_uppercase:
            file = "words/" + c + "word.csv"
            with open(file, 'r', encoding='UTF-8', newline='') as csvFile:
                reader = csv.reader(csvFile)
                print("Read file", file)
                for row in reader:
                    word = ''.join(x for x in row[0] if x.isalpha())
                    if word == 'oft':
                        print('will add oft to set', word)
                    possible_words_set.add(word)

        possible_words_list = filter(lambda x: len(x) > 1, sorted(list(possible_words_set)))
        self.possible_words = dawg.CompletionDAWG(possible_words_list)

    def prefix_exists(self, prefix):
        return self.possible_words.has_keys_with_prefix(prefix)


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
        self.round_no = -1
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
                if self.active_player.tilebox.active_field is not None and self.active_player.tilebox.active_field is not FieldState.FIXED:
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
                if self.board.active_field is not None and self.board.active_field.state is not FieldState.FIXED:
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
                self.board.fix_all()
            except Exception as e:
                print(str(e))
                self.ev_manager.post(events.MoveRejectedEvent())
                return
            # todo -> AI move

            self.set_active_player(self.players[self.index_of_next_player()])
            self.ev_manager.post(events.NextPlayerMoveStartedEvent(self))


        # todo -> handle buttons
        elif isinstance(event, events.ShuffleButtonPressedEvent):
            fields = self.active_player.tilebox.fields
            tiles = []
            for field in fields:
                if field.state == FieldState.TEMPORARY:
                    tiles.append(field.tile)

            import random
            permutations = list(itertools.permutations(tiles))
            rand_permutation_index = random.randint(0, len(permutations) - 1)
            tiles = permutations[rand_permutation_index]
            i = 0
            for field in self.active_player.tilebox.fields:
                if field.state != FieldState.TEMPORARY:
                    continue
                print(tiles[i])
                field.tile = tiles[i]
                i += 1

            self.ev_manager.post(events.TileBoxBuildEvent(self.active_player.tilebox))

        elif isinstance(event, events.SurrenderButtonPressedEvent):
            pass
        elif isinstance(event, events.FactButtonPressedEvent):
            pass
        elif isinstance(event, events.PassButtonPressedEvent):
            self.active_player.pass_strike += 1
            if self.active_player.pass_strike == 2 and self.players[self.index_of_next_player()].pass_strike == 2:
                # todo post end of game!!!!
                pass
            else:
                if self.round_no > 0:
                    self.set_active_player(self.players[self.index_of_next_player()])
                    self.ev_manager.post(events.NextPlayerMoveStartedEvent(self))
                else:
                    print("CANNOT USE PASS BUTTON DURING FIRST ROUND!")



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
                self.ev_manager.post(events.ScoreBoardBuildEvent(ScoreBoard(self.players)))
                self.round_no += 1
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
        self.cross_checks_board = [[set() for i in range(config.BOARD_SIZE + 1)] for j in range(config.BOARD_SIZE + 1)]
        self.tilebox_list = None
        # position : (word, type[horizontal, vertical])
        self.all_possible_words_dict = {}
        self.score = 0

    def remove_tile(self, word, x, y, index):
        if self.game.board.fields[x][y].state == FieldState.EMPTY:
            for field in self.tilebox.fields:
                if field.state != FieldState.EMPTY and field.tile.character == word[index]:
                    self.score += field.tile.get_value()
                    field.state = FieldState.EMPTY
                    field.tile = None
        pass

    def make_turn(self):
        self.__get_tilebox_list()
        self.get_all_possible_words()
        all_possible_words = self.all_possible_words_dict.items()
        # print("Found such possible words", all_possible_words)
        print("Tilebox of AI player", self.tilebox_list)

        if all_possible_words is not []:
            for el in all_possible_words:
                print('ai found', el)
                (word, placement_type, anchor_coords) = el[1]
                index = 0
                if placement_type == PlacementType.HORIZONTAL:
                    (end_x, end_y) = el[0]
                    i = end_y - len(word)
                    while i < end_y:
                        self.remove_tile(word, end_x, i, index)
                        self.game.board.fields[end_x][i].place_tile(Tile(word[index]))
                        self.game.board.fields[end_x][i].confirm_tile()
                        i += 1
                        index += 1
                else:
                    (end_x, end_y) = el[0]
                    i = end_x - len(word)
                    while i < end_x:
                        self.remove_tile(word, i, end_y, index)
                        self.game.board.fields[i][end_y].place_tile(Tile(word[index]))
                        self.game.board.fields[i][end_y].confirm_tile()
                        i += 1
                        index += 1
                break
        else:
            pass
            # todo -> POST PASS

    def __get_limit_of_left_part(self, field_position, anchors, placement_type):
        current_position = (field_position[0], field_position[1])
        limit = 0
        if placement_type is PlacementType.VERTICAL:
            current_position = (current_position[0] - 1, current_position[1])
            while current_position[0] >= 0 and current_position not in anchors and self.game.board.fields[
                current_position[0]][current_position[1]].state == FieldState.EMPTY:
                current_position = (current_position[0] - 1, current_position[1])
                limit += 1
            else:
                return limit
        else:
            current_position = (current_position[0], current_position[1] - 1)
            while current_position[1] >= 0 and current_position not in anchors and self.game.board.fields[
                current_position[0]][current_position[1]].state == FieldState.EMPTY:
                current_position = (current_position[0], current_position[1] - 1)
                limit += 1
            else:
                return limit

    def get_all_possible_words(self):
        self.all_possible_words_dict = {}
        anchors = self.__get_anchors()

        # print("Anchors horizontal are: ", anchors)
        self.__init_crosschecks(anchors, PlacementType.HORIZONTAL)
        print(self.cross_checks_board)
        for field_coords in anchors:
            # handle horizontal words cases
            limit = self.__get_limit_of_left_part(field_coords, anchors, PlacementType.HORIZONTAL)
            beginning = self.__get_beginning_of_left_part(field_coords, anchors, PlacementType.HORIZONTAL)
            # print("H - For anchor", field_coords, "limit is", limit, "prefix:", beginning)
            self.__left_part(beginning, limit, field_coords, PlacementType.HORIZONTAL)

        # print("Anchors vertical are: ", anchors)
        self.__init_crosschecks(anchors, PlacementType.VERTICAL)
        print(self.cross_checks_board)
        for field_coords in anchors:
            # handle vertical words cases
            limit = self.__get_limit_of_left_part(field_coords, anchors, PlacementType.VERTICAL)
            beginning = self.__get_beginning_of_left_part(field_coords, anchors, PlacementType.VERTICAL)
            # print("V - For anchor", field_coords, "limit is", limit, "prefix:", beginning)
            self.__left_part(beginning, limit, field_coords, PlacementType.VERTICAL)
        pass

    def __get_beginning_of_left_part(self, field_coords, anchors, placement_type):
        beginning = ''
        current_coords = field_coords
        if placement_type is PlacementType.VERTICAL:
            current_coords = (current_coords[0] - 1, current_coords[1])
            while current_coords[0] >= 0 and current_coords not in anchors and self.game.board.fields[
                current_coords[0]][current_coords[1]].state == FieldState.FIXED:
                beginning = self.game.board.fields[current_coords[0]][current_coords[1]].tile.character + beginning
                current_coords = (current_coords[0] - 1, current_coords[1])
            else:
                # print('V - begging is', beginning, 'field coords', field_coords)
                return beginning
        else:
            current_coords = (current_coords[0], current_coords[1] - 1)
            while current_coords[1] >= 0 and current_coords not in anchors and self.game.board.fields[
                current_coords[0]][current_coords[1]].state == FieldState.FIXED:
                beginning = self.game.board.fields[current_coords[0]][current_coords[1]].tile.character + beginning
                current_coords = (current_coords[0], current_coords[1] - 1)
            else:
                # print('H - begging is', beginning, 'field coords', field_coords)
                return beginning

    def __can_be_anchor(self, coords):
        (x, y) = coords
        if self.game.board.fields[x][y].state == FieldState.FIXED:
            return False
        x_dirs = [1, 0, -1, 0]
        y_dirs = [0, 1, 0, -1]
        for i in range(len(x_dirs)):
            x_neigh = x + x_dirs[i]
            y_neigh = y + y_dirs[i]
            if config.BOARD_SIZE > x_neigh >= 0 and config.BOARD_SIZE > y_neigh >= 0 and \
                    self.game.board.fields[x_neigh][y_neigh].state == FieldState.FIXED:
                return True
        return False

    def __get_anchors(self):
        anchors = []
        for i in range(config.BOARD_SIZE):
            for j in range(config.BOARD_SIZE):
                if self.__can_be_anchor((i, j)):
                    anchors.append((i, j))
        return anchors

    def __left_part(self, partial_word, limit, anchor_coords, placement_type):
        self.__extend_right_part(partial_word, anchor_coords, anchor_coords, placement_type)
        if limit > 0:
            for i, l in enumerate(self.tilebox_list):
                # print('will now check partial word', partial_word + l)
                if l != '?':
                    if self.game.dictionary.prefix_exists(partial_word + l):
                        # print('checking word in  partial word left part', partial_word + l, placement_type)
                        del self.tilebox_list[i]
                        self.__left_part(partial_word + l, limit - 1, anchor_coords, placement_type)
                        self.tilebox_list.insert(i, l)
                else:
                    for l_wild in string.ascii_lowercase:
                        if self.game.dictionary.prefix_exists(partial_word + l_wild):
                            # print('checking word in  partial word left part', partial_word + l_wild, placement_type)
                            del self.tilebox_list[i]
                            self.__left_part(partial_word + l_wild, limit - 1, anchor_coords, placement_type)
                            self.tilebox_list.insert(i, l)

    def __extend_right_part(self, partial_word, field_coords, anchor_coords, placement_type):
        if placement_type == PlacementType.HORIZONTAL and field_coords[1] == config.BOARD_SIZE \
                or placement_type == PlacementType.VERTICAL and field_coords[0] == config.BOARD_SIZE \
                or self.game.board.fields[field_coords[0]][field_coords[1]].state == FieldState.EMPTY:

            # print('will check partial word in right part', partial_word, field_coords)
            if partial_word in self.game.dictionary.possible_words and field_coords is not anchor_coords:
                self.legal_move(partial_word, field_coords, placement_type, anchor_coords)
            for i, e in enumerate(self.tilebox_list):
                if e != '?':
                    if e in self.cross_checks_board[field_coords[0]][field_coords[1]]:
                        del self.tilebox_list[i]
                        next_field_coords = (
                            field_coords[0], field_coords[1] + 1) if placement_type == PlacementType.HORIZONTAL else (
                            field_coords[0] + 1, field_coords[1])
                        if self.game.dictionary.prefix_exists(partial_word + e):
                            # print('prefix exists', partial_word + e)
                            self.__extend_right_part(partial_word + e, next_field_coords, anchor_coords, placement_type)
                        self.tilebox_list.insert(i, e)
                else:
                    for e_wild in string.ascii_lowercase:
                        if e_wild in self.cross_checks_board[field_coords[0]][field_coords[1]]:
                            del self.tilebox_list[i]
                            next_field_coords = (
                                field_coords[0],
                                field_coords[1] + 1) if placement_type == PlacementType.HORIZONTAL else (
                                field_coords[0] + 1, field_coords[1])
                            if self.game.dictionary.prefix_exists(partial_word + e_wild):
                                # print('prefix exists', partial_word + e)
                                self.__extend_right_part(partial_word + e_wild, next_field_coords, anchor_coords,
                                                         placement_type)
                            self.tilebox_list.insert(i, e)
        else:
            e = self.game.board.fields[field_coords[0]][field_coords[1]].tile.character
            next_field_coords = (
                field_coords[0], field_coords[1] + 1) if placement_type == PlacementType.HORIZONTAL else (
                field_coords[0] + 1, field_coords[1])
            if self.game.dictionary.prefix_exists(partial_word + e):
                self.__extend_right_part(partial_word + e, next_field_coords, anchor_coords, placement_type)

    def legal_move(self, word, field_coords, placement_type, anchor_coords):
        self.all_possible_words_dict[field_coords] = (word, placement_type, anchor_coords)

    def place_tiles(self, ai_word):
        self.score += ai_word.score
        for k, v in ai_word.pos_letter_dict.items():
            self.game.board.fields[k].place_tile(Tile(k))
            self.game.board.fields[k].confirm_tile()

    def __get_tilebox_list(self):
        self.tilebox_list = []
        for field in self.tilebox.fields:
            if field.state is not FieldState.EMPTY:
                self.tilebox_list.append(field.tile.character)
        print('tilebox of player is', self.tilebox_list)

    def __init_crosschecks(self, anchors, placement_type):
        self.cross_checks_board = [[set() for i in range(config.BOARD_SIZE + 1)] for j in
                                   range(config.BOARD_SIZE + 1)]
        if placement_type is PlacementType.VERTICAL:
            anchor_colums = set()
            for anchor in anchors:
                anchor_colums.add(anchor[1])

            for anchor_column in anchor_colums:
                for i in range(config.BOARD_SIZE):
                    if self.game.board.fields[i][anchor_column].state == FieldState.EMPTY:
                        for l in string.ascii_lowercase:
                            word = self.__get_whole_word_expansion([i, anchor_column], l, PlacementType.VERTICAL)
                            if len(word) == 1:
                                self.cross_checks_board[i][anchor_column].add(l)
                            elif word in self.game.dictionary.possible_words:
                                # if len(word) > 1:
                                # print('V - expanded', [i, anchor_column], 'letter', l, 'word', word)
                                self.cross_checks_board[i][anchor_column].add(l)
        else:
            anchor_rows = set()
            for anchor in anchors:
                anchor_rows.add(anchor[0])

            for anchor_row in anchor_rows:
                for i in range(config.BOARD_SIZE):
                    if self.game.board.fields[anchor_row][i].state == FieldState.EMPTY:
                        for l in string.ascii_lowercase:
                            word = self.__get_whole_word_expansion([anchor_row, i], l, PlacementType.HORIZONTAL)
                            if len(word) == 1:
                                self.cross_checks_board[anchor_row][i].add(l)
                            elif word in self.game.dictionary.possible_words:
                                # if len(word) > 1:
                                # print('H - expanded', [anchor_row, i], 'letter', l, 'word', word)
                                self.cross_checks_board[anchor_row][i].add(l)

    def __get_whole_word_expansion(self, field_coords, letter, placement_type):
        word_expansion = letter
        current_coords = field_coords.copy()
        # VERTICAL - expand words horizontally
        if placement_type is PlacementType.VERTICAL:
            current_coords[1] -= 1
            while current_coords[1] >= 0 and self.game.board.fields[current_coords[0]][
                current_coords[1]].state is FieldState.FIXED:
                word_expansion = self.game.board.fields[current_coords[0]][
                                     current_coords[1]].tile.character + word_expansion
                current_coords[1] -= 1

            current_coords = field_coords.copy()
            current_coords[1] += 1
            while current_coords[1] < config.BOARD_SIZE and self.game.board.fields[current_coords[0]][
                current_coords[1]].state is FieldState.FIXED:
                word_expansion += self.game.board.fields[current_coords[0]][
                    current_coords[1]].tile.character
                current_coords[1] += 1
            return word_expansion
        # HORIZONTAL- expand words vertically
        else:
            current_coords[0] -= 1
            while current_coords[0] >= 0 and self.game.board.fields[current_coords[0]][
                current_coords[1]].state is FieldState.FIXED:
                word_expansion = self.game.board.fields[current_coords[0]][
                                     current_coords[1]].tile.character + word_expansion
                current_coords[0] -= 1

            current_coords = field_coords.copy()
            current_coords[0] += 1
            while current_coords[0] < config.BOARD_SIZE and self.game.board.fields[current_coords[0]][
                current_coords[1]].state is FieldState.FIXED:
                word_expansion += self.game.board.fields[current_coords[0]][
                    current_coords[1]].tile.character
                current_coords[0] += 1
            return word_expansion
