import Tkinter
import game


class Render:
    def __init__(self, game_inst, settings, block_size=25):
        self._settings = settings
        self._blocksize = block_size
        self._winsize = block_size * self._settings.board_size + 40
        self._game = game_inst
        self._colors = game.Field(self._settings.board_size)
        self._paused = False

        self._master = Tkinter.Tk()
        self._master.title('Robot Game')

        width = self._winsize
        height = self._winsize + self._blocksize * 11/4
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
        self._highlighted = None
        self._highlightedtarget = None

        self.callback()
        self.update()
        self._win.mainloop()

    def change_turn(self, turns):
        self._turn = min(max(self._turn + turns, 1), self._game.turns)
        self._highlightedtarget = None
        self.update()

    def toggle_pause(self):
        self._paused = not self._paused
        self._toggle_button.config(text=u'\u25B6' if self._paused else u'\u25FC')

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

        def onclick(event):
            x = (event.x - 20) / self._blocksize
            y = (event.y - 20) / self._blocksize
            loc = (x, y)
            if loc[0] >= 0 and loc[1] >= 0 and loc[0] < self._settings.board_size and loc[1] < self._settings.board_size:
                if loc == self._highlighted:
                    self._highlighted = None
                else:
                    self._highlighted = loc
                self._highlightedtarget = None
                self.update()

        self._master.bind("<Button-1>", lambda e: onclick(e))
        self._master.bind('<Left>', lambda e: prev())
        self._master.bind('<Right>', lambda e: next())
        self._master.bind('<space>', lambda e: pause())

        frame = Tkinter.Frame()
        win.create_window(width, height, anchor=Tkinter.SE, window=frame)
        self._toggle_button = Tkinter.Button(frame, text=u'\u25B6', command=self.toggle_pause)
        self._toggle_button.pack(side='left')
        prev_button = Tkinter.Button(frame, text='<', command=prev)
        prev_button.pack(side='left')
        next_button = Tkinter.Button(frame, text='>', command=next)
        next_button.pack(side='left')
        restart_button = Tkinter.Button(frame, text='<<', command=restart)
        restart_button.pack(side='left')
        self._time_slider = Tkinter.Scale(frame, from_=-50, to_=50, orient=Tkinter.HORIZONTAL, borderwidth=0)
        self._time_slider.pack()

    def prepare_backdrop(self, win):
        self._win.create_rectangle(0, 0, self._winsize, self._winsize + self._blocksize, fill='#555', width=0)
        self._win.create_rectangle(0, self._winsize, self._winsize, self._winsize + self._blocksize * 15/4, fill='#333', width=0)
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
            x * self._blocksize + 30, y * self._blocksize + 30,
            text=text, font='TkFixedFont', fill=color)

        self._texts.append(item)

    def update_title(self, turns, max_turns):
        red = len(self._game.history[0][self._turn - 1])
        green = len(self._game.history[1][self._turn - 1])
        info = ''
        lastaction = ''
        if self._highlighted is not None:
            squareinfo = self.get_square_info(self._highlighted)
            if 'obstacle' in squareinfo:
                info = 'Obstacle'
            elif 'bot' in squareinfo:
                botinfo = squareinfo[1]
                hp = botinfo[0]
                team = botinfo[1]
                info = '%s Bot: %d HP' % (['Red', 'Green'][team], hp)
                action = self._game.actionat[self._turn - 1].get(self._highlighted)
                if action:
                    name = action['name']
                    lastaction += 'Last Action: %s' % (name,)
                    target = action['target']
                    if target is not None:
                        self._highlightedtarget = target
                        self.paint()
                        lastaction += ' to %s' % (target,)

        lines = [
            'Red: %d | Green: %d | Turn: %d/%d' % (red, green, turns, max_turns),
            'Highlighted: %s; %s' % (self._highlighted, info),
            lastaction
        ]
        self._win.itemconfig(
            self._label, text='\n'.join(lines))

    def get_square_info(self, loc):
        if loc in self._settings.obstacles:
            return ['obstacle']

        botinfo = self.loc_robot_hp_color(loc)
        if botinfo is not None:
            return ['bot', botinfo]

        return ['normal']

    def callback(self):
        v = self._time_slider.get()
        v = -v
        if v > 0:
            v = v * 20
        delay = self._settings.turn_interval + v
        if not self._paused:
            self.change_turn(1)

        self._win.after(delay, self.callback)

    def update(self):
        self.paint()
        self.update_title(self._turn, self._settings.max_turns)

    def determine_color(self, loc):
        if loc == self._highlighted:
            return "#aaa"
        if loc == self._highlightedtarget:
            return "#aaf"

        squareinfo = self.get_square_info(loc)
        if 'obstacle' in squareinfo:
            return '#222'

        if 'bot' in squareinfo:
            hp, color = squareinfo[1]
            rgb = [90, 90, 90]
            # red or green?
            rgb[color] += 35
            maxclr = min(hp, 50)
            for i, val in enumerate(rgb):
                rgb[i] = val + (100 - maxclr * 1.75)

            return '#%X%X%X' % tuple(rgb)

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
            self.draw_text((y, 0), str(y), '#888')
            self.draw_text((0, y), str(y), '#888')
            for x in range(self._settings.board_size):
                loc = (x, y)
                self.draw_square(loc, self.determine_color(loc))
                botinfo = self.loc_robot_hp_color(loc)
                if botinfo is not None:
                    hp, color = botinfo
                    text_color = '#220808' if color == 0 else '#220808'
                    self.draw_text(loc, hp, color=text_color)
