import functools
import time


def time_it(func):
    """Timestamp decorator for dedicated functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()                 
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        mlsec = repr(elapsed).split('.')[1][:3]
        readable = time.strftime("%H:%M:%S.{}".format(mlsec), time.gmtime(elapsed))
        print('Function "{}": {} sec'.format(func.__name__, readable))
        return result
    return wrapper