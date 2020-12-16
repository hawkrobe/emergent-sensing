import numpy as np
import statsmodels.api as sm

# http://stackoverflow.com/questions/11479064/multivariate-linear-regression-in-python
# usage
# y = [1,2,3,4,3,4,5,4,5,5,4,5,4,5,4,5,6,5,4,5,4,3,4]

# x = [
#          [4,2,3,4,5,4,5,6,7,4,8,9,8,8,6,6,5,5,5,5,5,5,5],
#          [4,1,2,3,4,5,6,7,5,8,7,8,7,8,7,8,7,7,7,7,7,6,5],
#          [4,1,2,5,6,7,8,9,7,8,7,8,7,7,7,7,7,7,6,6,4,4,4]
#          ]
# print reg_m(x,y).summary()

def reg_m(x,y):
    ones = np.ones(len(x[0]))
    X = sm.add_constant(np.column_stack((x[0], ones)))
    for ele in x[1:]:
        X = sm.add_constant(np.column_stack((ele, X)))
    results = sm.OLS(y, X).fit()
    return results

def get_normal_fit(points):
    """
    >>> mu = np.array([10,100])
    >>> cov = np.array([[10,-5],[-5,20]])
    >>> samples = np.random.multivariate_normal(mu, cov, size = 1000000)
    >>> m,s = get_normal_fit(samples)
    >>> assert np.linalg.norm(mu - m) < 1
    >>> assert np.linalg.norm(cov - s) < 1
    """
    return np.mean(points, 0), get_sample_cov(points)


def get_sample_cov(points):
    """
    >>> get_sample_cov([[1,2],[3,4],[5,6],[7,8]]).shape
    (2, 2)
    """
    return np.cov(np.transpose(points))

def bounding_oval(points):
    """    
    >>> abs(bounding_oval(np.random.normal(size=[10000,2])) - 1) < 0.1
    True
    >>> abs(bounding_oval(2*np.random.normal(size=[10000,2])) - 4) < 0.1
    True
    """
    
    cov = get_sample_cov(points)
    vals = np.linalg.eig(cov)[0]
    return np.prod(np.sqrt(vals))

def ave_dist(points):
    """    
    >>> ave_dist(np.array([[0,1],[0,0]]))
    1.0
    >>> ave_dist(np.array([[0,3],[0,0],[4,0]]))
    4.0
    """
    dists = []
    for i in range(len(points)-1):
        for j in range(i+1,len(points)):
                dists += [np.linalg.norm(points[i] - points[j])]
    return np.mean(dists)

def random_circle(radius, n):
    """
    >>> radius = 237
    >>> samples = random_circle(radius, 100000)
    >>> (np.sqrt(np.sum(samples**2,1)) <= radius).all()
    True
    >>> # make sure distribution within a random square inside the circle is uniform
    >>> size = 10
    >>> length = radius * np.cos(np.pi/4) - size/2
    >>> x = 2 * np.random.random() * length - length
    >>> y = 2 * np.random.random() * length - length
    >>> assert abs(x) < length and abs(y) < length
    >>> inds = (samples[:,0] > x - size/2) * (samples[:,0] < x + size/2)
    >>> inds = inds * (samples[:,1] > y - size/2) * (samples[:,1] < y + size/2)
    >>> assert abs(x - np.mean(samples[inds,0])) < 1
    >>> assert abs(y - np.mean(samples[inds,1])) < 1
    """

    theta = 2 * np.pi * np.random.random(size = n)
    rad = np.sqrt(np.random.random(size = n))
    x = radius * rad * np.cos(theta)
    y = radius * rad * np.sin(theta)
    return np.column_stack([x, y])

if __name__ == "__main__":
    import doctest
    doctest.testmod()
