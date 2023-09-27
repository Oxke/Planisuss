from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider
import mpl_toolkits.axes_grid1
import numpy as np

class Interactive_Animation(FuncAnimation):
    def __init__(self, fig, ax, func, frames=None, init_func=None, fargs=None,
                 save_count=None, mini=0, maxi=100, pos=(0.125, 0.835),
                 interval=500, **kwargs):
        self.pressed = []
        self.i = 0
        self.min=mini
        self.max=maxi
        self.runs = True
        self.forwards = True
        self.fig = fig
        self.ax = ax
        self.tracked = np.array([[]])
        self.func = func
        self.setup(pos)
        self._original_interval = interval
        FuncAnimation.__init__(self,self.fig, self.func, frames=self.play(),
                                           init_func=init_func, fargs=fargs,
                                           save_count=save_count,
                               interval=interval, **kwargs )

    def play(self):
        while self.runs:
            self.i = self.i+self.forwards-(not self.forwards)
            if self.i > self.min and self.i < self.max:
                yield self.i
            else:
                self.stop()
                yield self.i

    def start(self):
        self.runs=True
        self.event_source.start()

    def stop(self, event=None):
        self.runs = False
        self.event_source.stop()

    def forward(self, event=None):
        self.forwards = True
        self.start()
    def backward(self, event=None):
        self.forwards = False
        self.start()
    def oneforward(self, event=None):
        self.forwards = True
        self.onestep()
    def onebackward(self, event=None):
        self.forwards = False
        self.onestep()

    def onestep(self):
        if self.i > self.min and self.i < self.max:
            self.i = self.i+self.forwards-(not self.forwards)
        elif self.i == self.min and self.forwards:
            self.i+=1
        elif self.i == self.max and not self.forwards:
            self.i-=1
        self.func(self.i)
        self.fig.canvas.draw_idle()

    def changespeed(self, val):
        self._interval = self._original_interval / 10**val

    def onclick(self, event):
        if event.inaxes == self.ax[1] and not self.runs:
            self.i = max(0, round(event.xdata))
            self.func(self.i)
            self.fig.canvas.draw_idle()
        elif event.inaxes == self.ax[0] and not self.runs:
            if event.button == 1:
                self.func(self.i, (round(event.ydata), round(event.xdata)))
                self.pressed = [(round(event.ydata), round(event.xdata))]
            elif event.button == 3:
                self.func(self.i, bomb=(round(event.ydata), round(event.xdata)),
                          big=event.dblclick)
                self.fig.canvas.draw_idle()

    def on_move(self, event):
        if self.pressed and event.inaxes == self.ax[0]:
            self.pressed.append((round(event.ydata), round(event.xdata)))

    def on_release(self, event):
        shift = 'shift' in event.modifiers
        self.func(self.i, change_geology=self.pressed, invert=shift)
        self.pressed = []
        self.fig.canvas.draw_idle()

    def on_keypress(self, event):
        if event.key == 'right':
            self.oneforward()
        elif event.key == 'left':
            self.onebackward()
        elif event.key == ' ':
            if self.runs:
                self.stop()
            else:
                self.start()
        elif event.key == 'r':
            self.i = self.func(self.i, track_cancel=True)
            self.fig.canvas.draw_idle()
        elif event.key == 'e':
            self.func(self.i, revive='erbasts')
            self.fig.canvas.draw_idle()
        elif event.key == 'c':
            self.func(self.i, revive='carvizes')
            self.fig.canvas.draw_idle()
        elif event.key == 'enter':
            self.func(self.i, save=True)
            self.fig.canvas.draw_idle()


    def setup(self, pos):
        playerax = self.fig.add_axes([pos[0],pos[1], 0.352, 0.04])
        divider = mpl_toolkits.axes_grid1.make_axes_locatable(playerax)
        bax = divider.append_axes("right", size="80%", pad=0.05)
        sax = divider.append_axes("right", size="80%", pad=0.05)
        fax = divider.append_axes("right", size="80%", pad=0.05)
        ofax = divider.append_axes("right", size="100%", pad=0.05)
        self.button_oneback = Button(playerax, label=u'$\u29CF$')
        self.button_back = Button(bax, label=u'$\u25C0$')
        self.button_stop = Button(sax, label=u'$\u25A0$')
        self.button_forward = Button(fax, label=u'$\u25B6$')
        self.button_oneforward = Button(ofax, label=u'$\u29D0$')
        self.button_oneback.on_clicked(self.onebackward)
        self.button_back.on_clicked(self.backward)
        self.button_stop.on_clicked(self.stop)
        self.button_forward.on_clicked(self.forward)
        self.button_oneforward.on_clicked(self.oneforward)
        speedax = self.fig.add_axes([pos[0],0.08, 0.3527, 0.05])
        self.slider_speed = Slider(speedax, "Animation Speed", -2, 1, valinit=0)
        self.slider_speed.on_changed(self.changespeed)
        conn_click = self.fig.canvas.mpl_connect("button_press_event", self.onclick)
        conn_space = self.fig.canvas.mpl_connect("key_press_event", self.on_keypress)
        conn_release = self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        conn_move = self.fig.canvas.mpl_connect("motion_notify_event", self.on_move)


