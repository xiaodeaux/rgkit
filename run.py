#!/usr/bin/env python2

import argparse
import ast
import itertools
import os

_is_multiprocessing_supported = True
try:
    from multiprocessing import Pool
except ImportError:
    _is_multiprocessing_supported = False  # the OS does not support it. See http://bugs.python.org/issue3770

###
import game
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
parser.add_argument("-A", "--no-animate", action="store_false",
                    default=True,
                    help="Disable animations in rendering.")
parser.add_argument("--game-seed", default='initialseed',
                    help="Appended with game countfor per-match seeds.")
parser.add_argument("--match-seeds", nargs='*',
                    help="Used for random seed of the first matches in order.")

def make_player(fname):
    with open(fname) as player_code:
        return game.Player(player_code.read())

def play(players, match_seed, print_info=True, animate_render=True):
    g = game.Game(*players, record_turns=True, seed=match_seed)
    if print_info:
        print('Match seed: {}'.format(match_seed))
    for i in xrange(settings.max_turns):
        if print_info:
            print (' running turn %d ' % (g.turns + 1)).center(70, '-')
        g.run_turn()

    if print_info:
        # only import render if we need to render the game;
        # this way, people who don't have tkinter can still
        # run headless
        import render

        render.Render(g, game.settings, animate_render)
        print g.history

    return g.get_scores()

def test_runs_sequentially(args):
    players = [make_player(args.usercode1), make_player(args.usercode2)]
    scores = []
    for i in xrange(args.count):
        match_seed = args.game_seed + str(i)
        if args.match_seeds and i < len(args.match_seeds):
            match_seed = args.match_seeds[i]
        scores.append(
            play(players,
                 match_seed,
                 not args.headless,
                 args.no_animate)
        )
        print scores[-1]
    return scores

def task(data):
    usercode1, usercode2, headless, no_animate, match_seed = data
    result = play(
        [
            make_player(usercode1),
            make_player(usercode2)
        ],
        match_seed,
        not headless,
        no_animate,
    )
    print('{0} - seed: {1}'.format(result, match_seed))
    return result

def test_runs_concurrently(args):
    data = []
    for i in xrange(args.count):
        match_seed = args.game_seed + str(i)
        if args.match_seeds and i < len(args.match_seeds):
            match_seed = args.match_seeds[i]
        data.append([
            args.usercode1,
            args.usercode2,
            args.headless,
            args.no_animate,
            match_seed,
        ])
    return Pool().map(task, data, 1)

if __name__ == '__main__':

    args = parser.parse_args()

    map_name = os.path.join(args.map)
    map_data = ast.literal_eval(open(map_name).read())
    game.init_settings(map_data)
    print('Using game seed: {0}'.format(args.game_seed))

    runner = test_runs_sequentially
    if _is_multiprocessing_supported and args.count > 1:
        runner = test_runs_concurrently
    scores = runner(args)

    if args.count > 1:
        p1won = sum(p1 > p2 for p1, p2 in scores)
        p2won = sum(p2 > p1 for p1, p2 in scores)
        print [p1won, p2won, args.count - p1won - p2won]
