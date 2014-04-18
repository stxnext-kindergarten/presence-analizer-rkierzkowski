import threading

import time

def timestamp():
    return time.time()

def cache(period):
    def decorate(f):
        store = {} # work a round for missing nonlocal declaration in 2.7
        lock = threading.RLock()

        def in_cache():
            return 'result' in store and timestamp() < store['ts'] + period

        def execute(*args, **kwargs):
            with lock:
                if not in_cache():
                    store['ts'] = timestamp()
                    result = f(*args, **kwargs)
                    store['result'] = result
                    return result
                return store['result']
        return execute
    return decorate
