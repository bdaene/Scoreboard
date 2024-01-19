from tortoise import models, fields

from scoreboard.config import config
from scoreboard.models import round, player


class Score(models.Model):
    for score_field in config().tournament.score:
        locals()[score_field.name] = fields.IntField(default=0)

    round: fields.ForeignKeyRelation['round.Round'] = fields.ForeignKeyField('scoreboard.Round',
                                                                             related_name='scores')
    player: fields.ForeignKeyRelation['player.Player'] = fields.ForeignKeyField('scoreboard.Player')

    class Meta:
        ordering = [('-' if score_field.descending else '') + score_field.name
                    for score_field in config().tournament.score]

    def __lt__(self, other: 'Score') -> bool:
        for score_field in config().tournament.score:
            my_value, other_value = getattr(self, score_field.name), getattr(other, score_field.name)
            if my_value == other_value:
                continue
            if score_field.descending:
                return my_value > other_value
            else:
                return my_value < other_value
        return False
