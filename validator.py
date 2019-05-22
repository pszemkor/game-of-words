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

        for i in range(len(horizontal_sorted) - 1):
            if horizontal_sorted[i][0] != horizontal_sorted[i + 1][0]:
                return False

        for i in range(len(vertical_sorted) - 1):
            if vertical_sorted[i][1] != vertical_sorted[i + 1][1]:
                return False

        return True

    def __check_fixed_neighbour(self, pos, board):
        x_dirs = [1, 0, -1, 0]
        y_dirs = [0, 1, 0, -1]
        for i in range(len(x_dirs)):
            x_neigh = pos[0] + x_dirs[i]
            y_neigh = pos[1] + y_dirs[i]

            if board.fields[x_neigh][y_neigh].state == model.FieldState.FIXED:
                return True
        return False

    def __count_bonus(self, pos, board):
        score = 0
        score += board.fields[pos[0]][pos[1]].tile.get_value()
        factor = 1
        if board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_2W:
            factor = 2
        elif board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_3W:
            factor = 3
        elif board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_2L:
            score *= 2
        elif board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_3L:
            score *= 3
        return score, factor

    def __verify_check_cross(self, pos, board):

        score, factor = self.__count_bonus(pos, board)

        # horizontal verification
        if pos[1] - 1 >= 0 and pos[1] + 1 < config.BOARD_SIZE and \
                board.fields[pos[0]][pos[1] + 1].state == model.FieldState.FIXED or \
                board.fields[pos[0]][pos[1] - + 1].state == model.FieldState.FIXED:

            partial_word = ""
            for i in range(pos[0] - 1, -1, -1):
                curr_field = board.fields[pos[0]][i]
                if curr_field.state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    partial_word += curr_field.tile.character
                else:
                    break

            partial_word = partial_word[::-1]

            for i in range(pos[0], config.BOARD_SIZE):
                curr_field = board.fields[pos[0]][i]
                if curr_field.state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    partial_word += curr_field.tile.character
                else:
                    break

            if not self.check_word(partial_word):
                raise Exception("Word associated with pos: ", pos, " does not exist!")

        # vertical verification
        else:
            partial_word = ""
            for i in range(pos[1] - 1, -1, -1):
                curr_field = board.fields[i][pos[1]]
                if curr_field.state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    partial_word += curr_field.tile.character
                else:
                    break

            partial_word = partial_word[::-1]

            for i in range(pos[1], config.BOARD_SIZE):
                curr_field = board.fields[i][pos[1]]
                if curr_field.state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    partial_word += curr_field.tile.character
                else:
                    break

            if not self.check_word(partial_word):
                raise Exception("Word associated with pos: ", pos, " does not exist!")

        return score

    def verify_board_and_get_score(self, board, round):
        newly_added = []
        score = 0
        for row in range(config.BOARD_SIZE):
            col = 0
            for field in board[row]:
                if field.state == model.FieldState.TEMPORARY:
                    newly_added.append((row, col))
                col += 1
        if not self.__check_whether_one_line(newly_added):
            raise Exception("Tiles are not in one line!")

        if round == 0 and (config.BOARD_SIZE // 2, config.BOARD_SIZE // 2) not in newly_added:
            raise Exception("You have to start from the mid!")
        else:
            tiles_with_fixed_neighbour = []
            for pos in newly_added:
                if self.__check_fixed_neighbour(pos, board):
                    tiles_with_fixed_neighbour.append(pos)

            if len(tiles_with_fixed_neighbour) == 0:
                raise Exception("None of tiles has fixed neighbour")

            for pos in tiles_with_fixed_neighbour:
                score += self.__verify_check_cross(pos, board)
