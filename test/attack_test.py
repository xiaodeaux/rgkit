import base
from bots import *
from rgkit import game
from rgkit.settings import settings

class TestAttack(base.BaseTestCase):
    def test_attack_with_floating_point_location(self):
        [bot1], [bot2] = self.simulate(
            [RobotAttackRightWithFloatingLocation, RobotMoveLeft],
            [(10, 10)], [(10, 10)],
            [(12, 10)], [(11, 10)])

        assert(bot1)
        assert(bot2.hp < settings['robot_hp'])

    def test_attack_with_invalid_tuple_length(self):
        [bot1], _ = self.simulate(
            [RobotAttackWithInvalidLocation, RobotGuard],
            [(10, 10)], [(10, 10)],
            [], [])

        assert(bot1)
        self.assertEqual(self._game.history[0][0][0][2], ['guard'])
