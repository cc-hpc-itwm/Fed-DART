

def print_args(args):
    print('-'*21 + "FED-DART" + '-'*21)
    for arg, val in args.__dict__.items():
        print(arg + '.' * (50 - len(arg) - len(str(val))) + str(val))
    print()

class ClassProperty(object):
    def __init__(self, func):
        self.func = func
    def __get__(self, inst, cls):
        return self.func(cls)