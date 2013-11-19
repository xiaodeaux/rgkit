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

class RobotSaveState(RobotMoveLeft):
    def act(self, game):
        if hasattr(self, 'do_not_move') and self.do_not_move:
            return ['guard']
        self.do_not_move = True
        return RobotMoveLeft.act(self, game)

class RobotMoveUp:
    def act(self, game):
        return ['move', (self.location[0], self.location[1] - 1)]


class RobotMoveInvalid:
    def act(self, game):
        return ['move', (self.location[0] + 1, self.location[1] + 1)]


class RobotMoveRightAndGuard:
    def act(self, game):
        if (self.location[0] % 2 == 0):
            return ['move', (self.location[0] + 1, self.location[1])]
        else:
            return ['guard']


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
