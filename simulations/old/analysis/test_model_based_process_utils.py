
from model_based_process_utils import *
from environment import *

start_pos = [[0.0,0.0], [100.0,100.0], [0.0,0.0], [0.0,0.0], [100.0,100.0], [100.0,100.0]]

pos = []
angle = []
speed = []

for j in range(len(start_pos)):
    
    pos += [[]]
    angle += [[]]
    speed += [[]]
    
    p = Player(World(debug = True))
    
    p.pos = start_pos[j]
    p.angle = 135
    p.speed = 2.125
    
    for i in range(24):
        
        p.go_towards(np.array([100.0,100.0]))
        p.update_pos()
        pos[j] += [p.pos]
        angle[j] += [p.angle]
        speed[j] += [p.speed]

pos[-1] = pos[-1][:-4]
angle[-1] = angle[-1][:-4]
speed[-1] = speed[-1][:-4]

ticks = [i for x in pos for i in range(len(x))]
pids = [j for i in range(len(pos)) for j in [i]*len(pos[i])]
x_pos = [pos[i][j][0] for i in range(len(pos)) for j in range(len(pos[i]))]
y_pos = [pos[i][j][1] for i in range(len(pos)) for j in range(len(pos[i]))]
speeds = [speed[i][j] for i in range(len(pos)) for j in range(len(pos[i]))]
angles = [angle[i][j] for i in range(len(pos)) for j in range(len(pos[i]))]
bg = [1 if abs(pos[i][j][0] - 100) < 10 else 0 for i in range(len(pos)) for j in range(len(pos[i]))]

p = Processor(pd.DataFrame({'tick':ticks,'pid':pids,'x_pos':x_pos,'y_pos':y_pos,'velocity':speeds,'angle':angles,'bg_val':bg}),{})
success, df = p.process_data()

print df.iloc[60,]
print df.iloc[61,]
print df.iloc[62,]

i = 1
x = df.iloc[60 + i,]

samples = np.random.multivariate_normal(np.array(x[['goal_m0','goal_m1']]), np.array([[x['goal_v00'],x['goal_v01']],[x['goal_v01'],x['goal_v11']]]), size = 10000)
pd.DataFrame(samples).to_csv('tmp-1',index=False)
pd.DataFrame(goal_models[i].samples).to_csv('tmp-2',index=False)

x = df[df['tick'] == 23].iloc[0]

samples = np.random.multivariate_normal(np.array(x[['pos_m0','pos_m1']]), np.array([[x['pos_v00'],x['pos_v01']],[x['pos_v01'],x['pos_v11']]]), size = 10000)
pd.DataFrame(samples).to_csv('tmp-1',index=False)
pd.DataFrame(goal_models[i].samples).to_csv('tmp-2',index=False)
