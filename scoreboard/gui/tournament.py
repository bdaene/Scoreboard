import logging
from multiprocessing.connection import Client

from nicegui import ui

from scoreboard import models
from scoreboard.config import config

_LOGGER = logging.getLogger(__name__)


class TournamentSelectionFrame:

    def __init__(self, client: Client, tournaments: list[models.Tournament]):
        self.client = client
        self.tournaments = tournaments
        self.options = sorted(tournament.name for tournament in self.tournaments)

        self.tournaments_select = None
        self.select_button = None

        self._build()

    def _build(self):
        _LOGGER.debug(f"Building {self.__class__} for client {self.client}.")
        ui.dark_mode(value=config().gui.dark)
        with ui.dialog(value=True).props('persistent'), ui.card():
            with ui.row().classes('align-center'):
                self.tournaments_select = ui.select(label='Tournament :', options=self.options,
                                                    new_value_mode='add-unique')
                self.select_button = ui.button('Select').props(remove='round').classes('self-center')

        self.select_button.on('click', self.select_tournament)

    async def select_tournament(self):
        tournament_name = self.tournaments_select.value
        if not tournament_name:
            return

        tournament, created = await models.Tournament.get_or_create(name=tournament_name)
        if created:
            _LOGGER.info(f"Tournament {tournament.name} created.")
        ui.open(f'/tournaments/{tournament_name}')
