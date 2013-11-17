import base
import unittest
from .. import game
from ..settings import settings
from bots import *


class SuicideTest(base.BaseTestCase):
    def test_basic_suicide(self):
        _, [bot2] = self.simulate(
            [RobotSuicide, RobotGuard],
            [(10, 10)], [],
            [(11, 10)], [(11, 10)])

        assert(not self._game.robot_at_loc((10, 10)))
        self.assertEqual(bot2.hp, settings['robot_hp'] - settings['suicide_damage'] / 2)

    def test_move_out_of_suicide_range(self):
        _, [bot2] = self.simulate(
            [RobotSuicide, RobotMoveRight],
            [(10, 10)], [],
            [(11, 10)], [(12, 10)])

        assert(not self._game.robot_at_loc((10, 10)))
        self.assertEqual(bot2.hp, settings['robot_hp'])

    def test_move_into_suicide_range(self):
        _, [bot2] = self.simulate(
            [RobotSuicide, RobotMoveLeft],
            [(10, 10)], [],
            [(12, 10)], [(11, 10)])

        assert(not self._game.robot_at_loc((10, 10)))
        self.assertEqual(bot2.hp, settings['robot_hp'] - settings['suicide_damage'])

    def test_try_move_into_into_suicide_range(self):
        _, [bot2, bot3] = self.simulate(
            [RobotSuicide, RobotMoveLeft],
            [(10, 10)], [],
            [(11, 10), (12, 10)], [(11, 10), (12, 10)])

        assert(not self._game.robot_at_loc((10, 10)))
        self.assertEqual(bot2.hp, settings['robot_hp'] - settings['suicide_damage'] - settings['collision_damage'])
        self.assertEqual(bot3.hp, settings['robot_hp'])
