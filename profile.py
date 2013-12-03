import game
import ast
from settings import settings

def make_player(fname):
    with open(fname) as player_code:
        return game.Player(code=player_code.read())

map_data = ast.literal_eval(open('maps/default.py').read())

def run_match(fname1, fname2):
    global settings

    game.init_settings(map_data)
    g = game.Game(make_player(fname1), make_player(fname2), record_turns=True)
    for i in xrange(settings.max_turns):
        g.run_turn()

if __name__ == '__main__':
    run_match('robots/liquid.py', 'robots/liquid.py')
