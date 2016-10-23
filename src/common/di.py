import inspect


class FeatureBroker(object):

    def __init__(self):
        self.features = {}

    def add(self, name, feature):
        if name in self.features:
            raise ValueError('feature %s already exists' % name)
        if callable(feature):
            self.features[name] = feature()
        else:
            self.features[name] = feature

    def get(self, name):
        # Should fail if feature not available -- bad set-up.
        return self.features[name]

    def has(self, name):
        return name in self.features


features = FeatureBroker()


def inject(f):
    """Injects dependencies available through the FeatureBroker.

    For methods, it skips the argument named 'self'.
    """
    params = list(inspect.signature(f).parameters.items())
    injected_args_names = []
    injected_kwargs_names = []
    injected_args = []
    injected_kwargs = {}
    is_method = False
    for i, (name, param) in enumerate(params):
        if name == 'self':
            is_method = True
        if features.has(name):
            if param.kind == param.POSITIONAL_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD:
                injected_args_names.append(name)
                injected_args.append(features.get(name))
            else:
                injected_kwargs_names.append(name)
                injected_kwargs[name] = features.get(name)

    def refresh():
        nonlocal injected_args
        nonlocal injected_kwargs
        injected_args = [features.get(name) for name in injected_args_names]
        injected_kwargs = { name: features.get(name) for name in injected_kwargs_names }

    def inner(*args, **kwargs):
        refresh()
        kwargs.update(injected_kwargs)
        if not is_method:
            return f(*(tuple(injected_args) + args), **kwargs)
        else:
            self = args[0]
            args = list(args)
            del args[0]
            return f(*(tuple([self] + injected_args) + tuple(args)), **kwargs)
    return inner
