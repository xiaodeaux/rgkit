from rgkit.settings import settings

class Commander:
    def spawn(self, game):
        return ['Robot'] * settings.spawn_per_player

class Robot:
    def act(self, game):
        return ['guard']
    
class TankRobot:
    def act(self, game):
        return ['guard']
