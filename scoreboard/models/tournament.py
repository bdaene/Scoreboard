from tortoise import models, fields
from scoreboard.models import player, round


class Tournament(models.Model):
    name = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    players: fields.ManyToManyRelation['player.Player'] = fields.ManyToManyField('scoreboard.Player')
    rounds: fields.ReverseRelation['round.Round']
