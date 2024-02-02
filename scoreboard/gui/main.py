from multiprocessing.connection import Client

from attr import asdict
from nicegui import ui

from scoreboard import models
from scoreboard.config import config
from scoreboard.gui.scoreboard import ScoreBoardFrame
from scoreboard.gui.tournament import TournamentSelectionFrame


def style():
    ui.button.default_props('round flat dense')
    ui.input.default_props('dense')
    ui.tabs.default_props('dense')


def build():
    style()

    @ui.page('/')
    def index_page():
        ui.open('/tournaments')

    @ui.page('/tournaments')
    async def tournament_page(client: Client, unknown_tournament: str = ''):
        tournaments = await models.Tournament.all()
        TournamentSelectionFrame(client, tournaments)
        if unknown_tournament:
            ui.notify(f"Tournament {unknown_tournament} not found", type='negative')

    @ui.page('/tournaments/{tournament_name}')
    async def scoreboard_page(client: Client, tournament_name: str):
        tournament = await models.Tournament.get_or_none(name=tournament_name)
        if tournament is None:
            ui.open(f'/tournaments?unknown_tournament={tournament_name}')
            return

        await tournament.fetch_related('players', 'rounds__tables__seats__player', 'rounds__scores__player')
        ScoreBoardFrame(client, tournament)


def start():
    build()

    ui.run(reload=False, **asdict(config().gui))
