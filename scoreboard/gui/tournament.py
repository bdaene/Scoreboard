from nicegui import ui

from scoreboard import models
from scoreboard.gui.utils import Event

tournament_selected = Event('tournament_selected')


async def build(unknown_tournament: str = ''):
    with ui.dialog(value=True).props('persistent'), ui.card():
        if unknown_tournament:
            ui.notify(f"Tournament {unknown_tournament} not found", type='negative')

        tournaments: list[models.Tournament] = await models.Tournament.all()
        options = sorted(tournament.name for tournament in tournaments)
        with ui.row().classes('align-center'):
            select = ui.select(label='Tournament :', options=options, new_value_mode='add-unique')
            button = ui.button('Select').props(remove='round').classes('self-center')

        async def select_tournament():
            tournament_name = select.value
            if not tournament_name:
                return

            await models.Tournament.get_or_create(name=tournament_name)

            ui.open(f'/tournaments/{tournament_name}')

        button.on('click', select_tournament)
