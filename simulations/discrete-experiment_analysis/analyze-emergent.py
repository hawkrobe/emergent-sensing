
import os
import numpy as np

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

import seaborn as sns

import analysis_utils
#reload(analysis_utils)

out_dir = '../../../fish-plots/'

try:
    os.makedirs(out_dir)
except:
    pass

df = analysis_utils.get_emergent_data(group = False)

##

aggs = [('Mean',np.mean), 
        ('Median', np.median), 
        ('Max',max), 
        ('Min',min), 
        ('25th Percentile',lambda x: np.percentile(x, 25)), 
        ('75th Percentile',lambda x: np.percentile(x, 75))]

for agg in aggs:

    agg_name, agg_f = agg

    
    for noise in set(df['Model Noise']):

        file_suffix = "-" + agg_name + "-noise-" + noise + ".png"
        super_sub = df.copy()
        super_sub = super_sub.loc[super_sub['Model Noise'] == noise]

        super_sub[agg_name + ' Score'] = super_sub['Score']

        sns.set_style("white")
        sns.set_context("poster")
        sns_plot = sns.factorplot('Number of Players', agg_name + ' Score', col = 'Model', data = super_sub, kind = 'point', dodge = True, units = "Group", estimator = agg_f)
        sns_plot.savefig(out_dir + "score" + file_suffix)
        plt.close()
