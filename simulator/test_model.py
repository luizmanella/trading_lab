from datetime import datetime, timedelta
from model import Model


class DummyModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.last_position = dict()
        self.made_last_position = False

    def run(self):
        if not self.made_last_position:
            for security in self.security_universe:
                self.last_position[security] = -1
            self.made_last_position = True

        portfolio = dict()
        for security in self.security_universe:
            if self.last_position[security] == 1:
                portfolio[security] = -1
                self.last_position[security] = -1
            elif self.last_position[security] == -1:
                portfolio[security] = 1
                self.last_position[security] = 1
        return portfolio


class DummyModel2(Model):
    def __init__(self):
        Model.__init__(self)

    def run(self):
        portfolio = dict()
        for security in self.security_universe:
            portfolio[security] = -1
        return portfolio