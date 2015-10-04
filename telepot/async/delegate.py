
def call(corofunc, *args, **kwargs):
    def f(seed_tuple):
        return corofunc(seed_tuple, *args, **kwargs)
    return f

def create_run(cls, *args, **kwargs):
    def f(seed_tuple):
        j = cls(seed_tuple, *args, **kwargs)
        return j.run()
    return f
