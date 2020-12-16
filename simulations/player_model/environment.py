
import numpy as np
import utils
import copy

from rectangular_world import RectangularWorld

class Player():

    def __init__(self, world, stop_and_click):

        self.curr_background = 0
        self.avg_score = 0
        self.total_points = 0
        self.avg_score_last_half = 0

        self.world = world
                
        self.pos = world.get_random_position()
        self.angle = world.get_random_angle()
        self.speed = world.min_speed
        self.active = True

        self.turn_pref = np.random.choice(['left','right'])

        self.goal = None

        self.stop_and_click = stop_and_click

    def set_random_goal(self):
        self.goal = self.world.get_random_position()
    
    def at_goal(self):
        """
        >>> p = World(RectangularWorld,debug = True).players[0]
        >>> p.goal = np.array([100,100])
        >>> p.pos = np.array([99,101])
        >>> p.at_goal()
        True
        >>> p.pos = np.array([91,113])
        >>> p.at_goal()
        False
        """
        return np.linalg.norm(self.pos - self.goal) < 15
        
    def turn(self, angle):
        """
        >>> p = World(RectangularWorld,debug = True).players[0]
        >>> p.angle = 359
        >>> p.turn(25)
        >>> p.angle
        24
        >>> p.angle = 0
        >>> p.turn(-22.5)
        >>> p.angle
        337.5
        >>> p.angle = 0
        >>> p.turn(2.0)
        >>> p.angle
        2.0
        """
        self.angle = (self.angle + angle) % 360
    
    def stop(self):
        self.speed = 0
        
    def go_slow(self):
        self.speed = self.world.min_speed

    def go_super_slow(self):
        self.speed = self.world.min_speed/2.0
    
    def go_fast(self):
        self.speed = self.world.max_speed

    def go_towards(self, x, verbose = False, goal_dist = None):
        """
        >>> p = World(RectangularWorld,debug = True).players[0]
        >>> p.turn_pref = 'left'
        >>> p.pos = p.world.get_random_position()
        >>> p.angle = 0
        >>> p.speed = 0
        >>> for i in range(1000):
        ...     p.go_towards(np.array([200,100]))
        ...     p.update_pos()
        >>> np.linalg.norm(p.pos - np.array([200,100])) < 15
        True
        >>> p = World(RectangularWorld,debug = True).players[0]
        >>> p.turn_pref = 'left'
        >>> p.pos = np.array([50,50])
        >>> p.angle = 13
        >>> p.speed = 0
        >>> for i in range(5):
        ...     p.go_towards(np.copy(p.pos), verbose = True)
        ...     p.update_pos()
        {'angle': 40.0, 'speed': 'slow'}
        {'angle': 40.0, 'speed': 'slow'}
        {'angle': 40.0, 'speed': 'slow'}
        {'angle': 40.0, 'speed': 'slow'}
        {'angle': 40.0, 'speed': 'slow'}
        >>> p.pos = np.array([50,50])
        >>> p.angle = 0
        >>> p.speed = 0
        >>> p.go_towards(np.array([40,50]), verbose = True)
        {'angle': -40.0, 'speed': 'slow'}
        >>> p.go_towards(np.array([20,50]), verbose = True)
        {'angle': -40.0, 'speed': 'fast'}
        >>> p.go_towards(np.array([60,50]), verbose = True)
        {'angle': 40.0, 'speed': 'slow'}
        >>> p.angle = 90
        >>> p.speed = 0
        >>> p.go_towards(np.array([50,40]), verbose = True)
        {'angle': -40.0, 'speed': 'slow'}
        """
        move = self.get_move_towards(x, goal_dist)

        self.turn(move['angle'])
        if move['speed'] == 'stop':
            self.stop()
        elif move['speed'] == 'slow':
            self.go_slow()
        else:
            self.go_fast()
        if verbose:
            print(move)

    def get_move_towards(self, x, goal_dist):
        
        move = utils.get_move_towards(self.pos, self.angle, x,
                                      self.world.min_speed,
                                      self.world.max_speed,
                                      self.turn_pref,
                                      self.world.pos_limits,
                                      self.world.shape, 
                                      goal_dist = goal_dist, 
                                      stop_and_click = self.stop_and_click)
        return move
    
    def get_new_pos(self):
        """
        >>> p = World(RectangularWorld,debug = True).players[0]
        >>> p.pos = np.array([1,1])
        >>> p.angle = 90
        >>> p.speed = 1
        >>> p.get_new_pos()
        array([ 2.5,  2.5])
        >>> p.pos = np.array([1,1])
        >>> p.angle = 90
        >>> p.speed = 10
        >>> p.get_new_pos()
        array([ 11. ,   2.5])
        """
        return utils.get_new_pos(self.pos, self.angle, self.speed, self.world.pos_limits, self.world.shape)

    def update_pos(self):
        self.pos = self.get_new_pos()
    
    def update_scores(self, time):
        """
        >>> p = World(RectangularWorld,debug = True).players[0]
        >>> p.curr_background = 1
        >>> p.update_scores(0)
        >>> p.avg_score
        0.00034722222222222224
        >>> p.total_points
        0.0004340277777777778
        """
        self.avg_score = self.avg_score + self.curr_background/float(self.world.game_length)
        self.total_points = self.avg_score * self.world.max_bonus
        if time >= self.world.game_length/2:
            self.avg_score_last_half = self.avg_score_last_half + self.curr_background/float(self.world.game_length/2)

