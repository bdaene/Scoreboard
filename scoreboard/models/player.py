from tortoise import models, fields


class Player(models.Model):
    name = fields.TextField()
    is_active = fields.BooleanField(default=True)
