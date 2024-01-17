import asyncio
from functools import partial

from nicegui import ui

from scoreboard import models
from scoreboard.gui.utils import Event


def build():
    player_created = Event('player_state_created')
    player_name_updated = Event('player_name_updated')
    player_state_updated = Event('player_state_updated')

    async def switch_player_state(player):
        player.is_active = not player.is_active
        await player.save()
        state = 'active' if player.is_active else 'not active'
        ui.notify(f"Player {player.name} is {state}.")
        await player_state_updated.send()

    async def modify_player_name(player, value):
        if player.name == value:
            return
        player.name = value
        await player.save()
        ui.notify(f"Player {player.name} updated.")
        await player_name_updated.send()

    async def build_editable_player(player: models.Player):
        with ui.row(wrap=False):
            player_label = ui.label().bind_text_from(player, 'name').classes('mr-auto self-center')
            player_input = ui.input(value=player.name)
            player_input.visible = False
            player_button = ui.button(icon='edit').props('flat')
        ui.switch(value=player.is_active, on_change=partial(switch_player_state, player))

        async def toggle_edit(update=True):
            if update and player_input.visible:
                await modify_player_name(player, player_input.value)

            player_label.visible = not player_label.visible
            player_button.visible = not player_button.visible
            player_input.visible = not player_input.visible

        player_label.on('click', toggle_edit)
        player_button.on('click', toggle_edit)
        player_input.on('blur', toggle_edit)
        player_input.on('keydown.enter', toggle_edit)
        player_input.on('keydown.escape', partial(toggle_edit, update=False))

    @ui.refreshable
    async def list_of_players():
        players: list[models.Player] = await models.Player.all().order_by('name')
        for player in players:
            await build_editable_player(player)

    player_created.register(lambda _player: list_of_players.refresh())

    async def create_player():
        if not name.value:
            return
        new_player = await models.Player.create(name=name.value)
        name.value = ''
        ui.notify(f"New player {new_player.name}.")
        await player_created.send(new_player)

    with ui.grid(columns=2).classes('items-align content-start').style("grid-template-columns: 1fr auto"):
        ui.label("Name")
        ui.label("Active")

        ui.separator().classes('col-span-2')

        asyncio.run(list_of_players())

        ui.separator().classes('col-span-2')

        name = ui.input(placeholder='Name')
        ui.button(icon='add', on_click=create_player).classes('self-center ml-auto')
