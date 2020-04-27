import os, sys, random
import numpy as np
from noise import Noise
from multiprocessing import Process

# GNU Public Licence Copyright (c) Peter Krafft
# Comments and questions to pkrafft@mit.edu
# This code is provided freely, however when using this code you are asked to cite our related paper: 
# Krafft et al. (2015) Emergent Collective Sensing in Human Groups, CogSci
# adapted from code by Colin Torney:
# GNU Public Licence Copyright (c) Colin Torney
# Comments and questions to colin.j.torney@gmail.com
# This code is provided freely, however when using this code you are asked to cite our related paper: 
# Berdahl, A., Torney, C.J., Ioannou, C.C., Faria, J. & Couzin, I.D. (2013) Emergent sensing of complex environments by mobile animal groups, Science

DEBUG = False

base_dir = sys.argv[1] + '/'

def main():
    
    if DEBUG:
        ids = map(str, range(2))
        scales = [0.1, 0.25, 0.4]
    else:
        ids = map(str, range(8))
        scales = [0.1, 0.25, 0.4]

    running = []    
    for out_id in ids:
        for scale_noise in scales:
            
            seed = np.random.randint(sys.maxint)
            
            args = (
                out_id,
                seed,
                scale_noise,
                base_dir,
                )
            
            print out_id + ',' + str(scale_noise) + ',' + str(seed)
            process = Process(target = create_field,
                              args = args)
            process.start()
            running += [process]
    
    for process in running:
        process.join()

def create_field(out_id, seed, scale_noise, base_dir): 
    
    #int randseed=1;
    #int seedoffset=321;
    #if (argc>1)
    #randseed=atoi(argv[1]);
    #srand(randseed+seedoffset);
    
    np.random.seed(seed)
    seed = np.random.randint(sys.maxint)

    nx = 500
    ny = 300

    N = 512#powf(2,ceil(log2(ny)))
    noise = Noise(N, 0.025, seed)

    n_array = noise.get_address()
    sigma = 50
    amp = 1.50

    xmin = 5
    xmax = 490
    ymin = 20
    ymax = 300

    omega = 0.01
    speed = 1
    if DEBUG:
        tmax = 2
    else:
        tmax = 2880
    width = 1.0/(2.0*sigma)

    xrange = xmax-xmin
    yrange = ymax-ymin

    switch_time = 0

    offset = 20
    x = (xmin+offset) + (xrange-offset) * np.random.random()#(rand()/(RAND_MAX+1.0)))
    y = (ymin+offset) + (yrange-offset) * np.random.random()#(rand()/(RAND_MAX+1.0)))

    nmax = 0.0
    for i in range(N):
        if nmax < n_array[0,i]:
            nmax = n_array[0,i]

    level = '{0:.0e}'.format(scale_noise).replace("+","").replace("-","n")
    out_dir = base_dir + out_id + '-' + level + '/'
    try:
        os.makedirs(out_dir)
    except OSError:
        print 'Warning: ' + out_dir + ' directory exists'
        pass

    for t in range(tmax):
        if t == switch_time:
            nextx = (xmin + offset) + (xrange - offset) * np.random.random()# (rand()/(RAND_MAX+1.0)))
            nexty = (ymin + offset) + (yrange - offset) * np.random.random()#(rand()/(RAND_MAX+1.0)))
            switch_time = t + 1 + int( np.sqrt((x - nextx)**2 + (y - nexty)**2) / speed )
            heading = np.arctan2(nexty - y, nextx - x)

        f = open(out_dir + 't' + str(t) + '.csv', 'w')

        x = x + speed * np.cos(heading)
        y = y + speed * np.sin(heading)
        nav = 0.0
        nc = 0
        for i in range(xmin,xmax):
            for j in range(ymin,ymax):
                nav = nav + n_array[j,i]
                nc = nc + 1

        nav = nav/float(nmax*nc)

        for i in range(xmin,xmax):

            out = []
            for j in range(ymin,ymax):
                x_d = i - x
                y_d = j - y

                grey = 1.0 - amp * np.exp( -np.sqrt(x_d**2 + y_d**2)*width ) + scale_noise*( n_array[j,i]/float(nmax) - nav )
                if grey > 1:
                    grey = 1.0
                if grey < 0:
                    grey = 0.0
                #if ((mask.read(i,j)/256.0>0.5) 
                #   grey=0.0

                out += ["{0:0.2f}".format(grey)]

#            f.write(','.join(out) + '\n')

        f.close()

        noise.advance_timestep()

if __name__ == "__main__":
    main()
