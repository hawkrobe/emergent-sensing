
import matplotlib
matplotlib.use('Agg')

import os
import matplotlib.pyplot as plt
import pylab

class Canvas:

    def __init__(self, out_dir):
        self.objects = []
        self.simulated_objects = []
        self.time = 0
        self.out_dir = out_dir + '/images/'
        self.cm = plt.cm.get_cmap('Greens')
        try:
            os.makedirs(self.out_dir)
        except:
            pass

    def reset_simulated(self):
        self.simulated_objects = []

    def reset_objects(self):
        self.simulated_objects = []
        self.objects = []
        
    def plot(self, values, value_type, text = None):

        self.plot_point(values, value_type, True, text)
        
        if value_type == 'real' or value_type == 'other': # or value_type == 'true'
            self.objects += [(values, value_type)]             
        if value_type == 'simulated':
            self.simulated_objects += [(values, value_type)]
    
    def advance(self):

        ax = pylab.subplot(111)
        plt.axis('scaled')
        ax.set_xlim([0,480])
        ax.set_ylim([0,275])
        plt.savefig(self.out_dir + 'pos' + "%04d" % self.time +  '.png')
        plt.clf()

        self.time += 1

    def plot_previous(self):

        for o in self.objects:

            self.plot_point(*o)

        for o in self.simulated_objects:

            self.plot_point(*o)
            

        
    def plot_point(self, value, value_type, final = False, text = None):
        
        # if value_type == 'true' or value_type == 'start':
        #     color = 'black'
        #     x_pos = value['x_pos']
        #     y_pos = value['y_pos']
        #     bg_val = value['bg_val']
        #     angle = value['angle']
        
        if value_type == 'simulated' or value_type == 'real' or value_type == 'other':
            if value_type == 'real':
                color = 'black'
                alpha = 1.0
            elif value_type == 'simulated':
                color = 'red'
                alpha = 0.25
            elif value_type == 'other':
                color = '#00bfff'
                alpha = 1.0
            x_pos = value.pos[0]
            y_pos = value.pos[1]
            bg_val = value.curr_background
            angle = value.angle

        if value_type == 'beliefs':

            for i in range(len(value)):
                plt.scatter(value[i][0], value[i][1], s = 1, c = 'red', edgecolors='red', alpha = 0.1)

        else:
            if final:

                if value_type == 'simulated':
                    plt.scatter(x_pos - 2.5,
                                y_pos - 2.5,
                                s=150,
                                marker = (3, 0, (180 + angle) % 360 ),
                                facecolors='none'
                            )
                
                plt.scatter(x_pos - 2.5,
                            y_pos - 2.5,
                            s=150,
                            c=color if value_type == 'simulated' else 'white',
                            alpha = alpha,
                            marker = (3, 0, (180 + angle) % 360 ),
                )
                if text is not None:
                    plt.title(str(text), size = 16)

            else:

                plt.scatter(x_pos, y_pos, c=color, alpha = alpha)