class World():

    def __init__(self, world_model, n_players = 1, noise_location = '../test/', debug = False, scores = True, stop_and_click = False):

        if not scores:
            noise_location = None
        
        self.world_model = world_model(noise_location)
        self.game_length = self.world_model.game_length
        self.pos_limits = self.world_model.pos_limits
        self.shape = self.world_model.shape
        
        self.time = 0

        self.n_players = n_players
        self.players = [Player(self.world_model, stop_and_click) for i in range(n_players)]
        #if not debug and scores:
        #    self.update_scores()

        self.debug = debug
        
        self.stop_and_click = stop_and_click
        
    def advance(self):

        if not self.debug:
            self.update_scores()
        self.update_physics()
        self.time += 1
           
    def update_physics(self):
        """
        >>> w = World(RectangularWorld,debug = True)
        >>> w.players[0].pos = np.array([50,50])
        >>> w.players[0].angle = 0
        >>> w.update_physics()
        >>> w.players[0].pos
        array([ 50.   ,  47.875])
        >>> w.players[0].pos = np.array([3,3])
        >>> w.players[0].angle = 0
        >>> w.update_physics()
        >>> w.players[0].pos
        array([ 3. ,  2.5])
        >>> w.players[0].pos = np.array([50,50])
        >>> w.players[0].angle = 45
        >>> w.players[0].go_fast()
        >>> w.update_physics()
        >>> w.players[0].pos
        array([ 55.03813582,  44.96186418])
        """
        
        for p in self.players:
            p.update_pos()
        
    def update_scores(self):
        """
        >>> w = World(RectangularWorld,n_players = 2, debug = True)
        >>> w.players[0].pos = np.array([3,4])
        >>> w.players[1].pos = np.array([0,0])
        >>> w.update_scores()
        >>> w.players[0].curr_background
        0.8
        >>> w.players[0].avg_score
        0.0002777777777777778
        >>> w.players[1].curr_background
        0.0
        >>> w.players[1].avg_score
        0.0
        """
        
        for p in self.players:
            
            p.curr_background = self.world_model.get_score(p.pos, self.time)
            p.update_scores(self.time)
    
    def get_obs(self, player):
        """
        >>> w = World(RectangularWorld,debug = True)
        >>> obs = w.get_obs(0)
        >>> assert len(obs) == 4 and len(obs[0]) == 2 and len(obs[2]) == 0
        >>> w = World(RectangularWorld,n_players = 3, debug = True)
        >>> obs = w.get_obs(1)
        >>> assert len(obs) == 4 and len(obs[0]) == 2 and len(obs[2]) == 2
        """
        
        p = self.players[player]
        
        others = []
        
        for i in range(self.n_players):
            
            if player == i:
                continue
            
            if self.players[i].active:
                others += [copy.deepcopy({'position':self.players[i].pos,
                                          'angle':self.players[i].angle,
                                          'speed':self.players[i].speed,
                                          'bg_val':self.players[i].curr_background})]
            else:
                others += [{}]
        
        return p.pos, p.curr_background, others, self.time
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
