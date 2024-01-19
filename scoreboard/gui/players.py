from functools import partial

from nicegui import ui

from scoreboard import models
from scoreboard.gui.utils import Events, sort_in_parent


async def build(current_tournament: models.Tournament, events: Events):
    async def build_editable_player(player: models.Player, sort=False):
        with ui.row(wrap=False).classes('w-full') as player_row:
            player_label = ui.label().bind_text_from(player, 'name').classes('mr-auto self-center')
            player_edit = ui.button(icon='edit')
            player_remove = ui.button(icon='delete')
            player_input = ui.input(value=player.name)
            player_input.visible = False

        player_row.player = player
        if sort:
            sort_in_parent(player_row)

        async def toggle_edit(update=True):
            if update and player_input.visible:
                if player.name != player_input.value:
                    player.name = player_input.value
                    await player.save()
                    events.player_modified.send(player=player)
                    player_label.text = player_input.value
                    sort_in_parent(player_row)
            else:
                player_input.value = player_label.text

            player_label.visible = not player_label.visible
            player_edit.visible = not player_edit.visible
            player_remove.visible = not player_remove.visible
            player_input.visible = not player_input.visible

        player_edit.on('click', toggle_edit)
        player_input.on('keydown.enter', toggle_edit)
        player_input.on('keydown.escape', partial(toggle_edit, update=False))

        async def remove_player():
            await current_tournament.players.remove(player)
            events.player_removed.send(player=player)
            player_row.parent_slot.children.remove(player_row)
            player_row.parent_slot.parent.update()

        player_remove.on('click', remove_player)

    async def add_player():
        if not name.value:
            return
        player, created = await models.Player.get_or_create(name=name.value)
        await current_tournament.players.add(player)
        events.player_added.send(player=player)
        name.value = ''
        with column:
            await build_editable_player(player, sort=True)

    with ui.column().classes('items-align content-start') as column:
        with ui.row(wrap=False):
            name = ui.input(placeholder='Player name').classes('mr-auto self-center')
            ui.button(icon='add', on_click=add_player)
            ui.button(icon='menu_open', on_click=column.parent_slot.parent.hide)

        async for player in current_tournament.players.all().order_by('name'):
            await build_editable_player(player)

    name.on('keydown.enter', add_player)
