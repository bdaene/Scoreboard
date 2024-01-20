from nicegui import ui

from scoreboard import models
from scoreboard.config import config
from scoreboard.gui.utils import Events, tuples_sum


async def build(current_tournament: models.Tournament, events: Events):
    active_rule = {':classes': 'row => row.active? "" : "disabled"'}
    players_scores = {}

    columns = [dict(name='name', label='Player Name', field='name', align='left') | active_rule, ]

    async for round in current_tournament.rounds.all():
        round_id = f'round_{round.number}'
        columns.append(dict(name='round_id', label=f'Round {round.number}', field=round_id) | active_rule)
        async for score in round.scores.all():
            players_scores.setdefault(await score.player.get(), {})[round_id] = score

    tournament_players = set(await current_tournament.players.all())

    score_config = config().tournament.score
    for field_config in score_config:
        columns.append(dict(name=field_config.name, label=field_config.label, field=field_config.name) | active_rule)

    def get_total(scores: dict[str, models.Score]) -> tuple:
        return tuples_sum(map(models.Score.get_sort_key, scores.values()))

    def build_player_row(player: models.Player, scores: dict[str, models.Score]) -> dict:
        total_score = get_total(scores)
        row = dict(name=player.name, active=player in tournament_players, total_score=total_score)
        row |= {round_id: getattr(score, score_config[0].name)
                for round_id, score in scores.items()}
        for field_config, score in zip(score_config, total_score):
            row[field_config.name] = abs(score)
        return row

    rows = {player: build_player_row(player, players_scores[player])
            for player, scores in sorted(players_scores.items(), key=lambda player_scores: get_total(player_scores[1]))}

    table = ui.table(columns=columns, rows=list(rows.values()), title='Leaderboard').classes('w-full')
    with table.add_slot('top-right'):
        async def toggle_full_screen():
            table.toggle_fullscreen()
            button.props('icon=fullscreen_exit' if table.is_fullscreen else 'icon=fullscreen')

        button = ui.button(icon='fullscreen', on_click=toggle_full_screen).props('flat')

    def round_created(round: models.Round):
        round_id = f'round_{round.number}'
        column = dict(name='round_id', label=f'Round {round.number}', field=round_id) | active_rule
        columns.insert(round.number, column)
        table.columns = columns

    events.round_created.register(round_created)

    def player_removed(player: models.Player):
        tournament_players.remove(player)
        rows[player]['active'] = False
        table.update()

    events.player_removed.register(player_removed)

    def player_added(player: models.Player):
        tournament_players.add(player)
        if player in rows:
            rows[player]['active'] = True
            table.update()

    events.player_added.register(player_added)

    def player_modified(player: models.player):
        if player in rows:
            rows[player]['name'] = player.name
            table.update()

    events.player_modified.register(player_modified)

    def score_updated(score: models.Score):
        round_id = f'round_{score.round.number}'
        player = score.player
        scores = players_scores.setdefault(player, {})
        scores[round_id] = score
        rows[player] = build_player_row(player, scores)

        table.rows = [rows[player] for player in sorted(rows, key=lambda p: get_total(players_scores[p]))]

    events.score_updated.register(score_updated)
