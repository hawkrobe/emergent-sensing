
import os

groups = ['smart-social', 'naive-social', 'non-social']
experiments = []
background_types = []
for bg in ['spot', 'wall']:
    for bot_bg in ['spot', 'wall']:
        for loc in ['far', 'close']:
            for g in groups:
                exp = bg + '-' + bot_bg + '-' + loc
                command = 'python make_belief_images.py ' + exp + ' ' + g
                print command
                os.system(command)
                command = 'sh ../scripts/to_video.sh ~/Desktop/beliefs/' + exp + '_simulation-0-' + g + '/'
                print command
                os.system(command)
