import numpy as np

# GNU Public Licence Copyright (c) Peter Krafft
# Comments and questions to pkrafft@mit.edu

# adapted from:
# GNU Public Licence Copyright (c) Colin Torney
# Comments and questions to colin.j.torney@gmail.com
# This code is provided freely, however when using this code you are asked to cite our related paper: 
# Berdahl, A., Torney, C.J., Ioannou, C.C., Faria, J. & Couzin, I.D. (2013) Emergent sensing of complex environments by mobile animal groups, Science

# Initialise random number generator, set up arrays and define the initial velocity distribution
# Parameters: Number of grid points, time step
class Noise:
    
    def __init__(self, N_in, dt_in, seed):
        
        np.random.seed(seed)
        
        self.N = N_in
        self.dt = dt_in;  

        N = self.N
        
        self.sf_fourier = np.zeros([N,N], dtype = 'complex128')
        self.sf_normal = np.zeros([N,N])
        self.visc = 0.001
        self.k0 = 24

        
        lambda_k = 0.0
        for i in range(1,N):
            ki = 2 * np.pi * ( i - (N * 0.5) )
            for j in range(1,N):
                kj = 2 * np.pi * ( j - (N * 0.5) )
                ksq = ki**2 + kj**2
                lambda_k += self.getSpectrum(ksq)
        
        flow_speed = 1.000
        self.l_scaling = flow_speed/float(lambda_k)
        
        c_rand = self.generate_random_array()
        for i in range(N):
            for j in range(N):
                if i == 0 or j==0:                    
                    self.sf_fourier[j,i] = 0j
                else:
                    ki = 2 * np.pi * (i - (N * 0.5))
                    kj = 2 * np.pi * (j - (N * 0.5))
                    ksq = ki**2 + kj**2
                    lambda_k = self.l_scaling * self.visc * self.getSpectrum(ksq)
                    alpha_ij = self.visc * ksq
                    if abs(alpha_ij) < 1e-12:
                        mag_ij = 0.0
                    else:
                        mag_ij = np.sqrt( lambda_k / (2.0 * alpha_ij) )
                    self.sf_fourier[j,i] = mag_ij * c_rand[j,i]
        
        self.prepare_save()
    
    def generate_random_array(self):
        
        N = self.N
        
        r_array = np.zeros([N,N], dtype = 'complex128')
        
        N2 = int(0.5*N)
        stddev = np.sqrt(0.5)
        
        for j in range(N2+1):
            for i in range(N2+1):
                if i == 0 or j == 0:
                    r_array[j,i] = 0j
                else:
                    ki = i - N2
                    kj = j - N2
                    c_ki = -ki
                    c_kj = -kj
                    c_i = c_ki + N2
                    c_j = c_kj + N2
                    if ki == 0 and kj == 0: #ki == c_ki and kj == c_kj:
                        real = np.random.normal(0,1)
                        r_array[j,i] = real + 0j
                    else:
                        real = np.random.normal(0,stddev)
                        imag = np.random.normal(0,stddev)
                        r_array[j,i] = real + imag*1j
                        r_array[c_j,c_i] = real - imag*1j
        
        for j in range(N2+1, N):
            for i in range(N2):
                if i == 0:
                    r_array[j,i] = 0j
                else:
                    ki = i - N2
                    kj = j - N2
                    c_ki = -ki
                    c_kj = -kj
                    c_i = c_ki + N2
                    c_j = c_kj + N2
                    
                    real = np.random.normal(0,stddev)
                    imag = np.random.normal(0,stddev)
                    r_array[j,i] = real + imag*1j
                    r_array[c_j,c_i] = real - imag*1j
        
        return r_array
    
    def advance_timestep(self):
        # this routine called from main code to advance to next flow realisation
        # using the mean reverting random process it advances the velocity in fourier space to the next time step
        
        N = self.N
        
        nsf_fourier = np.zeros([N,N], dtype = 'complex128')
        c_rand = self.generate_random_array()
        
        for i in range(N):
            for j in range(N):
                if i == 0 or j == 0:
                    nsf_fourier[j,i] = 0j
                else:
                    ki = 2 * np.pi * (i-(N*0.5))
                    kj = 2 * np.pi * (j-(N*0.5))
                    ksq = ki**2 + kj**2
                    lambda_k = self.l_scaling * self.visc * self.getSpectrum(ksq)
                    alpha_ij = self.visc * ksq
                    
                    if alpha_ij == 0.0:
                        mag_ij = 0.0
                    else:
                        mag_ij = np.sqrt( lambda_k / (2.0*alpha_ij) * (1 - np.exp(-2.0*alpha_ij*self.dt)) )
                    nsf_fourier[j,i] = self.sf_fourier[j,i] * np.exp(-alpha_ij*self.dt) + mag_ij * c_rand[j,i]
        
        self.sf_fourier = nsf_fourier
        self.prepare_save()
    
    def prepare_save(self):
        # this routine converts the fourier space flow velocity to physical space and stores results in arrays
        
        N = self.N
        
        trans_array = np.copy(self.sf_fourier)
        
        for i in range(N):
            trans_array[:,i] = N * np.fft.ifft(trans_array[:,i])
            #data = &trans_array[i*2]            
            #gsl_fft_complex_radix2_backward(data, N, N)
        
        for i in range(N):
            trans_array[i] = N * np.fft.ifft(trans_array[i])
            #data = &trans_array[i*2*N]
            #gsl_fft_complex_radix2_backward(data, 1, N)
                
        for i in range(N):
            for j in range(N):
                if (i+j)%2 == 0:
                    self.sf_normal[j,i] = trans_array[j,i].real #( (i+j)%2 == 0 ? 1.0 : -1.0 ) * trans_array[(j*N*2)+(i*2)]
                else:
                    self.sf_normal[j,i] = -trans_array[j,i].real #( (i+j)%2 == 0 ? 1.0 : -1.0 ) * trans_array[(j*N*2)+(i*2)]
    
    # external access to velocity fields
    def get_address(self):
        # returns real space amps
        return self.sf_normal
    
    def getSpectrum(self, ksq):
        return ksq/float(self.k0**4) * np.exp(-ksq * (1.0/self.k0)**2)

