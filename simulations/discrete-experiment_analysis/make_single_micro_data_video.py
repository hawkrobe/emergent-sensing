
import os
import sys
import shutil

import pandas as pd

sys.path.append('../scripts/')
from image_utils import *

in_dir = sys.argv[1]
if len(sys.argv) > 2:
    game = sys.argv[2]
else:
    game = None

if game is None:
    games = [g[:-4] for g in os.listdir(in_dir) if g[-4:] == '.csv']
else:
    games = [game]


for game in games:

    print("Processing", game)
    
    sim_dir = '../../couzin_replication/metadata/v2/'

    tmp_out_dir = os.path.expanduser('~') + '/tmp-fish/'

    moves_file = in_dir + game + '.csv'

    player_data = pd.read_csv(moves_file)
    if len(player_data) == 0:
        continue

    rounds = set(player_data['round_type'])

    #for r in rounds:
    for r in ['social']:

        print('Round', r)

        this_out_dir = tmp_out_dir + game + '/' + r + '/'
        final_out_dir = '../../../fish-movies/' + game + '/' + r + '/'

        sub = player_data.loc[player_data['round_type'] == r]

        bg_cond = sub.iloc[0]['bg_cond']
        close_half = sub.iloc[0]['close_cond']
        sim_num = sub.iloc[0]['sim_num']

        if r[:7] == 'initial':

            centers = [sim_dir + bg_cond + '-demo' + str(sim_num) + '_bg.csv']
            sim_file = None

        else:

            sim_prefix = sim_dir + 'v2-' + bg_cond + '-close_' + close_half + '-asocial-smart-0-' + str(sim_num)
            centers = [sim_prefix + '-social-matched_bg.csv', sim_prefix + '-social-mismatch_bg.csv']

            if r == 'social':
                sim_file = sim_prefix + '-social-simulation.csv'
            elif r == 'nonsocial':
                sim_file = None

        make_images(sim_file, this_out_dir + '/images/', colored = True, plot_names = True, plot_targets = True, show_time = True,
                    center_files = centers, player_data = sub)

        os.system('sh ../scripts/to_video.sh ' + this_out_dir)

        try:
            os.makedirs(final_out_dir)
        except:
            pass

        shutil.move(this_out_dir + 'video.mp4', final_out_dir + game + '.mp4')

