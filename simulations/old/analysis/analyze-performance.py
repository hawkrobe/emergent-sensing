import pandas as pd
import numpy as np
from scipy import stats
import os, sys
import statsmodels.api as sm

sys.path.append("../utils/")
from utils import *

data_dir = '../../out/'
out_dir = '../../data/'
games = []
games += get_games(data_dir, 'experiment')
#games += ['tmp']

subset = True

data = get_data(data_dir, games)
#data = data[data['n_players'] < 6]
if subset:
    #data = data[data['noise'] == '2-1en01']
    #data = data[data['difficulty'] == '2en01']
    data = data[data['difficulty'] == '1en01']

indiv = []
for index, row in data.iterrows():
    indiv += [(row['pid'],row['game'],row['n_players'],row['score'])]

indiv = sorted(indiv, key=lambda tup: tup[-1])

print
print 'low performing individuals'
for p in indiv[:10]:
    print p

print
print 'high performing individuals'
for p in indiv[-10:]:
    print p

teams = []
for g in set(data['game']):
    mu = np.mean(data[data['game'] == g]['score'])
    n = list(data[data['game'] == g]['n_players'])[0]
    teams += [(g,n,mu)]

teams = sorted(teams, key=lambda tup: tup[-1])
    
print
print 'low performing groups'
for g in teams[:10]:
    print g

print
print 'high performing groups'
for g in teams[-10:]:
    print g
    
print
print 'performance'
for n in set(data['n_players']):
    bs = data[data['n_players'] == n]['score']
    print n, np.mean(bs), np.std(bs), len(bs), 2*np.std(bs)/np.sqrt(len(bs))

x = data['n_players']
y = data['score']
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

print
print 'regression slope:', slope, ', p:',  p_value

x = sm.add_constant(x)
model = sm.OLS(y,x)
results = model.fit()
print results.summary()

data.to_csv(out_dir + 'individual-data.csv', header = True, index = False)

