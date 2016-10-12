
import os
import datetime

time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

os.system('mv ./data/ ../datapile/' + time + '-data')

os.system('mkdir ./data/')
os.system('mkdir ./data/games/')
os.system('mkdir ./data/waiting_games/')
os.system('mkdir ./data/latencies/')
os.system('mkdir ./data/waiting_latencies/')

os.system('git add --all ../')
os.system('git commit -m "Running ' + time + '"')

os.system('git rev-parse HEAD >> ./data/commit_num')

os.system('nodejs app.js >> ./data/log  2>&1')
