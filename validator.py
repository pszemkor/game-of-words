import model
import config


class Validator:

    def __init__(self, ev_manager, dictionary):
        self.event_manager = ev_manager
        self.dictionary = dictionary

    def check_word(self, word):
        return True if word in self.dictionary else False

    def check_if_one_line(self, first_coords, current_coords):
        (x, y) = first_coords
        (a, b) = current_coords
        if x != a and y != b:
            raise Exception("Tiles are not in one line!")

    def __get_behind_temp_horizontal(self, board, y):
        letters_behind = ""
        score = 0
        for i in range(y - 1, -1, -1):
            if board.fields[i][y].state == model.FieldState.EMPTY:
                return (letters_behind, score)
            else:
                letters_behind += board.fields[i][y].tile.character
            score += board.fields[i][y].tile.get_value()

        return (letters_behind[::-1], score)

    def __get_behind_temp_vertical(self, board, x):
        letters_behind = ""
        score = 0
        for i in range(x - 1, -1, -1):
            if board.fields[x][i].state == model.FieldState.EMPTY:
                return letters_behind, score
            else:
                letters_behind += board.fields[x][i].tile.character
            score += board.fields[x][i].tile.get_value()

        return (letters_behind[::-1], score)

    def __get_after_temp_horizontal(self, board, y):
        letters_after = ""
        score = 0
        for i in range(y, config.BOARD_SIZE, 1):
            if board.fields[i][y].state == model.FieldState.EMPTY:
                return letters_after, score
            else:
                letters_after += board.fields[i][y].tile.character
            score += board.fields[i][y].tile.get_value()
        return (letters_after, score)

    def __get_after_temp_vertical(self, board, x):
        letters_after = ""
        score = 0
        for i in range(x, config.BOARD_SIZE, 1):
            if board.fields[x][i].state == model.FieldState.EMPTY:
                return letters_after, score
            else:
                letters_after += board.fields[x][i].tile.character
            score += board.fields[x][i].tile.get_value()
        return (letters_after, score)

    # method return length of new word (just for a while)
    def verify_board(self, board):

        first_temp = True
        first_temp_coord = (-1, -1)
        temps = []

        # getting temporary tiles coordinates
        for i in range(config.BOARD_SIZE):
            for j in range(config.BOARD_SIZE):
                if board.fields[i][j].state == model.FieldState.TEMPORARY:
                    if first_temp:
                        first_temp_coord = (i, j)
                        first_temp = False
                    else:
                        self.check_if_one_line(first_temp_coord, (i, j))
                    temps.append((i, j))

        if len(temps) == 0:
            raise Exception("None tile has been put!")

        horizontal_sorted = sorted(temps, key=lambda x: x[1])
        vertical_sorted = None
        if len(horizontal_sorted) > 1 and horizontal_sorted[0][1] == horizontal_sorted[1][1]:
            vertical_sorted = sorted(temps, key=lambda x: x[0])

        word_to_check = ""
        score = 0
        if vertical_sorted is None:
            x = horizontal_sorted[0][0]

            (word_to_check_behind, score_behind) = self.__get_behind_temp_horizontal(board, horizontal_sorted[0][1])

            for y in range(horizontal_sorted[0][1], horizontal_sorted[len(horizontal_sorted) - 1][1] + 1):
                if board.fields[x][y].state == model.FieldState.EMPTY:
                    raise Exception("Tiles not in one word")
                word_to_check_behind += board.fields[x][y].tile.character
                score_behind += board.fields[x][y].tile.get_value() * \
                                (1 if board.fields[x][y].state == model.FieldState.FIXED else board.fields[x][y].bonus)

            (word_to_check_after, score_after) = self.__get_after_temp_horizontal(board, horizontal_sorted[0][1])
            word_to_check = word_to_check_behind + word_to_check_after
            score = score_behind + score_after

        else:
            y = vertical_sorted[0][1]

            (word_to_check_behind, score_behind) = self.__get_behind_temp_vertical(board, vertical_sorted[0][0])

            for x in range(vertical_sorted[0][0], vertical_sorted[len(vertical_sorted) - 1][0] + 1):
                if board.fields[x][y].state == model.FieldState.EMPTY:
                    raise Exception("Tiles not in one word")
                word_to_check_behind += board.fields[x][y].tile.character
                score_behind += board.fields[x][y].tile.get_value() * \
                                (1 if board.fields[x][y].state == model.FieldState.FIXED else board.fields[x][y].bonus)

            (word_to_check_after, score_after) = self.__get_after_temp_vertical(board, vertical_sorted[0][0])
            word_to_check = word_to_check_behind + word_to_check_after
            score = score_behind + score_after

        word_to_check.lower()
        print(word_to_check)
        if self.check_word(word_to_check.lower()):
            return score
        else:
            raise Exception("Word does not exist!")

    def notify(self, board):
        return self.verify_board(board)
