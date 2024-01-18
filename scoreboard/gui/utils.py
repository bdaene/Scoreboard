import asyncio


class Event:
    def __init__(self):
        self.callbacks = []

    def register(self, callback):
        self.callbacks.append(callback)

    async def send(self, *args):
        await asyncio.gather(callback(*args) for callback in self.callbacks)
