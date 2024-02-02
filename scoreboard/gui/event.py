import asyncio
import logging
from enum import Enum
from typing import Callable

from nicegui import Client

_logger = logging.getLogger(__name__)


class Event:
    def __init__(self, name: str = ''):
        self.name: str = name
        self.callbacks: list[Callable] = []

    def register(self, callback: Callable):
        self.callbacks.append(callback)

    async def send(self, *args, **kwargs):
        callbacks = [callback(*args, **kwargs) for callback in self.callbacks]
        await asyncio.gather(*callbacks)


class EventType(Enum):
    PLAYER_ADDED = 'PLAYER_ADDED'
    PLAYER_MODIFIED = 'PLAYER_MODIFIED'
    PLAYER_REMOVED = 'PLAYER_REMOVED'
    ROUND_CREATED = 'ROUND_CREATED'
    SCORE_UPDATED = 'SCORE_UPDATED'


class TournamentEvents:
    def __init__(self):
        self.clients_events: dict[Client, dict[EventType, Event]] = {}

    def add_client(self, client: Client):
        _logger.debug(f"Add {client}.")
        self.clients_events[client] = {event_type: Event() for event_type in EventType}

    def remove_client(self, client: Client):
        _logger.debug(f"Remove {client}.")
        del self.clients_events[client]

    def register(self, client: Client, event_type: EventType, callback: Callable):
        _logger.debug(f"Register {client} {event_type} {callback}.")
        self.clients_events[client][event_type].register(callback)

    async def send(self, event_type: EventType, /, *args, **kwargs):
        _logger.debug(f"Send {event_type} ({args} {kwargs}).")
        sends = [events[event_type].send(*args, **kwargs) for events in self.clients_events.values()]
        await asyncio.gather(*sends)
