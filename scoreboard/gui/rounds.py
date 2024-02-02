import logging
from operator import attrgetter
from typing import Optional

from nicegui import ui, Client

from scoreboard import models, controller
from scoreboard.config import config
from scoreboard.gui.event import TournamentEvents, EventType

_LOGGER = logging.getLogger(__name__)


class PlayerRow:

    def __init__(self, events: TournamentEvents, tournament: models.Tournament, round: models.Round, seat: models.Seat,
                 score: Optional[models.Score]):
        self.events = events
        self.tournament = tournament
        self.round = round
        self.seat = seat
        self.player = seat.player
        self.score = score

        self.score_labels = []
        self.score_inputs = []

        self._build()

    def _build(self):
        ui.label(self.seat.number)
        self.player_label = ui.label(self.player.name).classes('mr-auto')
        for field_config in config().tournament.score:
            with ui.row(wrap=False):
                value = '' if self.score is None else getattr(self.score, field_config.name)
                score_label = ui.label(value)
                score_input = ui.input(value=value).classes('w-6 text-end')

            score_input.visible = False
            self.score_labels.append(score_label)
            self.score_inputs.append(score_input)

        with ui.row(wrap=False):
            self.edit_button = ui.button(icon='edit')

        for score_input in self.score_inputs:
            score_input.on('keydown.enter', self.validate)
            score_input.on('keydown.escape', self.toggle_edit)
        self.edit_button.on('click', lambda: self.toggle_edit() if self.score_labels[0].visible else self.validate())

    def update_player(self, player: models.Player):
        self.player = player
        self.player_label.text = player.name

    def update_score(self, score: models.Score):
        self.score = score
        for field, score_label, score_input in zip(config().tournament.score, self.score_labels, self.score_inputs):
            value = getattr(self.score, field.name)
            score_label.text = value
            score_input.value = value

    async def toggle_edit(self):
        for element in self.score_labels + self.score_inputs:
            element.visible = not element.visible
        self.edit_button.props(f"icon={'edit' if self.score_labels[0].visible else 'done'}")

    async def validate(self):
        if not all(score_input.value for score_input in self.score_inputs):
            ui.notify("All fields must have a value!", type='negative')
            return

        await self.toggle_edit()
        if self.score is not None and all(getattr(self.score, field.name) == score_input.value
                                          for field, score_input in zip(config().tournament.score, self.score_inputs)):
            return

        score_values = {field.name: score_input.value
                        for field, score_input in zip(config().tournament.score, self.score_inputs)}
        self.score, _ = await models.Score.update_or_create(score_values, round=self.round, player=self.player)
        await self.score.fetch_related('round', 'player')
        _LOGGER.info(f"Tournament {self.tournament.name}: "
                     f"Score of {self.score.round.number} for player {self.score.player.name} updated.")
        await self.events.send(EventType.SCORE_UPDATED, self.score)


class RoundFrame:
    def __init__(self, client: Client, events: TournamentEvents, tournament: models.Tournament, round: models.Round):
        self.client = client
        self.events = events
        self.tournament = tournament
        self.round = round
        self.scores: dict[models.Player, models.Score] = {score.player: score for score in self.round.scores}
        self.player_rows: dict[models.player, PlayerRow] = {}

        self._build()

    def _build(self):
        with (ui.grid(columns=3 + len(config().tournament.score))
                .classes('w-full items-align content-start items-center gap-y-0')
                .style(f'grid-template-columns: auto 1fr repeat({1 + len(config().tournament.score)}, 0.2fr)')
        ) as self.grid:
            for table in sorted(self.round.tables, key=attrgetter('number')):
                ui.label(f"Table {table.number}").classes('font-bold col-span-2 mr-auto')
                for field in config().tournament.score:
                    ui.label(field.label if table.number == 1 else '').classes('font-bold w-fill')
                ui.label('')

                for seat in sorted(table.seats, key=attrgetter('number')):
                    player_row = PlayerRow(self.events, self.tournament, self.round, seat, self.scores.get(seat.player))
                    self.player_rows[seat.player] = player_row

    def update_player(self, player: models.Player):
        player_row = self.player_rows.get(player)
        if player_row is None:
            return

        player_row.update_player(player)

    def update_score(self, score: models.Score):
        player_row = self.player_rows.get(score.player)
        if player_row is None:
            return
        player_row.update_score(score)


class RoundsFrame:
    def __init__(self, client: Client, events: TournamentEvents, tournament: models.Tournament):
        self.client = client
        self.events = events
        self.tournament = tournament
        self.round_frames: dict[models.Round, RoundFrame] = {}

        self._build()

        self.add_button.on('click', self.create_round)

        self.events.register(self.client, EventType.ROUND_CREATED, self.on_round_created)
        self.events.register(self.client, EventType.SCORE_UPDATED, self.on_score_updated)
        self.events.register(self.client, EventType.PLAYER_MODIFIED, self.on_player_modified)

    def _build(self):
        _LOGGER.debug(f"Building {self} for client {self.client}.")
        with ui.column().classes('w-full'):
            self.tabs = ui.tabs().classes('wrap')
            self.tab_panels = ui.tab_panels(self.tabs).classes('w-full')
            with self.tabs:
                self.add_button = ui.button(icon='add')

            for round in sorted(self.tournament.rounds, key=attrgetter('number')):
                self._build_round_panel(round)

    def _build_round_panel(self, round: models.Round):
        round_name = f'round_{round.number}'
        with self.tabs:
            ui.tab(round_name, label=f'Round {round.number}')
        self.add_button.move()
        with self.tab_panels:
            with ui.tab_panel(round_name):
                self.round_frames[round] = RoundFrame(self.client, self.events, self.tournament, round)
        self.tab_panels.set_value(round_name)

    async def create_round(self):
        round = await controller.create_round(self.tournament)
        await round.fetch_related('tables__seats__player', 'scores__player')
        _LOGGER.info(f"Tournament {self.tournament.name}: Round {round.number} created.")
        await self.events.send(EventType.ROUND_CREATED, round)

    async def on_round_created(self, round: models.Round):
        self._build_round_panel(round)
        self.client.notify(f"Round {round.number} created.")

    async def on_player_modified(self, player: models.Player):
        for round_frame in self.round_frames.values():
            round_frame.update_player(player)

    async def on_score_updated(self, score: models.Score):
        round_frame = self.round_frames.get(score.round)
        if round_frame is None:
            return
        round_frame.update_score(score)
        self.client.notify(f"Score of round {score.round.number} for player {score.player.name} updated.")
