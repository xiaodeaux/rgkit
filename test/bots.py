class RobotSuicide:
    def act(self, game):
        return ['suicide']


class RobotGuard:
    def act(self, game):
        return ['guard']


class RobotMoveRight:
    def act(self, game):
        return ['move', (self.location[0] + 1, self.location[1])]


class RobotMoveLeft:
    def act(self, game):
        return ['move', (self.location[0] - 1, self.location[1])]


class RobotMoveInvalid:
    def act(self, game):
        return ['move', (self.location[0] + 1, self.location[1] + 1)]


class RobotMoveInCircle:
    def act(self, game):
        from operator import add

        moves = {0: {0: (1, 0), 1: (0, 1)}, 1: {0: (0, -1), 1: (-1, 0)}}

        dest = tuple(map(add, self.location,
                         moves[self.location[1] % 2][self.location[0] % 2]))

        return ['move', dest]


class RobotMoveInCircleCounterclock:
    def act(self, game):
        from operator import add

        moves = {0: {0: (0, 1), 1: (-1, 0)}, 1: {0: (1, 0), 1: (0, -1)}}

        dest = tuple(map(add, self.location,
                         moves[self.location[1] % 2][self.location[0] % 2]))

        return ['move', dest]


class RobotMoveInCircleCollision:
    def act(self, game):
        from operator import add

        moves = {0: {0: (0, 1), 1: (-1, 0)}, 1: {0: (0, -1), 1: (0, -1)}}

        dest = tuple(map(add, self.location,
                         moves[self.location[1] % 2][self.location[0] % 2]))

        return ['move', dest]
