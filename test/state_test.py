#Embedded file name: /Users/bh/programs/robot/rgkit/test/state_test.py
import base
from bots import *
from rgkit import game
from rgkit.settings import settings

class TestRobotState(base.BaseTestCase):

    def test_save_robot_state(self):
        (bot1, bot2), (bot3, bot4) = self.simulate([RobotSaveState, RobotSaveState], [(9, 9), (9, 10)], [(8, 9), (8, 10)], [(9, 11), (9, 12)], [(8, 11), (8, 12)], turns=5)
        assert bot1
        assert bot2
        assert bot3
        assert bot4
