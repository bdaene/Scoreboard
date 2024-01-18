from functools import partial

from nicegui import ui

from scoreboard import models


async def build(current_tournament: models.Tournament):
    async def modify_player_name(player, value):
        if player.name == value:
            return
        player.name = value
        await player.save()
        ui.notify(f"Player {player.name} updated.")
        list_of_players.refresh()

    async def build_editable_player(player: models.Player):
        with ui.row(wrap=False).classes('w-full'):
            player_label = ui.label().bind_text_from(player, 'name').classes('mr-auto self-center')
            player_edit = ui.button(icon='edit')
            player_remove = ui.button(icon='delete')
            player_input = ui.input(value=player.name)
            player_input.visible = False

        async def toggle_edit(update=True):
            if update and player_input.visible:
                await modify_player_name(player, player_input.value)

            player_label.visible = not player_label.visible
            player_edit.visible = not player_edit.visible
            player_remove.visible = not player_remove.visible
            player_input.visible = not player_input.visible

        player_label.on('click', toggle_edit)
        player_edit.on('click', toggle_edit)
        player_input.on('blur', toggle_edit)
        player_input.on('keydown.enter', toggle_edit)
        player_input.on('keydown.escape', partial(toggle_edit, update=False))

        async def remove_player():
            await current_tournament.players.remove(player)
            list_of_players.refresh()
            ui.notify(f"Player {player.name} removed.")

        player_remove.on('click', remove_player)

    @ui.refreshable
    async def list_of_players():
        async for player in current_tournament.players.all().order_by('name'):
            await build_editable_player(player)

    async def add_player():
        if not name.value:
            return
        player, _ = await models.Player.get_or_create(name=name.value)
        await current_tournament.players.add(player)
        name.value = ''
        ui.notify(f"New player {player.name}.")
        list_of_players.refresh()

    with ui.column().classes('items-align content-start') as column:
        with ui.row(wrap=False):
            name = ui.input(placeholder='Player name').classes('mr-auto self-center')
            ui.button(icon='add', on_click=add_player)
            ui.button(icon='menu_open', on_click=column.parent_slot.parent.hide)

        await list_of_players()

    name.on('keydown.enter', add_player)
