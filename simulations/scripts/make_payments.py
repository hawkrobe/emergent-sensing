from boto.mturk.price import Price
from boto.mturk.connection import MTurkConnection
import bonuses
import re
import sys
import copy

from os.path import expanduser
home = expanduser("~")

hit_title = 'Play a game then answer a survey'
message = hit_title + ': Game bonus'

sys.path.append("../utils/")
from game_utils import *

sys.path.append("../utils/")

print

i = 1
hit_base_reward = float(sys.argv[i]); i+=1
max_num_hit_groups = int(sys.argv[i]); i+=1
exploratory_split = sys.argv[i] == 'true'; i+=1
game_id = sys.argv[i]; i+=1

pay = sys.argv[i] == 'pay' if len(sys.argv) > i else False

in_dir = '../../out/' + game_id + '/'

inactive = get_inactive(game_id)

ACCESS_ID = open(home + '/keys/aws-public').next().strip()
SECRET_KEY = open(home + '/keys/aws-private').next().strip()
HOST = 'mechanicalturk.amazonaws.com'

mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                                            aws_secret_access_key=SECRET_KEY,
                                            host=HOST)

hits = mtc.search_hits(sort_direction='Descending', page_size = max_num_hit_groups)


total_bonus = 0
n_hits = 0
n_valid = 0
n_usable = 0
review = []

for hit in hits:
    
    if hit.Title != hit_title:
        continue

    hit_id = hit.HITId
    
    i = 1
    new_assignments = mtc.get_assignments(hit_id)
    responses = copy.deepcopy(new_assignments)
    while len(new_assignments) > 0:
        i += 1
        new_assignments = mtc.get_assignments(hit_id, page_number = i)
        responses += new_assignments
    
    for res in responses:
    
        if res.AssignmentStatus != 'Submitted':
            continue
        
        n_hits += 1
        player_id = res.answers[0][0].fields[0].strip()
        if exploratory_split:
            bonus = bonuses.get_bonus(player_id, in_dir + '/exploratory/games/', in_dir + '/exploratory/waiting_games/')
            if bonus == '':
                bonus = bonuses.get_bonus(player_id, in_dir + '/confirmatory/games/', in_dir + '/confirmatory/waiting_games/')
        else:
            data_dir = in_dir + '/games/'
            waiting_dir = in_dir + '/waiting_games/'
            bonus = bonuses.get_bonus(player_id, data_dir, waiting_dir)
        if not re.match('\d{4}-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', player_id):
            bonus = ''
        if bonus != '':
            total_bonus += bonus
            n_valid += 1
            if player_id not in inactive:
                n_usable += 1
        if bonus != '' and res.AssignmentStatus == 'Submitted':
            if pay:
                print('paying', res.WorkerId, player_id, str(bonus))
                mtc.approve_assignment(res.AssignmentId)
                if bonus > 0:
                    mtc.grant_bonus(res.WorkerId, res.AssignmentId, Price(bonus), message)
            else:
                print(hit_id, res.WorkerId, player_id, str(bonus))
        else:
            review += [(hit_id, res.WorkerId, res.AssignmentStatus, player_id, bonus)]

print()
print('Please review:')
for worker in review:
    print(worker)
print()

print('Total Samples:', n_hits)
print('Valid Samples:', n_valid)
print('Usable Samples:', n_usable)
print('Total Base Pay:', n_valid*hit_base_reward)
print('Total Bonus:', total_bonus)
print('Total Pay:', 1.2*(total_bonus + n_valid*hit_base_reward))
