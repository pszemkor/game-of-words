import pygame


class EventManager:
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()

    def register(self, listener):
        self.listeners[listener] = 1

    def unregister(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, event):
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


# superior event for buttons
class ButtonEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "Button Event"


class ConfirmButtonEvent(Event):
    def __init__(self):
        super().__init__()
        self.name = "ConfirmButtonEvent"


class CPUSpinnerController:
    def __init__(self, event_manager):
        self.going = True
        self.event_manager = event_manager
        self.event_manager.register(self)

    def run(self):
        clock = pygame.time.Clock()
        elapsed = 0
        while self.going:
            clock.tick(100)
            event = TickEvent()
            self.event_manager.post(event)
            elapsed += 1

    def notify(self, event):
        if isinstance(event, QuitEvent):
            self.going = False


# todo -> check coordinates and set event_to_sent (it depends on coordinates)
class MouseEventHandler:
    @staticmethod
    def get_event_from_coordinates(coords):
        pass


class MouseController:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.register(self)

    def notify(self, event):
        if isinstance(event, TickEvent):
            for ev in pygame.event.get():
                event_to_send = None

                # left mouse button
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        event_to_send = MouseEventHandler.get_event_from_coordinates(ev.pos)
                        pass
                if event_to_send:
                    self.event_manager.post(event_to_send)
