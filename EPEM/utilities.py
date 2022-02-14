def singleton(self, *args, **kw):
    """
    The decorator is used to make sure that only one instance of the class is created in the program.
    """
    instances = {}

    def _singleton(*args, **kw):
        if self not in instances:
            instances[self] = self(*args, **kw)
        return instances[self]
    return _singleton