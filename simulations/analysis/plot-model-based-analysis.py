import pickle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

in_dir = '../../model-processed-results/'

true = 'data'
syn = 'synthetic-data'

subsets = ['pos-no-like-none-all-all',
           'pos-like-weighted-none-all-all',
           'goal-no-like-none-all-all',
           'goal-like-weighted-none-all-all']


with open(in_dir + true + '.out') as f:
    data = pickle.load(f)
with open(in_dir + syn + '.out') as g:
    nominal = pickle.load(g)

values = []
ns = []
games = []
subs = []

for subset in subsets:

    for game in data:

        players = data[game][subset].keys()
        syn_players = nominal[game][subset].keys()
        assert len(players) == len(syn_players)

        n = len(players)

        if n == 6:
             n = 5

        for i in range(len(players)):

            val_p = data[game][subset][players[i]]
            val_q = nominal[game][subset][syn_players[i]]

            values += [val_p - val_q]
            ns += [n]
            games += [game]
            subs += [subset]

df = pd.DataFrame({'subset':subs,'game':games,'n_players':ns,'value':values})

sns.set(font = 'serif', context = 'poster', style = 'white')
sns.despine()

g = sns.factorplot('n_players', 'value', markers = ['o', 's'], linestyles = ['-','--'], data = df, kind='point', dodge = 0.15, x_order = sorted(set(df['n_players'])), col = 'subset')

plt.plot([0, 7], [0, 0], 'k-', lw=2)

fig = plt.gcf()

fig.savefig('../../plots/values.pdf')

