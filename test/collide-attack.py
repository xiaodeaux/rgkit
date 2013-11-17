import os
from .. import rgkit.game

class Player1:
    def act(self, game):
        return ['attack', (9, 9)]

class Player2:
    def act(self, game):
        if self.location == (9, 9):
            return ['guard']
        return ['move', (9, 9)]

if __name__ == '__main__':
    map_file = os.path.join(os.path.dirname(__file__), 'maps/test/collide-attack.py')
    map_data = ast.literal_eval(open(map_file).read())
    game.init_settings(map_data)

    g = game.Game(
        game.Player(robots={'Robot': Player1()}),
        game.Player(robots={'Robot': Player2()}),
        record_turns=False)

    for r in g._robots:
        print r.player_id, r.location, r.hp

    g.run_turn()

    for r in g._robots:
        print r.player_id, r.location, r.hp
