
class TestModel():

    def __init__(self, cycle):

        self.cycle = cycle
        self.model = None
        self.time = -1
    
    def observe(self, pos, bg_val, others, time):
        
        self.pos = pos
        self.bg_val = bg_val
        self.others = others
        self.time = time
    
    def act(self, p):

        if self.time % self.cycle < self.cycle/2:
            p.go_slow()
        else:
            p.go_fast()
        
        if self.time % (self.cycle/2) == 0:
            if self.time < 1000:
                p.turn(20)
            else:
                p.turn(-20)
                
