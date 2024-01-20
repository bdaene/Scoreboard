from functools import partial

from nicegui import ui
from nicegui.elements.label import Label

from scoreboard import models, controller
from scoreboard.config import config
from scoreboard.gui.utils import Events


def update_player_label(player: models.player, target: models.player, label: Label):
    if player.pk == target.pk:
        label.set_text(player.name)


async def build(current_tournament: models.Tournament, events: Events):
    score_config = config().tournament.score

    async def build_player_row(round: models.round, seat: models.Seat):
        player = await seat.player.get()
        score = await models.Score.get_or_none(round=round, player=player)

        ui.label(seat.number)
        player_name = ui.label(player.name).classes('mr-auto')
        score_labels = []
        score_inputs = []
        for field_config in score_config:
            with ui.row(wrap=False):
                field_label = ui.label('' if not score else getattr(score, field_config.name))
                field_input = ui.input().classes('w-6 text-end')
            score_labels.append(field_label)
            score_inputs.append(field_input)
            field_input.visible = False

        with ui.row(wrap=False):
            edit_button = ui.button(icon='edit')
            done_button = ui.button(icon='done')
            done_button.visible = False

        events.player_modified.register(partial(update_player_label, target=player, label=player_name))

        async def toggle_score():
            if done_button.visible:
                if not all(field_input.value for field_input in score_inputs):
                    ui.notify("All fields must have a value!", type='negative')
                    return
                score_values = {field_config.name: field_input.value
                                for field_config, field_input in zip(score_config, score_inputs)}
                score, created = await models.Score.get_or_create(score_values, round=round, player=player)
                if not created:
                    await score.update_from_dict(score_values).save()
                await score.fetch_related('player', 'round')
                events.score_updated.send(score=score)

                for field_input, field_label in zip(score_inputs, score_labels):
                    field_label.text = field_input.value
            else:
                for field_input, field_label in zip(score_inputs, score_labels):
                    field_input.value = field_label.text

            for element in score_labels + score_inputs + [edit_button, done_button]:
                element.visible = not element.visible

        edit_button.on('click', toggle_score)
        done_button.on('click', toggle_score)

    async def build_round_grid(round: models.Round):
        with (ui.grid(columns=3 + len(score_config))
                .classes('w-full items-align content-start items-center gap-y-0')
                .style(f'grid-template-columns: auto 1fr repeat({1 + len(score_config)}, 0.2fr)')) as grid:
            async for table in round.tables.all().order_by('number'):
                ui.label(f"Table {table.number}").classes('font-bold col-span-2 mr-auto')
                for field in score_config:
                    ui.label(field.label if table.number == 1 else '').classes('font-bold w-fill')
                ui.label('')

                async for seat in table.seats.all().order_by('number'):
                    await build_player_row(round, seat)

    async def build_round_panel(round: models.Round):
        round_name = f'round_{round.number}'
        with tabs:
            ui.tab(round_name, label=f'Round {round.number}')
        button.move()
        with tab_panels:
            with ui.tab_panel(round_name):
                await build_round_grid(round)
        tab_panels.set_value(round_name)

    async def create_round():
        new_round = await controller.create_round(current_tournament)
        await build_round_panel(new_round)
        tab_panels.value = f'round_{new_round.number}'
        events.round_created.send(round=new_round)

    with ui.column().classes('w-full'):
        tabs = ui.tabs().classes('wrap')
        tab_panels = ui.tab_panels(tabs).classes('w-full')
        with tabs:
            button = ui.button(icon='add', on_click=create_round)

        async for round in current_tournament.rounds.all().order_by('number'):
            await build_round_panel(round)
