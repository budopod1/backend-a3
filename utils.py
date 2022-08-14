def pad_list(iterable, length, value):
    return [
        value if i >= len(iterable) else iterable[i]
        for i in range(length)
    ]


"""
def log_func(func):
    def inner(self, *args, **kargs):
        if self.log:
            print(args, kargs)
        return func(self, *args, **kargs)
    return inner


class LoggingDict(dict):
    def __init__(self):
        super().__init__()
        self.log = False
    
    # @log_func
    def __getitem__(self, *args):
        super().__getitem__(*args)
        
    @log_func
    def __setitem__(self, *args):
        super().__setitem__(*args)
"""
