class EventMenager:
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
            listener.notify()


