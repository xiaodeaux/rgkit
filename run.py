#!python
import os
import ast
import argparse
###
import game
import render
from settings import settings

parser = argparse.ArgumentParser(description="Robot game execution script.")
parser.add_argument("usercode1",
                    help="File containing first robot class definition.")
parser.add_argument("usercode2",
                    help="File containing second robot class definition.")
parser.add_argument("-m", "--map", help="User-specified map file.",
                    default='maps/default.py')
parser.add_argument("-H", "--headless", action="store_true",
                    default=False,
                    help="Disable rendering game output.")
args = parser.parse_args()

def make_player(fname):
    return game.Player(open(fname).read())

if __name__ == '__main__':

    map_name = os.path.join(os.path.dirname(__file__), args.map)
    map_data = ast.literal_eval(open(map_name).read())
    game.init_settings(map_data)

    players = [game.Player(open(args.usercode1).read()),
               game.Player(open(args.usercode2).read())]
    g = game.Game(*players, record_turns=True)
    for i in range(settings.max_turns):
        print (' running turn %d ' % (g.turns + 1)).center(70, '-')
        g.run_turn()
    if not args.headless:
        render.Render(g, game.settings)
        print g.history
    else:
        print g.get_scores()
