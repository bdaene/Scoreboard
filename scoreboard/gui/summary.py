from nicegui import ui

from scoreboard import models


async def build(current_tournament: models.Tournament):
    columns = [
        dict(name='name', label='Player Name', field='name', align='left'),
        dict(name='round_1', label='Round 1', field='round_1'),
        dict(name='round_2', label='Round 2', field='round_2'),
    ]
    rows = [
        dict(name='Player 1', round_1=5, round_2=3),
        dict(name='Player 2', round_1=3, round_2=1),
        dict(name='Player 3'),
    ]
    table = ui.table(columns=columns, rows=rows, title='Leaderboard').classes('w-full')

    with table.add_slot('top-right'):
        async def toggle_full_screen():
            table.toggle_fullscreen()
            button.props('icon=fullscreen_exit' if table.is_fullscreen else 'icon=fullscreen')
        button = ui.button(icon='fullscreen', on_click=toggle_full_screen).props('flat')

