from attrs import asdict
from nicegui import ui

from scoreboard import models
from scoreboard.config import config
from scoreboard.gui import players, rounds, summary, tournament
from scoreboard.gui.utils import Events


def style():
    ui.button.default_props('round flat dense')
    ui.input.default_props('dense')
    ui.tabs.default_props('dense')


def build():
    style()

    @ui.page('/')
    def index_page():
        ui.open('/tournaments')

    ui.page('/tournaments')(tournament.build)

    @ui.page('/tournaments/{tournament_name}')
    async def page(tournament_name: str):
        current_tournament = await models.Tournament.get_or_none(name=tournament_name)
        if current_tournament is None:
            ui.open(f'/tournaments?unknown_tournament={tournament_name}')
            return

        events = Events()
        ui.page_title(f'Score Board - {current_tournament.name}')
        dark_mode = ui.dark_mode(value=config().gui.dark)
        with ui.left_drawer(value=True, elevated=True, bottom_corner=True) as players_panel:
            await players.build(current_tournament, events)

        with ui.header():
            ui.button(icon='person', on_click=players_panel.toggle, color='white').classes(remove='bg-white')
            ui.button(icon='emoji_events', on_click=index_page, color='white').classes(remove='bg-white')
            ui.label().bind_text_from(current_tournament, 'name').classes('font-bold ml-auto self-center text-2xl')
            with ui.row(wrap=False).classes('ml-auto'):
                dark_button = ui.button(icon='dark_mode', color='white').classes(remove='bg-white')
                light_button = ui.button(icon='light_mode', color='white').classes(remove='bg-white')
                if dark_mode.value:
                    dark_button.visible = False
                else:
                    light_button.visible = False

        async def toggle_dark_mode():
            dark_mode.toggle()
            config().gui.dark = dark_mode.value
            dark_button.visible = not dark_button.visible
            light_button.visible = not light_button.visible

        dark_button.on('click', toggle_dark_mode)
        light_button.on('click', toggle_dark_mode)

        with ui.row(wrap=False).classes('w-full h-full'):
            await rounds.build(current_tournament, events)
            await summary.build(current_tournament, events)


def start():
    style()
    build()

    ui.run(reload=False, **asdict(config().gui))
