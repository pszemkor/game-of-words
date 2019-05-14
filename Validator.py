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
            print("heeereeeee")
            raise Exception("Tiles are not in one line!")

    def get_behind_temp_horizontal(self, board, y):
        letters_behind = ""
        for i in range(y - 1, -1, -1):
            if board.fields[i][y].state == model.FieldState.EMPTY:
                return letters_behind
            else:
                letters_behind += board.fields[i][y].tile.character

        return letters_behind[::-1]

    def get_behind_temp_vertical(self, board, x):
        letters_behind = ""
        for i in range(x - 1, -1, -1):
            if board.fields[x][i].state == model.FieldState.EMPTY:
                return letters_behind
            else:
                letters_behind += board.fields[x][i].tile.character

        return letters_behind[::-1]

    def get_after_temp_horizontal(self, board, y):
        letters_after = ""
        for i in range(y, config.BOARD_SIZE, 1):
            if board.fields[i][y].state == model.FieldState.EMPTY:
                return letters_after
            else:
                letters_after += board.fields[i][y]
        return letters_after

    def get_after_temp_vertical(self, board, x):
        letters_after = ""
        for i in range(x, config.BOARD_SIZE, 1):
            if board.fields[x][i].state == model.FieldState.EMPTY:
                return letters_after
            else:
                letters_after += board.fields[x][i]
        return letters_after

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

        horizontal_sorted = sorted(temps, key=lambda x: x[1])
        vertical_sorted = None
        if len(horizontal_sorted) > 1 and horizontal_sorted[0][1] == horizontal_sorted[1][1]:
            vertical_sorted = sorted(temps, key=lambda x: x[0])

        word_to_check = ""
        if vertical_sorted is None:
            x = horizontal_sorted[0][0]
            word_to_check += self.get_behind_temp_horizontal(board, horizontal_sorted[0][1])
            for y in range(horizontal_sorted[0][1], horizontal_sorted[len(horizontal_sorted) - 1][1]):
                if board.fields[x][y].state == model.FieldState.EMPTY:
                    raise Exception("Tiles not in one word")
                word_to_check += board.fields[x][y].tile.character
            word_to_check += self.get_after_temp_horizontal(board, horizontal_sorted[0][1])
        else:
            y = vertical_sorted[0][1]
            word_to_check += self.get_behind_temp_vertical(board, vertical_sorted[0][0])
            for x in range(vertical_sorted[0][0], vertical_sorted[len(vertical_sorted) - 1][0]):
                if board.fields[x][y].state == model.FieldState.EMPTY:
                    raise Exception("Tiles not in one word")
                word_to_check += board.fields[x][y].tile.character
            word_to_check += self.get_after_temp_vertical(board, vertical_sorted[0][0])
        if self.check_word(word_to_check):
            return len(word_to_check)

    def notify(self, board):
        return self.verify_board(board)
