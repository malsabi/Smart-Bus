class Event:
    def __init__(self):
        self.handlers = {}

    def add_handler(self, handler_name, handler):
        self.handlers[handler_name] = handler

    def remove_handler(self, handler_name):
        del self.handlers[handler_name]

    def trigger(self, handler_name, *args, **kwargs):
        if handler_name in self.handlers:
            self.handlers[handler_name](*               args, **kwargs)