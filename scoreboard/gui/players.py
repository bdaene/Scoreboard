import logging
from bisect import insort
from functools import partial
from operator import attrgetter

from nicegui import ui, Client

from scoreboard import models
from scoreboard.gui.event import TournamentEvents, EventType

_LOGGER = logging.getLogger(__name__)


class PlayerRow:
    def __init__(self, tournament: models.Tournament, events: TournamentEvents, player: models.Player):
        self.tournament = tournament
        self.events = events
        self.player = player

        self._build()

        self.input.on('keydown.enter', self.validate)
        self.input.on('keydown.escape', partial(self.validate, cancel=True))
        self.edit_button.on('click', lambda: self.toggle_edit() if self.label.visible else self.validate())
        self.remove_button.on('click', self.remove)

    def _build(self):
        with ui.row(wrap=False).classes('w-full') as self.row:
            self.label = ui.label(self.player.name).classes('mr-auto self-center')
            self.input = ui.input(value=self.player.name)
            self.edit_button = ui.button(icon='edit')
            self.remove_button = ui.button(icon='delete')

        self.input.visible = False

        self.row.player = self.player

    def sort_in_parent(self):
        slot = self.row.parent_slot
        slot.children.remove(self.row)
        insort(slot.children, self.row, lo=1, key=lambda e: e.player.name)
        slot.parent.update()

    def update_player(self, player: models.Player):
        self.player = player
        self.label.text = player.name
        self.input.value = player.name

    async def toggle_edit(self):
        self.label.visible = not self.label.visible
        self.input.visible = not self.input.visible
        self.edit_button.props(f"icon={'edit' if self.label.visible else 'done'}")

    async def validate(self, cancel=False):
        await self.toggle_edit()
        if cancel:
            self.input.value = self.label.text
            return

        if self.input.value == self.player.name:
            return

        self.player.name = self.input.value
        await self.player.save()
        _LOGGER.info(f"Tournament {self.tournament.name}: Player {self.player.name} modified.")
        await self.events.send(EventType.PLAYER_MODIFIED, self.player)

    async def remove(self):
        await self.tournament.players.remove(self.player)
        _LOGGER.info(f"Tournament {self.tournament.name}: Player {self.player.name} removed.")
        await self.events.send(EventType.PLAYER_REMOVED, self.player)


class PlayersFrame:

    def __init__(self, client: Client, events: TournamentEvents, tournament: models.Tournament):
        self.client = client
        self.events = events
        self.tournament = tournament
        self.player_rows: dict[models.player, PlayerRow] = {}

        self._build()

        self.player_input.on('keydown.enter', self.add_player)
        self.add_button.on('click', self.add_player)

        self.events.register(self.client, EventType.PLAYER_ADDED, self.on_player_added)
        self.events.register(self.client, EventType.PLAYER_MODIFIED, self.on_player_modified)
        self.events.register(self.client, EventType.PLAYER_REMOVED, self.on_player_removed)

    def _build(self):
        _LOGGER.debug(f"Building {self} for client {self.client}.")
        with ui.column().classes('items-align content-start') as self.column:
            with ui.row(wrap=False):
                self.player_input = ui.input(placeholder='Player name').classes('mr-auto self-center')
                self.add_button = ui.button(icon='add')
                self.menu_button = ui.button(icon='menu_open')

            for player in sorted(self.tournament.players, key=attrgetter('name')):
                self.player_rows[player] = PlayerRow(self.tournament, self.events, player)

    async def add_player(self):
        if not self.player_input.value:
            return
        player_name = self.player_input.value
        self.player_input.value = ''

        player, _ = await models.Player.get_or_create(name=player_name)
        await self.tournament.players.add(player)
        _LOGGER.info(f"Tournament {self.tournament.name}: Player {player.name} added.")
        await self.events.send(EventType.PLAYER_ADDED, player)

    async def on_player_removed(self, player):
        player_row = self.player_rows.get(player)
        if player_row is None:
            return
        self.column.default_slot.children.remove(player_row.row)
        self.column.update()
        del self.player_rows[player]
        self.client.notify(f"Player {player.name} removed.")

    async def on_player_added(self, player):
        await self.on_player_removed(player)
        with self.column:
            player_row = PlayerRow(self.tournament, self.events, player)
            self.player_rows[player] = player_row
            player_row.sort_in_parent()
        self.client.notify(f"Player {player.name} added.")

    async def on_player_modified(self, player):
        player_row = self.player_rows.get(player)
        if player_row is None:
            return
        player_row.update_player(player)
        self.client.notify(f"Player {player.name} modified.")
