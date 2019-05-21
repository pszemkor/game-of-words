import pygame
from pygame.locals import *
from enum import Enum
import controller_events as events
import config
import view
import model


class ScreenState(Enum):
    MENU = 0
    GAME = 1
    END_SCORE = 2
    ABOUT = 3
    BAG_OF_LETTERS = 4
    SETTINGS_MENU = 5
    BOARD_EDITOR = 6


def Debug(msg):
    print(msg)


def In2dArray(array, el_searched):
    for row in array:
        for e in row:
            if e == el_searched:
                return True
    return False


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
        if not isinstance(event, events.TickEvent):
            Debug("     Message: " + event.name)
        for listener in self.listeners.keys():
            listener.notify(event)


class CPUSpinnerController:
    def __init__(self, event_manager):
        self.going = True
        self.event_manager = event_manager
        self.event_manager.register(self)

    def run(self):
        clock = pygame.time.Clock()
        elapsed = 0
        while self.going:
            event = events.TickEvent()
            self.event_manager.post(event)
            clock.tick(100)
            elapsed += 1

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self.going = False


class MouseEventHandler:
    def __init__(self, event_manager, game):
        self.event_manager = event_manager
        self.game = game

    def get_event_from_clicked_sprites(self, sprites):
        if self.event_manager.screen_state == ScreenState.GAME:
            sprite = sprites[0]
            if hasattr(sprite, 'field') and In2dArray(self.game.board.fields, sprite.field):
                ev_to_send = events.SelectFieldEvent(sprite.field, model.FieldGroup.BOARD)
                return ev_to_send
            elif hasattr(sprite, 'field') and sprite.field in self.game.active_player.tilebox.fields:
                ev_to_send = events.SelectFieldEvent(sprite.field, model.FieldGroup.TILEBOX)
                return ev_to_send
            elif hasattr(sprite, 'button') and sprite.button.text == 'Confirm':
                ev_to_send = events.ConfirmButtonPressedEvent()
                return ev_to_send
            elif hasattr(sprite, 'button') and sprite.button.text == 'Pass':
                ev_to_send = events.PassButtonPressedEvent()
                return ev_to_send
            elif hasattr(sprite, 'button') and sprite.button.text == 'Shuffle':
                ev_to_send = events.ShuffleButtonPressedEvent()
                return ev_to_send
            elif hasattr(sprite, 'button') and sprite.button.text == 'Fact':
                ev_to_send = events.FactButtonPressedEvent()
                return ev_to_send
            elif hasattr(sprite, 'button') and sprite.button.text == 'Surrender':
                ev_to_send = events.SurrenderButtonPressedEvent()
                return ev_to_send


class MouseController:
    def __init__(self, event_manager, view_, game):
        self.event_manager = event_manager
        self.event_manager.register(self)
        self.mouse_event_handler = MouseEventHandler(self.event_manager, game)
        self.view = view_

    def notify(self, event):
        if isinstance(event, events.TickEvent):
            for ev in pygame.event.get():

                event_to_send = None
                if ev.type == pygame.QUIT:
                    event_to_send = events.QuitEvent()
                # left mouse button
                elif ev.type == pygame.MOUSEBUTTONUP:
                    if ev.button == 1:
                        all_sprites = list(self.view.back_sprites) + list(self.view.front_sprites)
                        clicked_sprites = [s for s in all_sprites if s.rect.collidepoint(ev.pos)]
                        if len(clicked_sprites) > 0:
                            event_to_send = self.mouse_event_handler.get_event_from_clicked_sprites(clicked_sprites)
                        pass

                if event_to_send:
                    self.event_manager.post(event_to_send)
