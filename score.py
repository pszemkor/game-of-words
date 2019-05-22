import model
import config


class ScoreCounter:
    def __init__(self, board, newly_added, tiles_with_fixed_neighbours):
        self.board = board
        self.newly_added = newly_added
        self.tiles_with_fixed_neighbours = tiles_with_fixed_neighbours

    def __count_bonus(self, pos, board):
        factor = 1
        if board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_2W:
            factor = 2
        elif board.fields[pos[0]][pos[1]].bonus == model.Bonus.BONUS_3W:
            factor = 3
        return factor

    def count_score(self):
        score = 0
        horizontal_sorted = sorted(self.newly_added, key=lambda x: x[1])
        vertical_sorted = sorted(self.newly_added, key=lambda x: x[0])

        if horizontal_sorted[0][0] == horizontal_sorted[1][0]:
            x = horizontal_sorted[0][0]
            for y in range(horizontal_sorted[0][1], -1, -1):
                if self.board.fields[x][y].state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    score += self.board.fields[x][y].tile.get_value()
                else:
                    break
            score -= self.board.fields[x][horizontal_sorted[0][1]].tile.get_value()
            for y in range(horizontal_sorted[0][1], horizontal_sorted[::-1][0][1]):
                if self.board.fields[x][y].state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    score += self.board.fields[x][y].tile.get_value()
                else:
                    break
            score -= self.board.fields[x][horizontal_sorted[::-1][0][1]].tile.get_value()
            for y in range(horizontal_sorted[::-1][0][1], config.BOARD_SIZE):
                if self.board.fields[x][y].state in [model.FieldState.FIXED, model.FieldState.TEMPORARY]:
                    score += self.board.fields[x][y].tile.get_value()
                else:
                    break

            # todo -> count vertical score for every member of tiles_with_fixed_neighbours

        else:
            pass
