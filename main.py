import model
import view
import controller
import controller_events as events
import config


# IMPORTANT - pygame.event.get() deletes read events, so be careful with the order of Controllers in event manager

def main():
    ev_manager = controller.EventManager()
    game_view = view.GameView(ev_manager)
    game = model.Game(ev_manager)

    mouse_controller = controller.MouseController(ev_manager, game_view, game)
    cpu_spinner = controller.CPUSpinnerController(ev_manager)

    human_player = model.Player(game)
    human_player.set_name("Human")

    game.players.append(human_player)
    game.set_active_player(human_player)

    cpu_player = model.AIPlayer(game)
    cpu_player.set_name("AI Player")
    game.players.append(cpu_player)
    game.main_player = game.players[0]
    ev_manager.post(events.NextPlayerMoveStartedEvent(game))

    # init_letters_player = game.bags_of_letters.get_new_letters(config.TILEBOX_SIZE)
    # i = 0
    # for l in init_letters_player:
    #     game.players[0].tilebox.fields[i].place_tile(model.Tile(l))
    #     i += 1
    #
    # i = 0
    # init_letters_cpu = game.bags_of_letters.get_new_letters(config.TILEBOX_SIZE)
    # for l in init_letters_player:
    #     game.players[1].tilebox.fields[i].place_tile(model.Tile(l))
    #     i += 1

    # print(game.players)
    # game.players[0].tilebox.fields[0].place_tile(model.Tile('A'))
    # game.players[0].tilebox.fields[1].place_tile(model.Tile('E'))
    # game.players[0].tilebox.fields[2].place_tile(model.Tile('C'))
    # game.players[0].tilebox.fields[3].place_tile(model.Tile('S'))
    # game.players[0].tilebox.fields[4].place_tile(model.Tile('E'))

    # ev_manager.post(events.TileBoxBuildEvent(game.players[0].tilebox))
    cpu_spinner.run()


if __name__ == "__main__":
    main()
    # print(game.__str__())
