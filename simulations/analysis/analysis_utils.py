
import numpy as np
import pandas as pd

# get mean length of time between when this state started and next
# state begins, ignoring durations that end in a third condition
def get_value(sub, ignore_condition, this_state, next_state, start_index = 0):
    """
    >>> ignore = lambda sub, i: False
    >>> this = lambda sub, i: ~sub.iloc[i-1]['spinning']
    >>> next = lambda sub, i: sub.iloc[i]['spinning']
    >>> df = pd.DataFrame({'spinning':[],'other_spinning':[],'facing_spinning':[]})
    >>> get_value(df, ignore, this, next, 1)
    nan
    >>> df = pd.DataFrame({'spinning':[False,False,False]})
    >>> get_value(df, ignore, this, next, 1)
    nan
    >>> df = pd.DataFrame({'spinning':[False,False,False,True,True]})
    >>> get_value(df, ignore, this, next, 1)
    1.0
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,True,True]})
    >>> get_value(df, ignore, this, next, 1)
    2.0
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,True,True,False,False]})
    >>> get_value(df, ignore, this, next, 1)
    2.0
    >>> df = pd.DataFrame({'spinning':[True,True,False,False,False,True]})
    >>> get_value(df, ignore, this, next, 1)
    1.0
    >>> df = pd.DataFrame({'spinning':[False,False,True,False,False,False,True]})
    >>> get_value(df, ignore, this, next, 1)
    0.5
    >>> ignore = lambda sub, i: sub.iloc[i]['spinning']
    >>> this = lambda sub, i: sub.iloc[i]['other_spinning']
    >>> next = lambda sub, i: sub.iloc[i]['facing_spinning']
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,False,False,False],'facing_spinning':[False,False,True,False,False,True,False],'other_spinning':[True,True,True,True,True,True,True]})
    >>> get_value(df, ignore, this, next)
    1.0
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,False,False,False],'facing_spinning':[False,False,True,False,False,True,False],'other_spinning':[True,True,True,False,True,True,True]})
    >>> get_value(df, ignore, this, next)
    0.5
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,False,False,False],'facing_spinning':[False,False,True,True,True,True,False],'other_spinning':[True,True,True,False,True,True,True]})
    >>> get_value(df, ignore, this, next)
    1.0
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,False,False,False],'facing_spinning':[False,False,True,True,False,True,False],'other_spinning':[True,True,True,False,True,True,True]})
    >>> get_value(df, ignore, this, next)
    0.5
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,False,False,False],'facing_spinning':[False,False,True,True,False,False,False],'other_spinning':[True,True,True,False,True,True,True]})
    >>> get_value(df, ignore, this, next)
    1.0
    >>> df = pd.DataFrame({'spinning':[True,False,False,False,False,False,False],'facing_spinning':[False,False,True,False,False,True,False],'other_spinning':[True,True,True,False,True,True,True]})
    >>> get_value(df, ignore, this, next)
    0.0
    >>> df = pd.DataFrame({'spinning':[False,False,True,False,False,False,False],'facing_spinning':[False,False,True,False,False,True,False],'other_spinning':[True,True,True,False,True,True,True]})
    >>> get_value(df, ignore, this, next)
    0.0
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,False,True,False],'facing_spinning':[False,False,True,False,False,True,False],'other_spinning':[True,True,True,False,True,True,True]})
    >>> get_value(df, ignore, this, next)
    1.0
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,True,False,False],'facing_spinning':[False,False,True,False,False,True,False],'other_spinning':[True,True,True,False,True,True,True]})
    >>> get_value(df, ignore, this, next)
    1.0
    """
    
    lengths = []
    am_in_this = False
    seen = True
    for i in range(start_index, len(sub)):
        if ignore_condition(sub, i): 
            if not seen:
                lengths[-1] = np.nan
            am_in_this = False
            seen = True
            continue
        if this_state(sub, i):
            if am_in_this:
                if not seen:
                    if next_state(sub, i):
                        seen = True
                    else:
                        lengths[-1] += 1
            else:
                if not next_state(sub, i):
                    am_in_this = True
                    seen = False
                    lengths += [0]
        else:
            if not seen:
                lengths[-1] = np.nan
            am_in_this = False
    if am_in_this and not seen:
        lengths[-1] = np.nan
    
    return np.nanmean(lengths)

