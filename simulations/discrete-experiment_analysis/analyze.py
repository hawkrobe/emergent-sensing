
import os

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


df = analysis_utils.get_data()

##

sns.set_style("white")
sns.set_context("poster")

for noise in set(df['Model Noise']):

    file_suffix = "-noise-" + noise + ".png"
    super_sub = df.copy()
    super_sub = super_sub.loc[super_sub['Model Noise'] == noise]
    
    # sub = super_sub.copy()
    # sub = sub.loc[sub['Background Match'] == 'match']
    # sub = sub.loc[sub['Nearest Goal'] == 'far']

    # sns_plot = sns.factorplot('Background', 'Social Index', hue = 'Bot Condition', col = 'Model', data = sub, kind = 'point', dodge = True)
    # sns_plot.savefig(out_dir + "asocial-comparison" + file_suffix)

    ###
    
    # sub = super_sub.copy()
    # sub = sub.loc[sub['Bot Condition'] == 'visible']
    # sub = sub.loc[sub['Nearest Goal'] == 'far']
    
    # sns_plot = sns.factorplot('Background', 'Social Index', hue = 'Background Match', col = 'Model', data = sub, kind = 'point', dodge = True)
    # sns_plot.savefig(out_dir + "naive-comparison" + file_suffix)

    # ###

    # sub = super_sub.copy()
    # sub = sub.loc[sub['Background Match'] == 'match']
    # sub = sub.loc[sub['Bot Condition'] == 'visible']
    
    # sns_plot = sns.factorplot('Background', 'Social Index', hue = 'Nearest Goal', col = 'Model', data = sub, kind = 'point', dodge = True)
    # sns_plot.savefig(out_dir + "eager-comparison" + file_suffix)

    ###
    
    sub = super_sub.copy()
    sub = sub.loc[sub['Bot Condition'] == 'visible']
    
    sns_plot = sns.factorplot('Bg Match', 'Social Index', hue = 'Nearest Goal', col = 'Model', row = 'Bg', data = sub, kind = 'bar')
    sns_plot.savefig(out_dir + "all-comparison-index-" + file_suffix)

    sns_plot = sns.factorplot('Bg Match', 'Goal Hits', hue = 'Nearest Goal', col = 'Model', row = 'Bg', data = sub, kind = 'bar')
    sns_plot.savefig(out_dir + "all-comparison-goal-" + file_suffix)

    sns_plot = sns.factorplot('Bg Match', 'Asocial Goal Hits', hue = 'Nearest Goal', col = 'Model', row = 'Bg', data = sub, kind = 'bar')
    sns_plot.savefig(out_dir + "all-comparison-asocial-goal-" + file_suffix)
