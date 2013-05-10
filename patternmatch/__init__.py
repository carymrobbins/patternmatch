from abc import ABCMeta
from itertools import izip, islice


class PatternMatchedFunction(object):
    def __init__(self, name, defs):
        self.__name__ = name
        self._defs = defs

    @classmethod
    def is_special_type(cls, t):
        return special_type in getattr(t, '__bases__', ())

    def __call__(self, *args, **kwargs):
        for function, pattern in self._defs:
            match_found = False
            if pattern == (PatternMatcher.Anything,):
                match_found = True
            else:
                args = list(args)
                match_found = True
                for i, (pattern_item, arg) in enumerate(izip(pattern, args)):
                    if self._arg_matches(pattern_item, arg):
                        if self.is_special_type(pattern_item):
                            pattern_arg = pattern_item(arg)
                            if pattern_arg.matches():
                                args[i] = pattern_arg.parse()
                            else:
                                break
                    else:
                        match_found = False
                        break
            if match_found:
                return function(*args, **kwargs)
        raise PatternMatcher.NonExhaustivePatternError(
            'Args {0} does not match any pattern in function {1}'.format(
                args, self.__name__))
        return self._defs[0][0](*args, **kwargs)

    def _arg_matches(self, pattern_item, arg):
        try:
            if isinstance(arg, pattern_item):
                return True
            if self.is_special_type(pattern_item):
                return True
        except TypeError:
            if arg == pattern_item:
                return True
        return False


class PatternMatcher(object):
    def __init__(self):
        self.functions = {}

    def reset(self):
        self.functions = {}

    @property
    def anything(self):
        return self(self.Anything)

    def __call__(self, *pattern):
        def decorator(function):
            function_pattern = (function, pattern)
            name = function.__name__
            if self.functions.has_key(name):
                self.functions[name].append(function_pattern)
            else:
                self.functions[name] = [function_pattern]
            return PatternMatchedFunction(name, self.functions[name])
        return decorator

    class Anything(object):
        pass

    class NonExhaustivePatternError(Exception):
        pass


pattern_match = PatternMatcher()


class special_type(object):
    """Abstract base class for creating special_types"""
    __metaclass__ = ABCMeta

    def __init__(self, arg):
        self._arg = arg

    def parse(self):
        return self._arg

    def matches(self):
        return True


class head_tail(special_type):
    """Passes an iterable as a tuple (head, iter(tail))"""
    def __init__(self, arg):
        super(head_tail, self).__init__(arg)
        self._arg_parsed = False

    def parse(self):
        if self._arg_parsed:
            return self._cached_arg
        else:
            # it = iter(self._arg)
            # self._cached_arg = (it.next(), it)
            if len(self._arg) < 2:
                raise IndexError
            self._cached_arg = (self._arg[0], self._arg[1:])
            self._arg_parsed = True
            return self._cached_arg

    def matches(self):
        try:
            self.parse()
            return True
        except IndexError:
            return False
