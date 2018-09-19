import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# Create new Figure and an Axes which fills it.
fig = plt.figure(figsize=(7, 7))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, 1), ax.set_xticks([])
ax.set_ylim(0, 1), ax.set_yticks([])
ax.set_title('click and drag to move sound source')

a = 0.9  # how much new velocity value goes into current vel measure

class SoundSource:
    def __init__(self):
        self.X, self.Y = 0, 0
        self.Xp, self.Yp = 0, 0
        self.Xv, self.Yv = 0, 0
        self.isCoasting = False   
        self.cid = fig.canvas.mpl_connect('motion_notify_event', self)

    def __call__(self, event):
        if event.button != 1:
            self.isCoasting = True
            return

        if event.inaxes != ax: return

        self.isCoasting = False   
        self.updatePosition(event.xdata, event.ydata)
        self.updateVelocity()

    def updateVelocity(self):
        self.Xv = (1-a) * self.Xv + a * (self.X - self.Xp)
        self.Yv = (1-a) * self.Yv + a * (self.Y - self.Yp)
    
    def updatePosition(self, x, y):
        self.Xp, self.Yp = self.X, self.Y
        self.X, self.Y = x, y
        
    def XY(self):
        if self.isCoasting:
            self.updatePosition(self.X + self.Xv, self.Y + self.Yv)
            self.updateVelocity()
        
        return (self.X, self.Y)
        

# Create expanding circle data
growth_rate = 200
n_expd_circles = 50
expd_circles = np.zeros(n_expd_circles, dtype=[('position', float, 2),
                                      ('size',     float, 1),
                                      ('t0',     float, 1),
                                      ('color',    float, 4)])
t = time.time()
expd_circles['t0'] = np.full(n_expd_circles, t)

# Construct the scatter which we will update during animation
# as the soundwaves develop.
scat = ax.scatter(expd_circles['position'][:, 0], expd_circles['position'][:, 1],
                  s=expd_circles['size'], lw=0.5, edgecolors=expd_circles['color'],
                  facecolors='none', marker="o")

soundsource = SoundSource()


def update(frame_number):
    current_index = (frame_number//13) % n_expd_circles

    # Make all colors more transparent as time progresses.
    expd_circles['color'][:, 3] *= 0.99
    expd_circles['color'][:, 3] = np.clip(expd_circles['color'][:, 3], 0, 1)

    # Make all circles bigger.  Square it because scat.set_sizes() expects area not radius.
    t = time.time()
    expd_circles['size'] = ((t-expd_circles['t0']) * growth_rate)**2
    
    expd_circles['position'][current_index] = soundsource.XY()
    expd_circles['size'][current_index] = 0
    expd_circles['t0'][current_index] = time.time()
    expd_circles['color'][current_index] = (0, 0, 1, 1)

    # Update the scatter collection, with the new colors, sizes and positions.
    scat.set_edgecolors(expd_circles['color'])
    scat.set_sizes(expd_circles['size'])
    scat.set_offsets(expd_circles['position'])

    return



# Construct the animation, using the update function as the animation director.
animation = FuncAnimation(fig, update, interval=10)
plt.show()

