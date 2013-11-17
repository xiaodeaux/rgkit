robot_move_right = """
class Robot:
    def act(self, game):
        return ['move', (self.location[0] + 1, self.location[1])]
"""


robot_move_left = """
class Robot:
    def act(self, game):
        return ['move', (self.location[0] - 1, self.location[1])]
"""


robot_move_invalid = """
class Robot:
    def act(self, game):
        return ['move', (self.location[0] + 1, self.location[1] + 1)]
"""


robot_move_in_circle = """
class Robot:
    def act(self, game):
        from operator import add

        moves = {0: {0: (1, 0), 1: (0, 1)}, 1: {0: (0, -1), 1: (-1, 0)}}

        dest = tuple(map(add, self.location,
                         moves[self.location[1] % 2][self.location[0] % 2]))

        return ['move', dest]
"""


robot_move_in_circle_counterclock = """
class Robot:
    def act(self, game):
        from operator import add

        moves = {0: {0: (0, 1), 1: (-1, 0)}, 1: {0: (1, 0), 1: (0, -1)}}

        dest = tuple(map(add, self.location,
                         moves[self.location[1] % 2][self.location[0] % 2]))

        return ['move', dest]
"""


robot_move_in_circle_collision = """
class Robot:
    def act(self, game):
        from operator import add

        moves = {0: {0: (0, 1), 1: (-1, 0)}, 1: {0: (0, -1), 1: (0, -1)}}

        dest = tuple(map(add, self.location,
                         moves[self.location[1] % 2][self.location[0] % 2]))

        return ['move', dest]
"""
