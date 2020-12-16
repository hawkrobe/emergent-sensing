import pandas as pd
import os, re

def get_bonus(worker, data_dir, waiting_dir):

    found = False
    bonus = ''
    for game in os.listdir(data_dir):
        if game[-4:] != '.csv':
            continue    
        data = pd.io.parsers.read_csv(data_dir + game)
        for p in set(data['pid']):
            if re.match(worker, p):
                worker = p
        if worker in set(data['pid']):
            sub = data[data['pid'] == worker]
            bonus = list(sub['total_points'])[-1]
            found = True
            break
    if not found:
        try:
            dirs = os.listdir(waiting_dir)
        except:
            dirs = []
        for game in dirs:
            if game[-4:] != '.csv':
                continue    
            data = pd.io.parsers.read_csv(waiting_dir + game)
            for p in set(data['pid']):
                if re.match(worker, p):
                    worker = p
            if worker in set(data['pid']):
                sub = data[data['pid'] == worker]
                bonus = list(sub['total_points'])[-1]
                break
    
    return bonus
