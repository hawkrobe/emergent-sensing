import pandas as pd
import numpy as np
import os, sys
from scipy import stats
import matplotlib.pyplot as plt
import statsmodels.api as sm

from parse import *

sys.path.append("../utils/")
from utils import *

data_dir = '../../out/'
games = []
games += get_games(data_dir, 'experiment')
#games += ['data']
data = get_data(data_dir, games)
data = data[data['n_players'] < 6]

x = data['wait']
y = data['score']

slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

print
print 'regression slope', slope, 'p', p_value


x = sm.add_constant(x)
model = sm.OLS(y,x)
results = model.fit()
print results.summary()


plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

fig, ax = plt.subplots()
ax.margins(0.05)
shapes = [(4,0,0), (3,0,0), (4,0,45), (0,3,0), (3,0,180), (5,1,0)]
i = 0
for n in sorted(list(set(data['n_players']))):
    sub = data[data['n_players'] == n]
    ax.plot(sub['wait'], sub['score'], marker=shapes[i], linestyle='', ms = 10, label = n)
    i += 1
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

plt.xlabel('Wait Time', fontsize=24)
plt.ylabel('Individual Score', fontsize=24)

plt.show()

plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

fig, ax = plt.subplots()
i = 0
sub = data[data['n_players'] == 1]
ax.plot(sub['wait'], sub['score'], marker=shapes[i], linestyle='', ms = 10, label = n)

plt.xlabel('Wait Time', fontsize=24)
plt.ylabel('Individual Score', fontsize=24)

plt.show()
