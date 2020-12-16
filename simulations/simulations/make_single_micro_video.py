
import os
import sys
import shutil

sys.path.append('../scripts/')
from image_utils import *

in_dir = sys.argv[1]
game = sys.argv[2] 

tmp_out_dir = os.path.expanduser('~') + '/tmp-fish/'
final_out_dir = '../../../fish-movies/'

moves_file = in_dir + game + '-simulation.csv'
this_out_dir = tmp_out_dir + game + '/'

make_images(moves_file, this_out_dir + '/images/', colored = True, plot_names = True, show_time = True,
            center_files = [in_dir + game + '-matched_bg.csv', in_dir + game + '-mismatch_bg.csv', in_dir + game + '-player_bg.csv'])

os.system('sh ../scripts/to_video.sh ' + this_out_dir)

shutil.move(this_out_dir + 'video.mp4', final_out_dir + game + '.mp4')

