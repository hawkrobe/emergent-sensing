
import numpy as np
import pandas as pd
import pickle

#
# compute D(p | q) for two multivariate normal distributions
#
# since, information projection is given by family of distributions P,
# P_0 should be model distribution
#
def kl_div(mu0, cov0, mu1, cov1):
    
    # smooth variance matrices to avoid singularities
    cov0[0,0] += 1
    cov0[1,1] += 1
    cov1[0,0] += 1
    cov1[1,1] += 1
    
    trace = np.trace(np.dot(np.linalg.inv(cov1), cov0))
    norm = np.dot(np.dot(mu1 - mu0, np.linalg.inv(cov1)), mu1 - mu0)
    det0 = np.linalg.slogdet(cov0)
    det1 = np.linalg.slogdet(cov1)
    assert det0[0] > 0
    assert det1[0] > 0
    return 0.5 * (trace + norm - 2 + det1[1] - det0[1])

def get_all_divergences(modeled):
    
    labels = ['pos','goal']
    conditional = ['no-like','like-weighted']
    
    results = {}
    for l in labels:
        for c in conditional:
            
            if c == 'like-weighted':
                weights = ['none', 'normed', 'unnormed']
            else:
                weights = ['none']
                
            for w in weights:
                
                results[l + '-' + str(c) + '-' + str(w)] = get_total_divergence(modeled, l, c, w)

    return results

def get_total_divergence(modeled, label, conditional, weighted):
    
    players = modeled.keys()
    
    divergence = {}

    for p in players:

        vals = []
        
        for t in sorted(modeled[p].keys()):
            
            if t < 16:
                vals += [np.nan]
                continue
            
            active_players = [q for q in players if (p != q) and (t in modeled[q])]
            n = len(active_players)

            norm = sum([modeled[p][t][label + '-' + q + '_prob'] for q in active_players])

            val = None
            
            for q in active_players:
                
                if val is None:
                    val = 0.0

                if conditional == 'like-weighted':
                    if weighted == 'unnormed':
                        prob = modeled[p][t][label + '-' + q + '_prob']
                    elif weighted == 'normed':
                        prob = modeled[p][t][label + '-' + q + '_prob'] / float(norm)
                    else:
                        prob = 1.0
                    mu0 = modeled[p][t][label + '-' + q + '_mean']
                    cov0 = modeled[p][t][label + '-' + q + '_cov']
                else:
                    prob = 1.0
                    mu0 = modeled[q][t][label + '_mean']
                    cov0 = modeled[q][t][label + '_cov']
                    
                mu1 = modeled[p][t]['goal_mean']
                cov1 = modeled[p][t]['goal_cov']
                
                val += prob * kl_div(mu0.copy(), cov0.copy(), mu1.copy(), cov1.copy()) / n
            
            if val is None:
                vals += [np.nan]
            else:
                vals += [val]

        divergence[p] = pd.Series(vals)
        divergence[p].index = sorted(modeled[p].keys())
                
    return divergence
