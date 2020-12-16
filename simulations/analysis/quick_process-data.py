
import pandas as pd
import numpy as np
from quick_process import *

import sys,os
sys.path.append("../")
sys.path.append("../utils/")
from utils import *

base = 'synthetic-all'
in_dir = '../../' + base + '/'
out_dir = '../../quick-processed-' + base + '/'
try:
    os.makedirs(out_dir)
except:
    pass

subset = '1en01'

for data_file in os.listdir(in_dir):
    if data_file[-4:] != '.csv':
        continue

    bg_file = data_file.split('_')[-2]
    
    if bg_file.split('-')[1] != subset:
        continue        
    
    print data_file
    
    in_file = in_dir + data_file
    data = pd.io.parsers.read_csv(in_file)
    success, df = process_data(data, {})
    df.to_csv(out_dir + data_file, index = False)
