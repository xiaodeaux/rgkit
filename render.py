import Tkinter
import game

class Render:
    def __init__(self, game_inst, settings, block_size=20):
        self._settings = settings
        self._blocksize = block_size
        self._winsize = block_size * self._settings.board_size + 40
        self._game = game_inst
        self._colors = game.Field(self._settings.board_size)
        self._paused = False

        self._master = Tkinter.Tk()
        self._master.title('robot game')

        width = self._winsize
        height = self._winsize + self._blocksize * 7/4
        self._win = Tkinter.Canvas(self._master, width=width, height=height)
        self._win.pack()

        self.prepare_backdrop(self._win)
        self._label = self._win.create_text(
            self._blocksize/2, self._winsize + self._blocksize/2,
            anchor='nw', font='TkFixedFont', fill='white')

        self.create_controls(self._win, width, height)

        self._turn = 1
        self._texts = []
        self._squares = {}

        self.callback()
        self.update()
        self._win.mainloop()

    def change_turn(self, turns):
        self._turn = min(max(self._turn + turns, 1), self._game.turns)
        self.update()

    def toggle_pause(self):
        self._paused = not self._paused
        self._toggleButton.config(text=u'\u25B6' if self._paused else u'\u25FC')

    def create_controls(self, win, width, height):
        def change_turn(turns):
            if not self._paused:
                self.toggle_pause()

            self.change_turn(turns)

        def prev():
            change_turn(-1)

        def next():
            change_turn(+1)

        def restart():
            change_turn((-self._turn)+1)

        def pause():
            self.toggle_pause()

        self._master.bind('<Left>', lambda e: prev())
        self._master.bind('<Right>', lambda e: next())
        self._master.bind('<space>', lambda e: pause())

        frame = Tkinter.Frame()
        win.create_window(width, height, anchor=Tkinter.SE, window=frame)
        self._toggleButton = Tkinter.Button(frame, text=u'\u25B6', command=self.toggle_pause)
        self._toggleButton.pack(side='left')
        prevButton = Tkinter.Button(frame, text='<', command=prev)
        prevButton.pack(side='left')
        nextButton = Tkinter.Button(frame, text='>', command=next)
        nextButton.pack(side='left')
        restartButton = Tkinter.Button(frame, text='<<', command=restart)
        restartButton.pack(side='left')

    def prepare_backdrop(self, win):
        self._win.create_rectangle(0, 0, self._winsize, self._winsize + self._blocksize, fill='#555', width=0)
        self._win.create_rectangle(0, self._winsize, self._winsize, self._winsize + self._blocksize * 7/4, fill='#333', width=0)
        for x in range(self._settings.board_size):
            for y in range(self._settings.board_size):
                self._win.create_rectangle(
                    x * self._blocksize + 21, y * self._blocksize + 21,
                    x * self._blocksize + self._blocksize - 3 + 21, y * self._blocksize + self._blocksize - 3 + 21,
                    fill='black',
                    width=0)

    def draw_square(self, loc, color):
        if self._colors[loc] == color:
            return

        self._colors[loc] = color
        x, y = loc
        item = self._win.create_rectangle(
            x * self._blocksize + 20, y * self._blocksize + 20,
            x * self._blocksize + self._blocksize - 3 + 20,
            y * self._blocksize + self._blocksize - 3 + 20,
            fill=color, width=0)
        # Delete previous square on this location.
        if loc in self._squares:
            self._win.delete(self._squares.pop(loc))
        self._squares[loc] = item

    def draw_text(self, loc, text, color=None):
        x, y = loc
        item = self._win.create_text(
            x * self._blocksize + 30, y * self._blocksize + 25,
            text=text, fill=color)
        self._texts.append(item)

    def update_title(self, turns, max_turns):
        red = len(self._game.history[0][self._turn - 1])
        green = len(self._game.history[1][self._turn - 1])
        self._win.itemconfig(
            self._label, text='Red: %d | Green: %d | Turn: %d/%d' %
            (red, green, turns, max_turns))

    def callback(self):
        if not self._paused:
            self.change_turn(1)

        self._win.after(self._settings.turn_interval, self.callback)

    def update(self):
        self.paint()
        self.update_title(self._turn, self._settings.max_turns)

    def determine_color(self, loc):
        if loc in self._settings.obstacles:
            return '#222'

        botinfo = self.loc_robot_hp_color(loc)
        if botinfo is not None:
            hp, color = botinfo
            maxclr = min(hp, 50)
            colorhex = 5 + maxclr / 5
            return ('#%X00' if color == 0 else '#0%X0') % colorhex

        return 'white'

    def loc_robot_hp_color(self, loc):
        for index, color in enumerate(('red', 'green')):
            for robot in self._game.history[index][self._turn - 1]:
                if robot[0] == loc:
                    return (robot[1], index)
        return None

    def paint(self):
        for item in self._texts:
            self._win.delete(item)
        self._texts = []

        for y in range(self._settings.board_size):
            self.draw_text((y, 0), str(y), 'white')
            self.draw_text((0, y), str(y), 'white')
            for x in range(self._settings.board_size):
                loc = (x, y)
                self.draw_square(loc, self.determine_color(loc))
                botinfo = self.loc_robot_hp_color(loc)
                if botinfo is not None:
                    hp, color = botinfo
                    color = 'white' if hp <= 20 else None
                    self.draw_text(loc, hp, color=color)
