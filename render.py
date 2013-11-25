import Tkinter
import game, rg
import time

def millis():
    return int(time.time() * 1000)

def rgb_to_hex(r, g, b, normalized = True):
    if normalized:
        return '#%02x%02x%02x' % (r*255, g*255, b*255)
    else:
        return '#%02x%02x%02x' % (r, g, b)

class RobotSprite:
    def __init__(self, bot, render):
        self.robot = bot
        self.renderer = render
        self.halfupdate = False
        # Tkinter objects
        self.square = None
        self.overlay = None
        self.text = None
        self.animation_offset = (0,0)
        self.location = self.robot.location
    
    def animate(self, delta=0):
        """Animate this sprite
           
           delta is between 0 and 1. it tells us how far along to render (0.5 is halfway through animation)
                this allows animation logic to be separate from timing logic
        """
        delta = max(0, min(delta, 1))
        bot_color = self.compute_color(self.robot.player_id, self.robot.hp)
        self.animation_offset = (0,0)
        if self.robot.action[0] == 'move':
            # if normal move, start at bot location and move to next location
            # (note that first half of all move animations is the same)
            if delta < 0.5 or self.robot.location_next == self.robot.action[1]:
                x, y = self.robot.location
                self.location = self.robot.location
                tx, ty = self.robot.action[1]
            # if we're halfway through this animation AND the movement didn't succeed, reverse it (bounce back)
            else:
                # starting where we wanted to go
                x, y = self.robot.action[1]
                self.location = self.robot.action[1]
                # and ending where we are now
                tx, ty = self.robot.location
            dx = tx - x
            dy = ty - y
            off_x = dx*delta*self.renderer._blocksize
            off_y = dy*delta*self.renderer._blocksize
            self.animation_offset = (off_x, off_y)
        elif self.robot.action[0] == 'attack':
            pass
        elif self.robot.action[0] == 'guard':
            pass
        elif self.robot.action[0] == 'suicide':
            pass
        elif self.robot.action[0] == 'spawn':
            pass
        elif self.robot.action[0] == 'dead':
            pass
        self.draw_bot(delta)
        self.draw_bot_hp(delta)

    def compute_color(self, player, hp):
        max_hp = float(self.renderer._settings.robot_hp)
        r,g,b = self.renderer._settings.colors[player]
        hp = float(hp)
        r *= hp / max_hp
        g *= hp / max_hp
        b *= hp / max_hp
        return rgb_to_hex(r, g, b)
    
    def draw_bot(self, delta):
        x, y = self.renderer.grid_to_xy(self.location)
        rx, ry = self.renderer.square_bottom_corner((x,y))
        ox, oy = self.animation_offset
        color = self.compute_color(self.robot.player_id, self.robot.hp)
        if self.square is None:
            self.square = self.renderer.draw_grid_square(self.location, color)
        self.renderer._win.coords(self.square, (x+ox, y+oy, rx+ox, ry+oy))

    def draw_bot_hp(self, delta):
        x, y = self.renderer.grid_to_xy(self.location)
        ox, oy = self.animation_offset
        tex_color = "#888"
        val = self.robot.hp if delta < 0.5 else self.robot.hp_next
        if self.text is None or (delta >= 0.5 and not self.halfupdate):
            self.text = self.renderer.draw_text(self.location, val, tex_color)
            self.halfupdate = True
        self.renderer._win.coords(self.text, (x+ox+10, y+oy+10))

    def clear(self):
        self.renderer.remove_object(self.square)
        self.renderer.remove_object(self.overlay)
        self.renderer.remove_object(self.text)

