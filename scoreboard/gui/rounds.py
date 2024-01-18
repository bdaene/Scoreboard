from nicegui import ui

from scoreboard import models


async def build(current_tournament: models.Tournament):
    async def build_round(round: models.Round):
        round_name = f'round_{round.number}'
        with tabs:
            ui.tab(round_name, label=f'Round {round.number}')
        button.move()
        with tab_panels:
            with ui.tab_panel(round_name):
                with ui.card():
                    ui.number(label='Round', value=round.number)
        tab_panels.set_value(round_name)

    async def create_round():
        i = 1 + await models.Round.filter(tournament=current_tournament).count()
        round = await models.Round.create(number=i, tournament=current_tournament)
        await build_round(round)
        tab_panels.value = f'round_{round.number}'

    with ui.column().classes('w-full'):
        tabs = ui.tabs()
        tab_panels = ui.tab_panels(tabs).classes('w-full')
        with tabs:
            button = ui.button(icon='add', on_click=create_round)

        async for round in current_tournament.rounds.all().order_by('number'):
            await build_round(round)
        tabs.update()
        tab_panels.update()
