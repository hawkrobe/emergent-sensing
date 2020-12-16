from goal_inference import *
from environment import *

p = Player(World(debug = True))
p.turn_pref = 'left'
p.pos = np.array([100,250])
p.angle = 0
p.speed = 0
pos = []
angle = []
speed = []

for i in range(50):
    pos += [p.pos]
    p.go_towards(np.array([100,250]))
    p.update_pos()
    angle += [p.angle]
    speed += [p.speed]

print pos, angle, speed

m = Model(n_samples = 100)
x = [m.observe(pos[i+2], angle[i], angle[i+1], angle[i+2], speed[i+2]) for i in range(len(pos)-2)]

