
import numpy as np
import pandas as pd
import goal_inference_with_data
import rational_model

class Fit:

    def __init__(self, df, background_dir, player):

        in_dir = '../../modeling/'    

game = '0-1en01_simulation.csv'
player = 0

background_dir = '/Users/peter/Desktop/light-fields/0-1en01/'

df = pd.read_csv(in_dir + game)

players = list(set(df['pid']))
my_pid = players[player]


    def fit(self, model_type, pars):

        scores = []
        
        for i in range(len(pars)):

            scores += [self.run(model_type, pars[i])]

        ind = np.argmax(scores)
        
        return pars[ind], scores[ind]
    
    def run(self, model_type, par):
        
        model = goal_inference_with_data.Model(model_type(par), n_samples = self.n_samples)
        
        ticks = list(set(df['tick']))
        
        for tick in range(max(ticks)+1):

            sub = df[df['tick'] == tick]

            others = []

            for pid in players:

                if pid == my_pid:
                    continue

                others += [{'position':np.array([float(sub.loc[sub['pid'] == pid, 'x_pos']),
                                                 float(sub.loc[sub['pid'] == pid, 'y_pos'])]),
                            'angle':float(sub.loc[sub['pid'] == pid, 'angle']),
                            'speed':float(sub.loc[sub['pid'] == pid, 'velocity'])}]

            model.observe(np.array([float(sub.loc[sub['pid'] == my_pid,'x_pos']),
                                    float(sub.loc[sub['pid'] == my_pid,'y_pos'])]),
                          float(sub.loc[sub['pid'] == my_pid,'angle']),
                          float(sub.loc[sub['pid'] == my_pid,'velocity']),
                          float(sub.loc[sub['pid'] == my_pid,'bg_val']), others, tick)

        return max(model.likelihoods)
