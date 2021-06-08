
class BaselineModel():

    def __init__(self, action):

        self.action = action
        self.model = None
        self.time = -1
    
    def observe(self, pos, bg_val, others, time):
        
        self.pos = pos
        self.bg_val = bg_val
        self.others = others
        self.time = time
    
    def act(self, p):

        if self.action == 'spin':
            p.go_slow()
            p.go_towards(p.pos)
        elif self.action == 'random':
            if p.goal is None or p.at_goal():
                p.set_random_goal()
            p.go_towards(p.goal)
        else:
            assert self.action == 'straight'
