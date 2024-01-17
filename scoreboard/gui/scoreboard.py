from attr import asdict
from nicegui import ui

from scoreboard.config import config
from scoreboard.gui import players, rounds, summary


def style():
    ui.button.default_props('round')
    ui.input.default_props('dense')


def build():
    style()

    dark_mode = ui.dark_mode(value=config().gui.dark).props('align-right')
    with ui.left_drawer(value=True, elevated=True, bottom_corner=True) as players_panel:
        players.build()
        ui.button(icon='menu_open', on_click=players_panel.hide).classes('mu-auto ml-auto').props('flat')

    with ui.header():
        ui.button(icon='person', on_click=players_panel.toggle)
        ui.label("Tournament").classes('font-bold ml-auto self-center text-2xl')
        ui.button(icon='dark_mode', on_click=dark_mode.toggle).classes('ml-auto')

    with ui.row(wrap=False).classes('w-full h-screen'):
        rounds.build()
        summary.build()


def start():
    style()
    build()
    # app.on_connect(actions['show_tournament_dialog'])
    ui.run(**asdict(config().gui))
