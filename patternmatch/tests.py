import unittest
from patternmatch import pattern_match as pm, special_types as st

class PatternMatchTest(unittest.TestCase):

    def setUp(self):
        pm.reset()

    def testBasicFunction(self):
        @pm(int)
        def plus_one(x):
            return x + 1

        self.assertEqual(plus_one(1), 2)

    def testSingleTypedArgument(self):
        @pm(int)
        def f(x):
            return 'int'

        @pm(float)
        def f(x):
            return 'float'

        self.assertEqual(f(1), 'int')
        self.assertEqual(f(1.0), 'float')

    def testMultipleTypedArguments(self):
        @pm(int, int)
        def f(x, y):
            return '2 ints'

        @pm(float, float)
        def f(x, y):
            return '2 floats'

        @pm(int, float)
        def f(x, y):
            return 'int and float'

        self.assertEqual(f(1, 1), '2 ints')
        self.assertEqual(f(1.0, 1.0), '2 floats')
        self.assertEqual(f(1, 1.0), 'int and float')

    def testMatchAnything(self):
        @pm.anything
        def f(x):
            return x

        self.assertEqual(f(1), 1)

    def testValueArguments(self):
        @pm(1)
        def f(x):
            return 'one'

        @pm([])
        def f(x):
            return 'empty list'

        @pm.anything
        def f(x):
            return 'neither one nor empty list'

        self.assertEqual(f(1), 'one')
        self.assertEqual(f([]), 'empty list')
        self.assertEqual(f([1]), 'neither one nor empty list')

    def testRecursion(self):
        @pm([])
        def rsum(_):
            return 0

        @pm(list)
        def rsum(xs):
            return xs[0] + rsum(xs[1:])

        self.assertEqual(rsum([1, 2, 3, 4]), 1 + 2 + 3 + 4)

    def testRaisesNonExhaustivePattern(self):
        @pm([])
        def rsum(x):
            return x

        self.assertRaises(pm.NonExhaustivePatternError,
                          rsum, [1, 2, 3])

    def testHeadTail(self):
        @pm(st.head_tail)
        def f((x, xs)):
            return x, list(xs)

        self.assertEqual(f([1, 2, 3]), (1, [2, 3]))

    def testHeadTailList(self):
        @pm(st.head_tail_list)
        def f((x, xs)):
            return x, xs

        self.assertEqual(f([1, 2, 3]), (1, [2, 3]))

    def testEmptyIter(self):
        @pm(st.empty_iter)
        def f(x):
            return 'empty iterable'

        @pm(int)
        def f(x):
            return 'int'

        self.assertEqual(f(1), 'int')
        for iterable in ([], (), set(), ''):
            try:
                self.assertEqual(f(iterable), 'empty iterable')
            except (AssertionError, pm.NonExhaustivePatternError):
                raise AssertionError('{0!r} was not considered an '
                                     'empty iterable'.format(iterable))

    def testHeadTailRecursion(self):
        @pm(st.empty_iter)
        def rproduct(_):
            return 1

        @pm(st.head_tail)
        def rproduct((x, xs)):
            return x * rproduct(xs)

        self.assertEqual(rproduct([2, 3, 4]), 24)


if __name__ == '__main__':
    unittest.main()
