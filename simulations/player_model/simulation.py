
from environment import *
import copy

def simulate(model_type, environment_model, background_dir, n_players, par_settings = None, par_dist = None, init_pos = None, out_file = None, pids = None, add_individual_noise = False, second_bg_dir = None, second_model = None, second_environment = None, extended_write = False, noise_level = None, stop_and_click = False):

    if add_individual_noise:
        noise = np.random.normal(size = n_players)
    else:
        noise = None
    
    world = World(environment_model, noise_location = background_dir, n_players = n_players, stop_and_click = stop_and_click)
    if second_bg_dir is not None:
        assert n_players > 1
        second_world = World(second_environment, noise_location = second_bg_dir, n_players = n_players - 1, stop_and_click = stop_and_click)
    
    if init_pos is not None:
        for i in range(len(init_pos)):
            world.players[i].pos = init_pos[i]

    if second_bg_dir is not None:                
        for i in range(n_players):
            second_world.players[i-1].turn_pref = world.players[i].turn_pref
            second_world.players[i-1].pos = copy.copy(world.players[i].pos)
            second_world.players[i-1].angle = copy.copy(world.players[i].angle)
            second_world.players[i-1].speed = copy.copy(world.players[i].speed)
    
    if pids is None:
        pids = range(n_players)
    
    world.advance() # TODO: this is a hack to have bg_vals set properly
    world.time = 0
    if second_world is not None:
        second_world.advance() 
        second_world.time = 0

    goals = [['',''] for i in range(n_players)]
    obs_bg_vals = [None for i in range(n_players)]
    
    models = []
    for i,p in enumerate(world.players):

        if i == 0 or second_bg_dir is None:
            if par_settings is not None:
                models += [model_type(par_settings[i])]
            elif par_dist is not None:
                ind = np.random.choice(len(par_dist[1]),p=par_dist[1])
                models += [model_type(par_dist[0][ind])]
        else:
            if par_settings is not None:
                models += [second_model(par_settings[i])]
            elif par_dist is not None:
                ind = np.random.choice(len(par_dist[1]),p=par_dist[1])
                models += [second_model(par_dist[0][ind])]            

        obs_bg_vals[i] = get_obs_bg_val(world, second_world, i, add_individual_noise, noise_level, noise)
        
        if out_file is not None:
            write(pids[i], p, 0, out_file, obs_bg_vals[i], goals[i], extended_write)
    
    for tick in range(1, world.game_length):

        for i in range(len(world.players)):

            if second_world is None or i == 0:
                p = world.players[i]
                pos, bg_val, others, time = world.get_obs(i)
            else:
                p = second_world.players[i-1]
                pos, bg_val, others, time = second_world.get_obs(i-1)
            
            models[i].observe(pos, obs_bg_vals[i], others, time)
            goal = models[i].act(p)
            goals[i] = goal
            if second_world is not None:
                world.players[i].go_towards(goal)

        world.advance()
        if second_world is not None:
            second_world.advance()

        if add_individual_noise:
            noise += np.random.normal(size = n_players)
            
        for i,p in enumerate(world.players):

            if second_world is not None and i > 0:
                assert np.linalg.norm(world.players[i].angle - second_world.players[i-1].angle) < 1e-8
                assert np.linalg.norm(world.players[i].speed - second_world.players[i-1].speed) < 1e-8
                assert np.linalg.norm(world.players[i].pos - second_world.players[i-1].pos) < 1e-8
            
            obs_bg_vals[i] = get_obs_bg_val(world, second_world, i, add_individual_noise, noise_level, noise)
            
            if out_file is not None:
                write(pids[i], p, tick, out_file, obs_bg_vals[i], goals[i], extended_write)
            
    if second_world is not None:
        return world
    else:
        return world, second_world

def write(k, p, tick, out_file, obs_bg_val, goal, extended_write):
    out = [k, tick, 'true', p.pos[0], p.pos[1], p.speed, p.angle, p.curr_background, p.total_points]
    if extended_write:
        out += [obs_bg_val, goal[0], goal[1]]
    out = map(str, out)
    out_file.write(','.join(out) + '\n')

def get_obs_bg_val(world, second_world, i, add_individual_noise, noise_level, noise):

    if second_world is None or i == 0:
        p = world.players[i]
    else:
        p = second_world.players[i-1]
    
    bg_val = p.curr_background
    
    if add_individual_noise:
        obs_noise = 2*(1/(1 + np.exp(-noise_level*noise[i]))) - 1
        obs_bg_val = max(min(obs_noise + bg_val, 1), 0)
    else:
        obs_bg_val = bg_val
    
    return obs_bg_val

