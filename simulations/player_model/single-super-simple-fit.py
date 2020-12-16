
import numpy as np
import pandas as pd
from fit_super_simple import Fit
import rational_model

import sys

par_1 = float(sys.argv[1])
par_2 = float(sys.argv[2])

in_dir = '../../modeling/'    

game = '0-1en01_simulation.csv'
player = 1

bg_dir = '/home/pkrafft/couzin_copy/light-fields/' + game.split('_')[-2] + '/'

df = pd.read_csv(in_dir + game)

errs = []
for i in range(100):
    fit = Fit(df, bg_dir, player)
    err = fit.fit_model(lambda: rational_model.RationalModel((par_1,par_2)))
    errs += [np.abs(err)]
    print i, np.mean(errs, 0)


