import logging
from operator import attrgetter

from nicegui import ui, Client

from scoreboard import models
from scoreboard.config import config
from scoreboard.gui.event import TournamentEvents, EventType

_LOGGER = logging.getLogger(__name__)

ACTIVE_RULE = {':classes': 'row => row.active? "" : "disabled"'}


class PlayerRow:

    def __init__(self, events: TournamentEvents, tournament: models.Tournament, player: models.player, active: bool):
        self.events = events
        self.tournament = tournament
        self.player = player
        self.active = active
        self.scores = {}
        self.row = {}

        self._build()

    def _build(self):
        self.row |= dict(name=self.player.name, active=self.active)
        self.row |= {f"round_{round.number}": getattr(score, config().tournament.score[0].name)
                     for round, score in self.scores.items()}
        self.update_total_score()

    @property
    def total_score(self):
        return tuple(map(sum, zip(*map(models.Score.get_sort_key, self.scores.values()))))

    def update_player(self, player: models.Player):
        self.player = player
        self.row['name'] = player.name

    def update_total_score(self):
        for field, value in zip(config().tournament.score, self.total_score):
            self.row[field.name] = abs(value)

    def update_score(self, score: models.Score):
        self.scores[score.round] = score
        self.row[f"round_{score.round.number}"] = getattr(score, config().tournament.score[0].name)
        self.update_total_score()

    def enable(self):
        self.row['active'] = True

    def disable(self):
        self.row['active'] = False


class SummaryFrame:

    def __init__(self, client: Client, events: TournamentEvents, tournament: models.Tournament):
        self.client = client
        self.events = events
        self.tournament = tournament
        self.players = set()
        self.players_row: dict[models.Player, PlayerRow] = {}

        self._build()

        self.full_screen_button.on('click', self.toggle_full_screen)

        self.events.register(self.client, EventType.SCORE_UPDATED, self.on_score_updated)
        self.events.register(self.client, EventType.ROUND_CREATED, self.on_round_created)
        self.events.register(self.client, EventType.PLAYER_ADDED, self.on_player_added)
        self.events.register(self.client, EventType.PLAYER_REMOVED, self.on_player_removed)
        self.events.register(self.client, EventType.PLAYER_MODIFIED, self.on_player_modified)

    def _build(self):
        _LOGGER.debug(f"Building {self.__class__} for client {self.client}.")
        columns = [dict(name='name', label='Player Name', field='name', align='left') | ACTIVE_RULE]
        self.players = set(self.tournament.players)
        for round in sorted(self.tournament.rounds, key=attrgetter('number')):
            round_id = f'round_{round.number}'
            columns.append(dict(name=round_id, label=f'Round {round.number}', field=round_id) | ACTIVE_RULE)

            for score in round.scores:
                score.round = round
                player_row = self.get_or_build_player_row(score.player, self.players)
                player_row.update_score(score)

        for field in config().tournament.score:
            columns.append(dict(name=field.name, label=field.label, field=field.name) | ACTIVE_RULE)

        self.table = ui.table(columns=columns, rows=[], title='Leaderboard').classes('w-full')
        with self.table.add_slot('top-right'):
            self.full_screen_button = ui.button(icon='fullscreen').props('flat')

        self.sort_players()

    def get_or_build_player_row(self, player: models.Player, players: set[models.Player]) -> PlayerRow:
        player_row = self.players_row.get(player)
        if player_row is None:
            player_row = PlayerRow(self.events, self.tournament, player, player in players)
            self.players_row[player] = player_row
        return player_row

    def sort_players(self):
        self.table.rows = [player_row.row
                           for player_row in sorted(self.players_row.values(), key=attrgetter('total_score'))]

    async def toggle_full_screen(self):
        self.table.toggle_fullscreen()
        self.full_screen_button.props('icon=fullscreen_exit' if self.table.is_fullscreen else 'icon=fullscreen')

    async def on_score_updated(self, score: models.Score):
        player_row = self.get_or_build_player_row(score.player, self.players)
        player_row.update_score(score)
        self.sort_players()

    async def on_round_created(self, round: models.Round):
        round_id = f'round_{round.number}'
        column = dict(name=round_id, label=f'Round {round.number}', field=round_id) | ACTIVE_RULE
        self.table.columns.insert(round.number, column)
        self.table.update()

    async def on_player_added(self, player: models.Player):
        self.players.add(player)
        player_row = self.players_row.get(player)
        if player_row is None:
            return
        player_row.enable()
        self.table.update()

    async def on_player_removed(self, player: models.Player):
        self.players.remove(player)
        player_row = self.players_row.get(player)
        if player_row is None:
            return
        player_row.disable()
        self.table.update()

    async def on_player_modified(self, player: models.Player):
        player_row = self.players_row.get(player)
        if player_row is None:
            return
        player_row.update_player(player)
        self.table.update()
