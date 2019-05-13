import pygame
from pygame.locals import *
from enum import Enum

import config
import view


def Debug(msg):
    print(msg)


class EventManager:
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.screen_state = ScreenState.GAME

    def register(self, listener):
        self.listeners[listener] = 1

    def unregister(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, event):
        if not isinstance(event, TickEvent):
            Debug("     Message: " + event.name)
        for listener in self.listeners.keys():
            listener.notify(event)


class Event:
    def __init__(self):
        self.name = "Generic event"


class TickEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "CPU Tick Event"


class QuitEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "Quit Event"


class MouseEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "Mouse Event"


class TileBoxEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "Tile Box Event"


class EmptyFieldEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "Empty Field Event"


class GameStartedEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "Game Started Event"


# Initialize game events
class BoardBuildEvent(Event):
    def __init__(self, board):
        super().__init__()
        self.name = "Build Board Event"
        self.board = board


class TileBoxBuildEvent(Event):
    def __init__(self, tilebox):
        super().__init__()
        self.name = "Build TileBox Event"
        self.tilebox = tilebox


# superior event for buttons
class ButtonEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "Button Event"


class ConfirmButtonEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "ConfirmButtonEvent"


class SelectBoardFieldEvent(Event):
    def __init__(self, coords):
        super().__init__()
        self.name = "SelectBoardFieldEvent"
        self.coords = coords


class SelectTileBoxFieldEvent(Event):
    def __init__(self, coords):
        super().__init__()
        self.name = "SelectTileBoxFieldEvent"
        self.coords = coords


class ConfirmButtonPressedEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "ConfirmButtonPressedEvent"


# #################################################################

class ScreenState(Enum):
    MENU = 0
    GAME = 1
    END_SCORE = 2
    ABOUT = 3
    BAG_OF_LETTERS = 4
    BOARD_EDITOR = 5


# #################################################################

class VerifyBoardEvent(Event):
    def __init__(self, board):
        super().__init__()
        self.name = "VerifyBoardEvent"
        self.board = board


class CPUSpinnerController:
    def __init__(self, event_manager):
        self.going = True
        self.event_manager = event_manager
        self.event_manager.register(self)

    def run(self):
        clock = pygame.time.Clock()
        elapsed = 0
        while self.going:
            event = TickEvent()
            self.event_manager.post(event)
            clock.tick(100)
            elapsed += 1

    def notify(self, event):
        if isinstance(event, QuitEvent):
            self.going = False


# todo -> check coordinates and set event_to_sent (it depends on coordinates)
class MouseEventHandler:
    def __init__(self, event_manager):
        self.event_manager = event_manager

    def get_event_from_coordinates(self, coords):
        if self.event_manager.screen_state == ScreenState.GAME:
            print(coords)
            if coords[0] in range(config.LEFT_EDGE_BOARD_OFFSET, config.LEFT_EDGE_BOARD_OFFSET + config.BOARD_WIDTH) \
                    and coords[1] in range(config.TOP_EDGE_BOARD_OFFSET,
                                           config.TOP_EDGE_BOARD_OFFSET + config.BOARD_WIDTH):
                field_coords = [0, 0]
                field_coords[0] = (coords[0] - config.LEFT_EDGE_BOARD_OFFSET) // config.FIELD_RECTANGLE_WIDTH
                field_coords[1] = (coords[1] - config.TOP_EDGE_BOARD_OFFSET) // config.FIELD_RECTANGLE_WIDTH
                ev_to_send = SelectBoardFieldEvent(field_coords)
                print('Plansza!!', field_coords[0], field_coords[1])
                return ev_to_send
            pass


class MouseController:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.register(self)
        self.mouse_event_handler = MouseEventHandler(self.event_manager)

    def notify(self, event):
        if isinstance(event, TickEvent):
            for ev in pygame.event.get():
                event_to_send = None

                if ev.type == pygame.QUIT:
                    event_to_send = QuitEvent()
                # left mouse button
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        event_to_send = self.mouse_event_handler.get_event_from_coordinates(ev.pos)
                        pass

                if event_to_send:
                    self.event_manager.post(event_to_send)
