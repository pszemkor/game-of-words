import model
import view
import controller


if __name__ == "__main__":
    game = model.Game()
    # print(game.__str__())

    ev_manager = controller.EventManager()
    game_view = view.GameView(ev_manager, game.board)
