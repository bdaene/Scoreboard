from nicegui import ui


class Event:
    def __init__(self, notification: str):
        self.notification = notification
        self.callbacks = []

    def register(self, callback):
        self.callbacks.append(callback)

    def send(self, **kwargs):
        ui.notify(self.notification.format(**kwargs))
        for callback in self.callbacks:
            callback(**kwargs)


class Events:
    def __init__(self):
        self.player_added = Event('Player {player.name} added.')
        self.player_removed = Event('Player {player.name} removed.')
        self.player_modified = Event('Player {player.name} modified.')
        self.round_created = Event('Round {round.number} created.')
        self.score_updated = Event('Score of player {score.player.name} for round {score.round.number} updated.')
