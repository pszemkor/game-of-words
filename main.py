import model
import view
import controller
import controller_events as events


# IMPORTANT - pygame.event.get() deletes read events, so be careful with the order of Controllers in event manager

def main():
    ev_manager = controller.EventManager()
    game_view = view.GameView(ev_manager)
    game = model.Game(ev_manager)

    mouse_controller = controller.MouseController(ev_manager, game_view, game)
    cpu_spinner = controller.CPUSpinnerController(ev_manager)

    ##### DEBUG
    player = model.Player()
    game.players.append(player)
    game.set_active_player(player)
    # print(game.players)s
    game.players[0].tilebox.fields[0].place_tile(model.Tile('A'))
    game.players[0].tilebox.fields[1].place_tile(model.Tile('E'))
    game.players[0].tilebox.fields[2].place_tile(model.Tile('C'))
    game.players[0].tilebox.fields[3].place_tile(model.Tile('S'))
    game.players[0].tilebox.fields[4].place_tile(model.Tile('E'))
    ev_manager.post(events.TileBoxBuildEvent(game.players[0].tilebox))
    #######

    cpu_spinner.run()


if __name__ == "__main__":
    main()
    # print(game.__str__())
