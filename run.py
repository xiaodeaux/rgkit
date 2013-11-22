#!/usr/bin/env python2

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
                    default=os.path.join(os.path.dirname(__file__), 'maps/default.py'))
parser.add_argument("-H", "--headless", action="store_true",
                    default=False,
                    help="Disable rendering game output.")
parser.add_argument("-c", "--count", type=int,
                    default=1,
                    help="Game count, default: 1")

def make_player(fname):
    with open(fname) as player_code:
        return game.Player(player_code.read())

def play(players, print_info=True):
    g = game.Game(*players, record_turns=True)
    for i in xrange(settings.max_turns):
        if print_info:
            print (' running turn %d ' % (g.turns + 1)).center(70, '-')
        g.run_turn()

    if print_info:
        render.Render(g, game.settings)
        print g.history

    return g.get_scores()

if __name__ == '__main__':

    args = parser.parse_args()

    map_name = os.path.join(args.map)
    map_data = ast.literal_eval(open(map_name).read())
    game.init_settings(map_data)

    players = [make_player(args.usercode1),
               make_player(args.usercode2)]

    scores = []

    for i in xrange(args.count):
        scores.append(play(players, not args.headless))
        print scores[-1]

    if args.count > 1:
        p1won = sum(p1 > p2 for p1, p2 in scores)
        p2won = sum(p2 > p1 for p1, p2 in scores)
        print [p1won, p2won, args.count - p1won - p2won]
