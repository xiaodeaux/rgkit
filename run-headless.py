import game
import sys
import os
from settings import settings

def make_player(fname):
    return game.Player(open(fname).read())

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'usage: python run.py <usercode1.py> <usercode2.py> [<map file>]'
        sys.exit()

    players = [make_player(x) for x in sys.argv[1:3]]
    g = game.Game(*players, record_turns=False)

    map_name = os.path.join(os.path.dirname(__file__), 'maps/default.py')
    if len(sys.argv) > 3:
        map_name = sys.argv[3]

    game.init_settings(map_name)
    for i in range(settings.max_turns):
        g.run_turn()

    scores = g.get_scores()
    print scores[0], scores[1]
