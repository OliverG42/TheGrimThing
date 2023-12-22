class Character():
    def __init__(self, name):
        self.name = name
        self.player_name = None

    def add_name(self, player_name):
        self.player_name = player_name

    def get_night_info(self):
        return False

    def get_day_info(self):
        return False

    def on_nomination(self, nominee):
        return False

    def when_nominated(self, nominator):
        return False