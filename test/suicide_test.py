import base
import unittest
from bots import *
from rgkit import game
from rgkit.settings import settings


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

    def test_collide_and_stay_out_of_suicide_range(self):
        _, [bot2, bot3] = self.simulate(
            [RobotSuicide, RobotMoveRightAndGuard],
            [(10, 10)], [],
            [(8, 10), (9, 10)], [(8, 10), (9, 10)])

        assert(not self._game.robot_at_loc((10, 10)))
        self.assertEqual(bot2.hp, settings['robot_hp'])
        self.assertEqual(bot3.hp, settings['robot_hp'] - settings['suicide_damage'] / 2)

    def test_collide_and_stay_in_suicide_range(self):
        _, [bot2, bot3] = self.simulate(
            [RobotSuicide, RobotMoveRightAndGuard],
            [(9, 10)], [],
            [(10, 10), (11, 10)], [(10, 10), (11, 10)])

        assert(not self._game.robot_at_loc((9, 10)))
        self.assertEqual(bot2.hp, settings['robot_hp'] - settings['suicide_damage'])
        self.assertEqual(bot3.hp, settings['robot_hp'])

    def test_move_into_suicide_bot(self):
        _, [bot2] = self.simulate(
            [RobotSuicide, RobotMoveLeft],
            [(10, 10)], [],
            [(11, 10)], [(10, 10)])

        self.assertEqual(len(self._game._robots), 1)
        self.assertEqual(bot2.hp, settings['robot_hp'] - settings['suicide_damage'])
