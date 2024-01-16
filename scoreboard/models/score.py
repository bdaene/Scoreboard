from tortoise import models, fields

from scoreboard.config import config
from scoreboard.models import round, player

ORDER = tuple((order.startswith('-'), order.removeprefix('-')) for order in config().score.order)


class Score(models.Model):
    for _, name in ORDER:
        locals()[name] = fields.IntField(default=0)

    round: fields.ForeignKeyRelation['round.Round'] = fields.ForeignKeyField('scoreboard.Round',
                                                                             related_name='scores')
    player: fields.ForeignKeyRelation['player.Player'] = fields.ForeignKeyField('scoreboard.Player')

    class Meta:
        ordering = [('-' if descending else '') + name for descending, name in ORDER]

    def __lt__(self, other: 'Score') -> bool:
        for descending, name in ORDER:
            my_value, other_value = getattr(self, name), getattr(other, name)
            if my_value == other_value:
                continue
            if descending:
                return my_value > other_value
            else:
                return my_value < other_value
        return False
