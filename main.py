import model
import view
import controller


# IMPORTANT - pygame.event.get() deletes read events, so be careful with the order of Controllers in event manager

def main():

    ev_manager = controller.EventManager()
    game_view = view.GameView(ev_manager)
    game = model.Game(ev_manager)

    mouse_controller = controller.MouseController(ev_manager)
    cpu_spinner = controller.CPUSpinnerController(ev_manager)

    ##### DEBUG
    game.players.append(model.Player())
    # print(game.players)
    game.players[0].tilebox.fields[1].place_tile(model.Tile('A'))
    ev_manager.post(controller.TileBoxBuildEvent(game.players[0].tilebox))

    #######

    cpu_spinner.run()


if __name__ == "__main__":
    main()
    # print(game.__str__())
