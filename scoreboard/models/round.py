from tortoise import models, fields

from scoreboard.models import tournament as tournament_models, table, score


class Round(models.Model):
    number = fields.IntField()

    tournament: fields.ForeignKeyRelation[tournament_models.Tournament] = fields.ForeignKeyField(
        'scoreboard.Tournament',
        related_name='rounds')
    tables: fields.ReverseRelation[table.Table]
    scores: fields.ReverseRelation[score.Score]
