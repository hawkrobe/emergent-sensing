
import numpy as np
import pandas as pd

import statsmodels.api as sm 
import statsmodels.formula.api as smf

def get_results(data, verbose = True):
    
    print('Analyzing Individual Score')
    
    md = smf.mixedlm("score ~ n_players + noise", data, groups=data["game"]) 
    mdf = md.fit() 
    if verbose:
        print(mdf.summary())

    noises = []
    game_ids = sorted(list(set(data['game'])))
    for g in game_ids:
        noises += [(data.loc[data['game'] == g,'noise']).iloc[0]]

    game_df_max = []

    comps = {}
    reps = 10
    for n in range(1,7):
        comps[n] = {}
        for noise in ['0','1','2','3']:
            comps[n][noise] = 0
            for i in range(reps):
                comp = data.loc[(data['n_players'] == 1) & (data['noise'] == noise), 'score']
                comps[n][noise] += np.max(np.random.choice(comp, size = n))
            comps[n][noise] /= float(reps)

    for g in set(data['game']):
        sub = data.loc[data['game'] == g]
        n = sub.iloc[0]['n_players']
        noise = sub.iloc[0]['noise']
        score = max(sub['score']) - comps[n][noise]
        game_df_max += [[g, noise, n, score]]

    game_df_max = pd.DataFrame(game_df_max)
    game_df_max.columns = ['game','noise','n_players','max_score']

    game_df_min = []

    comps = {}
    reps = 10
    for n in range(1,7):
        comps[n] = {}
        for noise in ['0','1','2','3']:
            comps[n][noise] = 0
            for i in range(reps):
                comp = data.loc[(data['n_players'] == 1) & (data['noise'] == noise), 'score']
                comps[n][noise] += np.min(np.random.choice(comp, size = n))
            comps[n][noise] /= float(reps)

    for g in set(data['game']):
        sub = data.loc[data['game'] == g]
        n = sub.iloc[0]['n_players']
        noise = sub.iloc[0]['noise']
        score = min(sub['score']) - comps[n][noise]
        game_df_min += [[g, noise, n, score]]

    game_df_min = pd.DataFrame(game_df_min)
    game_df_min.columns = ['game','noise','n_players','min_score']
    
    print('Analyzing Max Score')
    
    mod = smf.ols(formula='max_score ~ n_players + noise', data=game_df_max)
    gres = mod.fit()
    if verbose:
        print(gres.summary())

    rgres = gres.get_robustcov_results()
    if verbose:
        print(rgres.summary())

    print('Analyzing Min Score')
    
    mod = smf.ols(formula='min_score ~ n_players + noise', data=game_df_min)
    gres = mod.fit()
    if verbose:
        print(gres.summary())

    rgres = gres.get_robustcov_results()
    if verbose:
        print(rgres.summary())
        
    print('Analyzing Mean Score')

    game_df = data.groupby('game').mean()
    game_df['noise'] = noises

    mod = smf.ols(formula='score ~ n_players + noise', data=game_df)
    gres = mod.fit()
    if verbose:
        print(gres.summary())

    rgres = gres.get_robustcov_results()
    if verbose:
        print(rgres.summary())

    return mdf, gres, rgres

def bootstrap_data(data, num_games):
    
    boot_data = pd.DataFrame()

    games = set(data['game'])
    
    sample = np.random.choice(list(games), num_games)

    for i,g in enumerate(sample):
        
        game_data = data.loc[data['game'] == g].copy()
        
        game_data['game'] = 'game-' + str(i)
        boot_data = pd.concat([boot_data, game_data])

    return boot_data
