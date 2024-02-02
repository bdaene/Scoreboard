import logging
from functools import partial

from nicegui import ui, Client

from scoreboard import models
from scoreboard.config import config
from scoreboard.gui.event import TournamentEvents
from scoreboard.gui.players import PlayersFrame
from scoreboard.gui.rounds import RoundsFrame
from scoreboard.gui.summary import SummaryFrame

_LOGGER = logging.getLogger(__name__)

tournaments_events: dict[models.Tournament, TournamentEvents] = {}


class ScoreBoardHeader:
    def __init__(self, tournament: models.Tournament):
        self.tournament = tournament
        self.dark_mode = ui.dark_mode(value=config().gui.dark)

        self._build()

    def _build(self):
        with ui.header():
            self.player_button = ui.button(icon='person', color='white').classes(remove='bg-white')
            self.tournaments_button = ui.button(icon='emoji_events', color='white').classes(remove='bg-white')
            self.title_label = ui.label(text=self.tournament.name).classes('font-bold ml-auto self-center text-2xl')
            self.dark_mode_button = ui.button(icon='dark_mode', color='white').classes('ml-auto', remove='bg-white')

        self.update_dark_mode()

        self.tournaments_button.on('click', partial(ui.open, '/tournaments'))
        self.dark_mode_button.on('click', partial(self.update_dark_mode, toggle=True))

    def update_dark_mode(self, toggle=False):
        if toggle:
            self.dark_mode.toggle()
        self.dark_mode_button.props(f"icon={'light_mode' if self.dark_mode.value else 'dark_mode'}")


class ScoreBoardFrame:
    def __init__(self, client: Client, tournament: models.Tournament):
        self.client = client
        self.tournament = tournament
        self.events = tournaments_events.setdefault(tournament, TournamentEvents())

        self.events.add_client(self.client)
        self.client.on_disconnect(partial(self.events.remove_client, self.client))
        self.client.notify = lambda message: self.client.outbox.enqueue_message('notify', dict(message=message),
                                                                                self.client.id)

        self._build()

        self.header.player_button.on('click', self.players_panel.toggle)
        self.players.menu_button.on('click', self.players_panel.toggle)

    def _build(self):
        _LOGGER.debug(f"Building {self} for client {self.client}.")
        ui.page_title(f'Score Board - {self.tournament.name}')
        self.header = ScoreBoardHeader(self.tournament)
        with ui.left_drawer(value=True, elevated=True, bottom_corner=True) as self.players_panel:
            self.players = PlayersFrame(self.client, self.events, self.tournament)
        with ui.row(wrap=False).classes('w-full h-full'):
            self.rounds = RoundsFrame(self.client, self.events, self.tournament)
            self.summary = SummaryFrame(self.client, self.events, self.tournament)
