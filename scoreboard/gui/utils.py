import asyncio

from attr import define

from scoreboard import models

events = {}


class Event:
    def __init__(self, name: str):
        if name in events:
            raise ValueError(f"Event {name} exists already.")
        events[name] = self
        self.callbacks = []
        self.name = name

    def register(self, callback):
        self.callbacks.append(callback)

    async def send(self, *args):
        await asyncio.gather(callback(*args) for callback in self.callbacks)


@define
class State:
    current_tournament: models.Tournament