class Render:
    def __init__(self, game_inst, settings, block_size=25):
        self._settings = settings
        self._blocksize = block_size
        self._winsize = block_size * self._settings.board_size + 40
        self._game = game_inst
        self._paused = True

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
                
        # Animation stuff (also see #render heading in settings.py)
        self._sprites = []
        self._t_paused = 0
        self._t_frame_start = 0
        self._t_next_frame = 0
        self.update_frame_timing()

        self.draw_background()
        self.update_title(self._turn, self._settings.max_turns)
        self.update_sprites_new_turn()
        self.paint()
        self.callback()
        self._win.mainloop()
    
    def remove_object(self, obj):
        if obj is not None:
            self._win.delete(obj)

    def change_turn(self, turns):
        self._turn = min(max(self._turn + turns, 1), self._game.turns)
        self.update_title(self._turn, self._settings.max_turns)
        self.update_sprites_new_turn()
        self.paint()

    def toggle_pause(self):
        self._paused = not self._paused
        print "paused" if self._paused else "unpaused"
        self._toggle_button.config(text=u'\u25B6' if self._paused else u'\u25FC')
        now = millis()
        if self._paused:
            self._t_paused = now
        else:
            if self._t_paused != 0:
                self.update_frame_timing(now - (self._t_paused - self._t_frame_start))
            else:
                self.update_frame_timing(now)

    def update_frame_timing(self, tstart=None):
        if tstart is None:
            tstart = millis()
        self._t_frame_start = tstart
        self._t_next_frame = tstart + self._settings.turn_interval

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
        self._toggle_button = Tkinter.Button(frame, text=u'\u25B6', command=self.toggle_pause)
        self._toggle_button.pack(side='left')
        prev_button = Tkinter.Button(frame, text='<', command=prev)
        prev_button.pack(side='left')
        next_button = Tkinter.Button(frame, text='>', command=next)
        next_button.pack(side='left')
        restart_button = Tkinter.Button(frame, text='<<', command=restart)
        restart_button.pack(side='left')

    def prepare_backdrop(self, win):
        self._win.create_rectangle(0, 0, self._winsize, self._winsize + self._blocksize, fill='#555', width=0)
        self._win.create_rectangle(0, self._winsize, self._winsize, self._winsize + self._blocksize * 7/4, fill='#333', width=0)
        for x in range(self._settings.board_size):
            for y in range(self._settings.board_size):
                self.draw_grid_square((x,y), "white" if ("normal" in rg.loc_types((x,y))) else "black")

    def draw_grid_square(self, loc, color):
        x, y = self.grid_to_xy(loc)
        rx, ry = self.square_bottom_corner((x,y))
        item = self._win.create_rectangle(
            x, y,
            rx, ry,
            fill=color, width=0)
        return item

    def draw_text(self, loc, text, color=None):
        x, y = self.grid_to_xy(loc)
        item = self._win.create_text(
            x+10, y+10,
            text=text, font='TkFixedFont', fill=color)
        return item

    def update_title(self, turns, max_turns):
        red = len(self._game.history[0][self._turn - 1])
        green = len(self._game.history[1][self._turn - 1])
        self._win.itemconfig(
            self._label, text='Red: %d | green: %d | Turn: %d/%d' %
            (red, green, turns, max_turns))

    def tick(self):
        now = millis()
        # check if frame-update
        if not self._paused:
            if now >= self._t_next_frame:
                self.change_turn(1)
                if self._turn >= self._settings.max_turns:
                    self.toggle_pause()
                else:
                    self.update_frame_timing(self._t_next_frame)
            subframe = float(now - self._t_frame_start) / float(self._settings.turn_interval)
            self.paint(subframe)

    def callback(self):
        self.tick()
        self._win.after(int(1000.0 / self._settings.FPS), self.callback)

    def determine_bg_color(self, loc):
        if loc in self._settings.obstacles:
            return '#222'
        return 'white'

    def get_robot(self, loc):
        for index, color in enumerate(('red', 'green')):
            for robot in self._game.history[index][self._turn - 1]:
                if robot[0] == loc:
                    if len(robot) == 3:
                        return RobotData(loc, robot[1], index, robot[2])
                    else:
                        return RobotData(loc, robot[1], index, ['guard'])
        return None

    def draw_background(self):
        # draw squares
        for y in range(self._settings.board_size):
            for x in range(self._settings.board_size):
                loc = (x, y)
                self.draw_grid_square(loc, self.determine_bg_color(loc))
        # draw text labels
        for y in range(self._settings.board_size):
            self.draw_text((y, 0), str(y), '#888')
            self.draw_text((0, y), str(y), '#888')
    
    def update_sprites_new_turn(self):
        for sprite in self._sprites:
            sprite.clear()
        self._sprites = []
        
        board_activity = self._game.get_recent_activity(self._turn)
        for y in range(self._settings.board_size):
            for x in range(self._settings.board_size):
                loc = (x, y)
                bot_data = board_activity[loc]
                if bot_data is not None:
                    self._sprites.append(RobotSprite(bot_data, self))

    def paint(self, subframe=0):
        for sprite in self._sprites:
            sprite.animate(subframe)
    
    def grid_to_xy(self, loc):
        x,y = loc
        return  (x * self._blocksize + 20, y * self._blocksize + 20)
    
    def square_bottom_corner(self, square_topleft):
        x,y = square_topleft
        return (x + self._blocksize - 3, y + self._blocksize - 3)