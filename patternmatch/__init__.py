from abc import ABCMeta
from itertools import izip, islice


class special_type(object):
    """Abstract base class for creating special_types"""
    __metaclass__ = ABCMeta

    @classmethod
    def parse_arg(cls, arg):
        return arg

    @classmethod
    def matches(cls, arg):
        return True


class special_types(object):
    class head_tail(special_type):
        """Passes an iterable as a tuple (head, iter(tail))"""
        @classmethod
        def parse_arg(cls, arg):
            it = iter(arg)
            return (it.next(), it)

        @classmethod
        def match(cls, (head, tail)):
            class head_tail_match(special_type):
                @classmethod
                def matches(cls, (arg_head, arg_tail)):
                    return head == arg_head and tail == arg_tail
            return head_tail_match


class PatternMatchedFunction(object):
    def __init__(self, name, defs):
        self.__name__ = name
        self._defs = defs

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
                        if isinstance(pattern_item, special_type):
                            args[i] = pattern_item.parse_arg(arg)
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
            if isinstance(arg, special_type):
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
