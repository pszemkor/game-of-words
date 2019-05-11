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


class MouseController:
    def notify(self, event):
        pass
