def cls_name(cls):
    return ".".join([cls.__module__, cls.__name__])


def call_mro(obj, func_name, *args, **kwargs):
    for cls in reversed(obj.__class__.__mro__):
        try:
            cls.__dict__[func_name](obj, *args, **kwargs)
        except KeyError:
            pass


def subclasses(cls):
    yield cls
    for subclass in cls.__subclasses__():
        yield subclass
        for sub_sub in subclasses(subclass):
            yield sub_sub
