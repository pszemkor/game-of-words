import pygame
from enum import Enum
import controller_events as events
import model
from tkinter import Tk
from tkinter.filedialog import askopenfilename


class ScreenState(Enum):
    NORMAL = 0
    EDIT = 1


def debug(msg):
    print(msg)


def in2darray(array, el_searched):
    for row in array:
        for e in row:
            if e == el_searched:
                return True
    return False


class EventManager:
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.screen_state = ScreenState.NORMAL

    def register(self, listener):
        self.listeners[listener] = 1

    def unregister(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, event):
        if not isinstance(event, events.TickEvent):
            debug("     Message: " + event.name)
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
        ev_to_send = None
        sprite = sprites[0]
        if hasattr(sprite, 'field') and in2darray(
                self.game.board.fields, sprite.field):
            ev_to_send = events.SelectFieldEvent(sprite.field,
                                                 model.FieldGroup.BOARD)
        elif hasattr(sprite, 'field') and sprite.field in \
                self.game.active_player.tilebox.fields:
            ev_to_send = events.SelectFieldEvent(sprite.field,
                                                 model.FieldGroup.TILEBOX)
        elif hasattr(sprite, 'button') and sprite.button.text == 'Confirm':
            ev_to_send = events.ConfirmButtonPressedEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Pass':
            self.game.active_player.put_all_temps_in_tilebox()
            ev_to_send = events.PassButtonPressedEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Mute':
            ev_to_send = events.MuteEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Unmute':
            ev_to_send = events.UnmuteEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Shuffle':
            ev_to_send = events.ShuffleButtonPressedEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Letters':
            ev_to_send = events.NewLettersButtonPressedEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Return':
            ev_to_send = events.TakeAllButtonEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Surrender':
            ev_to_send = events.SurrenderButtonPressedEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Play':
            pygame.mixer.music.stop()
            pygame.mixer.music.load(
                'music/Game of Thrones S8 - The Night '
                'King - Ramin Djawadi (Official Video) (128  kbps).mp3')
            pygame.mixer.music.play(-1)
            ev_to_send = events.NextPlayerMoveStartedEvent(self.game)
        elif hasattr(sprite, 'button') and sprite.button.text == 'About':
            ev_to_send = events.AboutBannerShowEvent()
        elif hasattr(sprite, 'button') and sprite.button.text \
                == 'Set difficulty':
            ev_to_send = events.MenuDifficultyBuildEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Easy':
            self.game.difficulty_level = model.DifficultyLevel.EASY
            ev_to_send = events.MenuBuildEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Medium':
            self.game.difficulty_level = model.DifficultyLevel.MEDIUM
            ev_to_send = events.MenuBuildEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Hard':
            self.game.difficulty_level = model.DifficultyLevel.HARD
            ev_to_send = events.MenuBuildEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Edit board':
            self.event_manager.screen_state = ScreenState.EDIT
            ev_to_send = events.EditDashboardBuildEvent(self.game.board)
        elif hasattr(sprite, 'button') and sprite.button.text == 'Save':
            self.event_manager.screen_state = ScreenState.NORMAL
            ev_to_send = events.MenuBuildEvent()
        elif hasattr(sprite, 'button') and sprite.button.text == 'Load':
            Tk().withdraw()
            filename = askopenfilename()
            self.game.board.get_board_from_file(filename)
            ev_to_send = events.EditDashboardBuildEvent(self.game.board)
        elif hasattr(sprite, 'button') \
                and sprite.button.text == 'Load dictionary':
            Tk().withdraw()
            filename = askopenfilename()
            self.game.dictionary.load_txt_file(filename)
            print('Loaded from file')

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
                        all_sprites = list(self.view.back_sprites) + \
                                      list(self.view.front_sprites)
                        clicked_sprites = [s for s in all_sprites
                                           if s.rect.collidepoint(ev.pos)]
                        if len(clicked_sprites) > 0:
                            event_to_send = self.mouse_event_handler. \
                                get_event_from_clicked_sprites(clicked_sprites)
                        pass

                if event_to_send:
                    self.event_manager.post(event_to_send)
