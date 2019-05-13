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

    cpu_spinner.run()


if __name__ == "__main__":
    main()
    # print(game.__str__())
