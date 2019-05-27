import model
import view
import controller
import controller_events as events
import pygame


def main():
    pygame.mixer.init()
    pygame.mixer.music.\
        load('music/Game of Thrones - Main Theme (Extended) HD.mp3')
    pygame.mixer.music.play(-1)
    ev_manager = controller.EventManager()
    game_view = view.GameView(ev_manager)
    game = model.Game(ev_manager)

    mouse_controller = controller.MouseController(ev_manager, game_view, game)
    mouse_controller.notify(events.TickEvent())
    cpu_spinner = controller.CPUSpinnerController(ev_manager)

    human_player = model.Player(game)
    human_player.set_name("Human")

    game.players.append(human_player)
    game.set_active_player(human_player)

    cpu_player = model.AIPlayer(game)
    cpu_player.set_name("AI Player")
    game.players.append(cpu_player)
    game.main_player = game.players[0]

    ev_manager.post(events.MenuBuildEvent())
    cpu_spinner.run()


if __name__ == "__main__":
    main()
