import model
import config

class ScoreCounter:
    def __init__(self, board, newly_added, tiles_with_fixed_neighbours):
        self.board = board
        self.newly_added = newly_added
        self.tiles_with_fixed_neighbours = tiles_with_fixed_neighbours

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

    def count_score(self):