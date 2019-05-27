import model
import config


class ScoreCounter:
    def __init__(self, board, newly_added=None, tiles_with_fixed_neighbours=None):
        self.board = board
        self.newly_added = newly_added
        self.tiles_with_fixed_neighbours = tiles_with_fixed_neighbours

    def __count_word_bonus(self, pos):
        factor = 1
        if self.board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_2W:
            factor = 2
        elif self.board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_3W:
            factor = 3
        return factor

    def __count_letter_bonus(self, pos):
        letter_factor = 1
        if self.board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_2L:
            letter_factor = 2
        elif self.board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_3L:
            letter_factor = 3
        return letter_factor

    def __get_newly_added(self):
        newly = []
        for i in range(config.BOARD_SIZE):
            for j in range(config.BOARD_SIZE):
                if self.board.fields[i][j].state == model.FieldState.TEMPORARY:
                    newly.append((i, j))
        return newly

    def __check_fixed_neighbour(self, pos, board):
        x_dirs = [1, 0, -1, 0]
        y_dirs = [0, 1, 0, -1]
        for i in range(len(x_dirs)):
            x_neigh = pos[0] + x_dirs[i]
            y_neigh = pos[1] + y_dirs[i]
            if 0 <= x_neigh < config.BOARD_SIZE and 0 <= y_neigh < config.BOARD_SIZE:
                if board.fields[x_neigh][y_neigh].state == model.FieldState.FIXED:
                    return True
        return False

    def __get_tiles_with_fixed_neighbours(self):
        tiles_with_fixed_neighbour = []
        for pos in self.newly_added:
            if self.__check_fixed_neighbour(pos, self.board):
                tiles_with_fixed_neighbour.append(pos)
        return tiles_with_fixed_neighbour

    def __check_whether_has_vertical_neighbours(self, pos):
        if pos[0] + 1 < config.BOARD_SIZE and self.board.fields[pos[0] + 1][pos[1]].state == model.FieldState.FIXED:
            return True
        if pos[0] - 1 >= 0 and self.board.fields[pos[0] - 1][pos[1]].state == model.FieldState.FIXED:
            return True
        return False

    def __check_whether_has_horizontal_neighbours(self, pos):
        if pos[1] + 1 < config.BOARD_SIZE and self.board.fields[pos[0]][pos[1] + 1].state == model.FieldState.FIXED:
            return True
        if pos[1] - 1 >= 0 and self.board.fields[pos[0]][pos[1] - 1].state == model.FieldState.FIXED:
            return True
        return False

    def horizontal_word_score(self, pos):
        score = 0
        if pos[1] + 1 < config.BOARD_SIZE and self.board.fields[pos[0]][pos[1] + 1].state == model.FieldState.FIXED:
            for y in range(pos[1] + 1, config.BOARD_SIZE):
                if self.board.fields[pos[0]][y].state == model.FieldState.EMPTY:
                    break
                score += self.board.fields[pos[0]][y].tile.get_value()
                print("H coords", pos[0], y)

        if pos[1] - 1 >= 0 and self.board.fields[pos[0]][pos[1] - 1].state == model.FieldState.FIXED:
            for y in range(pos[1] - 1, -1, -1):
                if self.board.fields[pos[0]][y].state == model.FieldState.EMPTY:
                    break
                score += self.board.fields[pos[0]][y].tile.get_value()

        return score

    def vertical_word_score(self, pos):
        score = 0
        if pos[0] + 1 < config.BOARD_SIZE and self.board.fields[pos[0] + 1][pos[1]].state == model.FieldState.FIXED:
            for x in range(pos[0] + 1, config.BOARD_SIZE):
                if self.board.fields[x][pos[1]].state == model.FieldState.EMPTY:
                    break
                score += self.board.fields[x][pos[1]].tile.get_value()
                print("V coords", x, pos[1])

        if pos[0] - 1 >= 0 and self.board.fields[pos[0] - 1][pos[1]].state == model.FieldState.FIXED:
            for x in range(pos[0] - 1, -1, -1):
                if self.board.fields[x][pos[1]].state == model.FieldState.EMPTY:
                    break
                score += self.board.fields[x][pos[1]].tile.get_value()

        return score

    def count_score(self):

        if self.newly_added is None:
            self.newly_added = self.__get_newly_added()
            print(self.newly_added)
            # for ai pass
            if len(self.newly_added) == 0:
                return 0
        if self.tiles_with_fixed_neighbours is None:
            self.tiles_with_fixed_neighbours = self.__get_tiles_with_fixed_neighbours()

        score = 0
        horizontal_sorted = sorted(self.newly_added, key=lambda x: x[1])
        vertical_sorted = sorted(self.newly_added, key=lambda x: x[0])
        if (len(horizontal_sorted) == 1 and self.__check_whether_has_horizontal_neighbours(horizontal_sorted[0])) \
                or (len(horizontal_sorted) > 1  and horizontal_sorted[0][0] == horizontal_sorted[1][0]):
            # horizontal word which consists of newly-added letters (with temporary state)
            word_bonus_factor = 1
            x = horizontal_sorted[0][0]
            for y in range(horizontal_sorted[0][1], -1, -1):
                if self.board.fields[x][y].state == model.FieldState.FIXED:
                    score += self.board.fields[x][y].tile.get_value()
                    print("for ", x, y, " value: ", self.board.fields[x][y].tile.get_value(), " score: ", score)
                elif self.board.fields[x][y].state == model.FieldState.TEMPORARY:
                    score += self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y))
                    print("for ", x, y, " value: ",
                          self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y)), " score: ",
                          score)
                else:
                    break
            if len(self.newly_added) > 1:
                for y in range(horizontal_sorted[0][1] + 1, horizontal_sorted[::-1][0][1]):
                    if self.board.fields[x][y].state == model.FieldState.FIXED:
                        score += self.board.fields[x][y].tile.get_value()
                        print("for ", x, y, " value: ", self.board.fields[x][y].tile.get_value(), " score: ", score)
                    elif self.board.fields[x][y].state == model.FieldState.TEMPORARY:
                        score += self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y))
                        print("for ", x, y, " value: ",
                              self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y)), " score: ",
                              score)
                    else:
                        break
            for y in range(horizontal_sorted[::-1][0][1], config.BOARD_SIZE):
                if self.board.fields[x][y].state == model.FieldState.FIXED:
                    score += self.board.fields[x][y].tile.get_value()
                    print("for ", x, y, " score: ", self.board.fields[x][y].tile.get_value(), score)
                elif self.board.fields[x][y].state == model.FieldState.TEMPORARY:
                    score += self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y))
                    print("for ", x, y, " value: ",
                          self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y)), " score: ",
                          score)
                else:
                    break
            if len(self.newly_added) == 1:
                score -= self.board.fields[x][horizontal_sorted[::-1][0][1]].tile.get_value() * \
                         self.__count_letter_bonus((x, horizontal_sorted[::-1][0][1]))
            print("score after checking in temporary tiles line: ", score)
            for pos in horizontal_sorted:
                word_bonus_factor *= self.__count_word_bonus(pos)
                print("GOT BONUS FOR WORD: ", word_bonus_factor)

            score *= word_bonus_factor
            print("after word bonus: ", score)

            for pos in self.tiles_with_fixed_neighbours:
                if self.__check_whether_has_vertical_neighbours(pos):
                    print("counting extra vertical for letter: ", self.board.fields[pos[0]][pos[1]].tile.character, pos)
                    score += self.vertical_word_score(pos) + self.board.fields[pos[0]][pos[1]].tile.get_value() \
                             * self.__count_letter_bonus(pos)
                    score *= self.__count_word_bonus(pos)
                    print("got: ", self.vertical_word_score(pos))

        else:
            word_bonus_factor = 1
            y = vertical_sorted[0][1]
            for x in range(vertical_sorted[0][0], -1, -1):
                if self.board.fields[x][y].state == model.FieldState.FIXED:
                    print("for ", x, y, " value: ", self.board.fields[x][y].tile.get_value(), " score: ", score)
                    score += self.board.fields[x][y].tile.get_value()
                elif self.board.fields[x][y].state == model.FieldState.TEMPORARY:
                    score += self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y))
                    print("for ", x, y, " value: ",
                          self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y)), " score: ",
                          score)
                else:
                    break
            if len(self.newly_added) > 1:
                for x in range(vertical_sorted[0][0] + 1, vertical_sorted[::-1][0][0]):
                    if self.board.fields[x][y].state == model.FieldState.FIXED:
                        score += self.board.fields[x][y].tile.get_value()
                        print("for ", x, y, " value: ", self.board.fields[x][y].tile.get_value(), " score: ", score)
                    elif self.board.fields[x][y].state == model.FieldState.TEMPORARY:
                        score += self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y))
                        print("for ", x, y, " value: ",
                              self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y)), " score: ",
                              score)
                    else:
                        break
            for x in range(vertical_sorted[::-1][0][0], config.BOARD_SIZE):
                if self.board.fields[x][y].state == model.FieldState.FIXED:
                    score += self.board.fields[x][y].tile.get_value()
                    print("for ", x, y, " value: ", self.board.fields[x][y].tile.get_value(), " score: ", score)
                elif self.board.fields[x][y].state == model.FieldState.TEMPORARY:
                    score += self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y))
                    print("for ", x, y, " value: ",
                          self.board.fields[x][y].tile.get_value() * self.__count_letter_bonus((x, y)), " score: ",
                          score)
                else:
                    break
            if len(self.newly_added) == 1:
                score -= self.board.fields[vertical_sorted[::-1][0][0]][y].tile.get_value() * \
                         self.__count_letter_bonus((vertical_sorted[::-1][0][0], y))
            print("score after checking in temporary tiles line: ", score)
            for pos in vertical_sorted:
                word_bonus_factor *= self.__count_word_bonus(pos)
                print("GOT BONUS FOR WORD: ", word_bonus_factor)
            score *= word_bonus_factor
            print("after word bonus: ", score)

            for pos in self.tiles_with_fixed_neighbours:
                if self.__check_whether_has_horizontal_neighbours(pos):
                    print("counting extra vertical for letter: ", self.board.fields[pos[0]][pos[1]].tile.character, pos)
                    score += self.horizontal_word_score(pos) + self.board.fields[pos[0]][pos[1]].tile.get_value() \
                             * self.__count_letter_bonus(pos)
                    score *= self.__count_word_bonus(pos)
                    print("got: ", self.vertical_word_score(pos), "curr score: ", score)
        return score
