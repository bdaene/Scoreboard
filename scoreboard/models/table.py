from tortoise import models, fields

from scoreboard.models import round, player


class Table(models.Model):
    number = fields.IntField()

    round: fields.ForeignKeyRelation['round.Round'] = fields.ForeignKeyField('scoreboard.Round',
                                                                             related_name='tables')
    seats: fields.ReverseRelation['Seat']


class Seat(models.Model):
    number = fields.IntField()

    table: fields.ForeignKeyRelation['Table'] = fields.ForeignKeyField('scoreboard.Table', related_name='seats')
    player: fields.ForeignKeyRelation['player.Player'] = fields.ForeignKeyField('scoreboard.Player')