# get mean duration after an initial condition until first final
# condition while a third condition holds continuously
def get_while_value(sub, initial_condition, while_condition, final_condition, start_index = 0):
    """
    >>> initial = lambda sub, i: ~sub.iloc[i-1]['spinning'] and ~sub.iloc[i-1]['other_spinning'] and ~sub.iloc[i]['spinning'] and sub.iloc[i]['other_spinning']
    >>> whilec = lambda sub, i: ~sub.iloc[i-1]['facing_spinning']
    >>> final = lambda sub, i: sub.iloc[i]['facing_spinning']
    >>> df = pd.DataFrame({'spinning':[],'other_spinning':[],'facing_spinning':[]})
    >>> get_while_value(df, initial, whilec, final, 1)
    nan
    >>> df = pd.DataFrame({'spinning':[False,False,False,False],'other_spinning':[False,True,False,False],'facing_spinning':[False,False,False,True]})
    >>> get_while_value(df, initial, whilec, final, 1)
    1.0
    >>> df = pd.DataFrame({'spinning':[True,False,False,False],'other_spinning':[False,True,False,False],'facing_spinning':[False,False,False,True]})
    >>> get_while_value(df, initial, whilec, final, 1)
    nan
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,False,False,False,False,False,False],'other_spinning':[False,True,False,False,False,True,False,False,False,False],'facing_spinning':[False,False,False,True,False,False,False,False,True,False]})
    >>> get_while_value(df, initial, whilec, final, 1)
    1.5
    >>> df = pd.DataFrame({'spinning':[False,False,False,False,False,False,False,False,False,False],'other_spinning':[False,True,False,False,False,True,False,False,False,False],'facing_spinning':[False,False,False,True,False,False,False,False,True,False]})
    >>> get_while_value(df, initial, whilec, final, 1)
    1.5
    >>> initial = lambda sub, i: sub.iloc[i]['other_spinning']
    >>> whilec = lambda sub, i: ~sub.iloc[i]['spinning']
    >>> final = lambda sub, i: sub.iloc[i]['facing_spinning']
    >>> df = pd.DataFrame({'other_spinning':[False,False,False],'spinning':[False,False,False],'facing_spinning':[False,False,True]})
    >>> get_while_value(df, initial, whilec, final)
    nan
    >>> df = pd.DataFrame({'other_spinning':[True,False,False],'spinning':[False,False,False],'facing_spinning':[False,False,True]})
    >>> get_while_value(df, initial, whilec, final)
    1.0
    >>> df = pd.DataFrame({'other_spinning':[True,False,False],'spinning':[False,False,False],'facing_spinning':[True,False,True]})
    >>> get_while_value(df, initial, whilec, final)
    nan
    >>> df = pd.DataFrame({'other_spinning':[True,False,False],'spinning':[False,True,False],'facing_spinning':[True,False,True]})
    >>> get_while_value(df, initial, whilec, final)
    nan
    >>> df = pd.DataFrame({'other_spinning':[True,True,True],'spinning':[False,False,False],'facing_spinning':[True,False,False]})
    >>> get_while_value(df, initial, whilec, final)
    nan
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True,True,True],'spinning':[False,False,False,True,False,False],'facing_spinning':[False,False,True,False,False,True]})
    >>> get_while_value(df, initial, whilec, final)
    0.5
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True,True,True],'spinning':[False,False,False,False,False,False],'facing_spinning':[False,False,True,False,True,False]})
    >>> get_while_value(df, initial, whilec, final)
    1.0
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True,True,True],'spinning':[False,False,False,False,False,False],'facing_spinning':[False,False,True,False,False,False]})
    >>> get_while_value(df, initial, whilec, final)
    1.0
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True],'spinning':[False,False,False,False],'facing_spinning':[False,False,True,True]})
    >>> get_while_value(df, initial, whilec, final)
    1.0
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True,True],'spinning':[False,False,False,False,False],'facing_spinning':[False,False,True,True,True]})
    >>> get_while_value(df, initial, whilec, final)
    1.0
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True,True,True],'spinning':[False,False,False,False,False,False],'facing_spinning':[False,False,True,True,True,True]})
    >>> get_while_value(df, initial, whilec, final)
    1.0
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True,True,True,True],'spinning':[False,False,False,False,False,False,False],'facing_spinning':[False,False,True,True,True,True,True]})
    >>> get_while_value(df, initial, whilec, final)
    1.0
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True,True,True,True],'spinning':[False,False,False,True,False,False,False],'facing_spinning':[False,False,True,True,True,True,True]})
    >>> get_while_value(df, initial, whilec, final)
    1.0
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True,True,True,True],'spinning':[False,False,False,True,False,False,False],'facing_spinning':[False,False,True,False,False,True,True]})
    >>> get_while_value(df, initial, whilec, final)
    0.5
    >>> df = pd.DataFrame({'other_spinning':[True,True,True,True,True,True,True],'spinning':[False,False,False,True,False,False,False],'facing_spinning':[False,False,False,False,False,True,True]})
    >>> get_while_value(df, initial, whilec, final)
    0.0
    """
    
    lengths = []
    am_in_while = False
    seen = True
    for i in range(start_index, len(sub)):
        if not am_in_while and (not initial_condition(sub, i) or final_condition(sub, i)):
            continue
        if while_condition(sub, i):
            if am_in_while:
                if not seen:
                    if final_condition(sub, i):
                        seen = True
                    else:
                        lengths[-1] += 1.0
            else:
                am_in_while = True
                seen = False
                lengths += [0.0]
        else:
            am_in_while = False
            if not seen:
                lengths[-1] = np.nan
                seen = True
    if am_in_while and not seen:
        lengths[-1] = np.nan
    
    return np.nanmean(np.array(lengths))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
