from tortoise import models, fields


class Player(models.Model):
    name = fields.TextField()
