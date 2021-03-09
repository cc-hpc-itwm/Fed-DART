

def print_args(args):
    for arg, val in args.__dict__.items():
        print(arg + '.' * (50 - len(arg) - len(str(val))) + str(val))
    print()

class ClassProperty(object):
    def __init__(self, func):
        self.func = func
    def __get__(self, inst, cls):
        return self.func(cls)