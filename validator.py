import config
import model


class Validator:
    def __init__(self, ev_manager, dawg):
        self.event_manager = ev_manager
        self.dawg = dawg

    def check_word(self, word):
        return word in self.dawg

    def __check_whether_one_line(self, newly_added):
        horizontal_sorted = sorted(newly_added, key=lambda x: x[1])
        vertical_sorted = sorted(newly_added, key=lambda x: x[0])
        if len(newly_added) > 1:
            if horizontal_sorted[0][0] == horizontal_sorted[1][0]:
                for i in range(len(horizontal_sorted) - 1):
                    if horizontal_sorted[i][0] != horizontal_sorted[i + 1][0]:
                        print("H: ", horizontal_sorted[i][0], horizontal_sorted[i + 1][0])
                        return False
            else:
                for i in range(len(vertical_sorted) - 1):
                    if vertical_sorted[i][1] != vertical_sorted[i + 1][1]:
                        print("V: ", vertical_sorted[i][1], vertical_sorted[i + 1][1])
                        return False

        return True

    def __check_whether_one_word(self, board, newly_added):
        horizontal_sorted = sorted(newly_added, key=lambda x: x[1])
        vertical_sorted = sorted(newly_added, key=lambda x: x[0])
        if horizontal_sorted[0][0] == horizontal_sorted[1][0]:
            for y in range(horizontal_sorted[0][1], horizontal_sorted[::-1][0][1] + 1):
                if board.fields[horizontal_sorted[0][0]][y].state == model.FieldState.EMPTY:
                    raise Exception("Tiles don't belong to one word!")

        else:
            for x in range(vertical_sorted[0][0], vertical_sorted[::-1][0][0] + 1):
                if board.fields[x][vertical_sorted[0][1]].state == model.FieldState.EMPTY:
                    raise Exception("Tiles don't belong to one word!")

    def __check_fixed_neighbour(self, pos, board):
        x_dirs = [1, 0, -1, 0]
        y_dirs = [0, 1, 0, -1]
        for i in range(len(x_dirs)):
            x_neigh = pos[0] + x_dirs[i]
            y_neigh = pos[1] + y_dirs[i]

            if board.fields[x_neigh][y_neigh].state == model.FieldState.FIXED:
                return True
        return False

    def __verify_check_cross(self, pos, board):

        # horizontal verification
        if pos[1] - 1 >= 0 and pos[1] + 1 < config.BOARD_SIZE and \
                board.fields[pos[0]][pos[1] + 1].state == model.FieldState.FIXED or \
                board.fields[pos[0]][pos[1] - + 1].state == model.FieldState.FIXED:

            partial_word = ""
            for i in range(pos[1] - 1, -1, -1):
                curr_field = board.fields[pos[0]][i]
                if curr_field.state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    partial_word += curr_field.tile.character
                else:
                    break

            partial_word = partial_word[::-1]

            for i in range(pos[1], config.BOARD_SIZE):
                curr_field = board.fields[pos[0]][i]
                if curr_field.state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    partial_word += curr_field.tile.character
                else:
                    break

            if not self.check_word(partial_word):
                raise Exception("Word ", partial_word, " associated with pos: ", pos, " does not exist!")
            else:
                print("word ", partial_word, "exists")

        # vertical verification
        else:
            partial_word = ""
            for i in range(pos[0] - 1, -1, -1):
                curr_field = board.fields[i][pos[1]]
                if curr_field.state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    partial_word += curr_field.tile.character
                else:
                    break
            print("vertical verification1: ", partial_word)
            partial_word = partial_word[::-1]

            for i in range(pos[0], config.BOARD_SIZE):
                curr_field = board.fields[i][pos[1]]
                if curr_field.state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    partial_word += curr_field.tile.character
                else:
                    break
            print("vertical verification2: ", partial_word)
            if not self.check_word(partial_word):
                raise Exception("Word ", partial_word, " associated with pos: ", pos, " does not exist!")
            else:
                print("word ", partial_word, "exists")

    def verify_board(self, board, round):
        print("here")
        newly_added = []
        for row in range(config.BOARD_SIZE):
            col = 0
            for field in board.fields[row]:
                if field.state == model.FieldState.TEMPORARY:
                    newly_added.append((row, col))
                col += 1
        if len(newly_added) == 0:
            raise Exception("You have to put tile")
        if not self.__check_whether_one_line(newly_added):
            print(newly_added)
            raise Exception("Tiles are not in one line!")

        tiles_with_fixed_neighbour = []
        for pos in newly_added:
            if self.__check_fixed_neighbour(pos, board):
                tiles_with_fixed_neighbour.append(pos)
        self.__check_whether_one_word(board, newly_added)
        if round == 0:
            if (config.BOARD_SIZE // 2, config.BOARD_SIZE // 2) not in newly_added:
                raise Exception("You have to start from the mid!")
            if len(newly_added) == 1:
                raise Exception("You have to put at least two tiles")

            horizontal_sorted = sorted(newly_added, key=lambda x: x[1])
            vertical_sorted = sorted(newly_added, key=lambda x: x[0])
            word = ""
            if horizontal_sorted[0][0] == horizontal_sorted[1][0]:
                for pos in horizontal_sorted:
                    word += board.fields[pos[0]][pos[1]].tile.character
            else:
                for pos in vertical_sorted:
                    word += board.fields[pos[0]][pos[1]].tile.character
            if not self.check_word(word):
                raise Exception("Word ", word, " does not exists")


        else:
            if len(tiles_with_fixed_neighbour) == 0:
                raise Exception("None of tiles has fixed neighbour")
            for pos in tiles_with_fixed_neighbour:
                self.__verify_check_cross(pos, board)

        return newly_added, tiles_with_fixed_neighbour
