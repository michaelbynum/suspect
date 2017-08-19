import numpy as np
from numbers import Number
import operator
from functools import reduce
from convexity_detection.expr_visitor import (
    BottomUpExprVisitor,
    ProductExpression,
    DivisionExpression,
    SumExpression,
    LinearExpression,
    NegationExpression,
    AbsExpression,
    UnaryFunctionExpression,
    expr_callback,
)
from pyomo.core.base.var import SimpleVar


class Bound(object):
    def __init__(self, l, u):
        if l is None:
            l = -np.inf
        if u is None:
            u = np.inf
        if l > u:
            raise ValueError('l must be >= u')
        self.l = l
        self.u = u

    def __add__(self, other):
        l = self.l
        u = self.u
        if isinstance(other, Bound):
            return Bound(l + other.l, u + other.u)
        elif isinstance(other, Number):
            return Bound(l + other, u + other)
        else:
            raise TypeError('adding Bound to incompatbile type')

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        l = self.l
        u = self.u
        if isinstance(other, Bound):
            return Bound(l - other.u, u - other.l)
        elif isinstance(other, Number):
            return Bound(l - other, u - other)
        else:
            raise TypeError('subtracting Bound to incompatbile type')

    def __mul__(self, other):
        l = self.l
        u = self.u
        if isinstance(other, Bound):
            ol = other.l
            ou = other.u
            new_l = min(l * ol, l * ou, u * ol, u * ou)
            new_u = max(l * ol, l * ou, u * ol, u * ou)
            return Bound(new_l, new_u)
        elif isinstance(other, Number):
            return self.__mul__(Bound(other, other))
        else:
            raise TypeError('multiplying Bound to incompatible type')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Bound):
            ol = other.l
            ou = other.u
            if ol <= 0 and ou >= 0:
                return Bound(-np.inf, np.inf)
            else:
                return self.__mul__(Bound(1/ou, 1/ol))
        elif isinstance(other, Number):
            return self.__truediv__(Bound(other, other))
        else:
            raise TypeError('dividing Bound by incompatible type')

    def __eq__(self, other):
        if not isinstance(other, Bound):
            return False
        return np.isclose(self.l, other.l) and np.isclose(self.u, other.u)

    def __repr__(self):
        return '<{} at {}>'.format(str(self), id(self))

    def __str__(self):
        return '[{}, {}]'.format(self.l, self.u)


def _sin_bound(lower, upper):
    if upper - lower >= 2 * np.pi:
        return Bound(-1, 1)
    else:
        l = lower % (2 * np.pi)
        u = l + (upper - lower)
        new_u = max(np.sin(l), np.sin(u))
        new_l = min(np.sin(l), np.sin(u))
        if l <= 0.5 * np.pi <= u:
            new_u = 1
        if l <= 1.5 * np.pi <= u:
            new_l = -1
        return Bound(new_l, new_u)


class BoundsVisitor(BottomUpExprVisitor):
    def __init__(self):
        self.memo = {}

    def bound(self, expr):
        if isinstance(expr, Number):
            return Bound(expr, expr)
        else:
            return self.memo[id(expr)]

    def set_bound(self, expr, bound):
        self.memo[id(expr)] = bound

    @expr_callback(SimpleVar)
    def visit_simple_var(self, v):
        bound = Bound(v.bounds[0], v.bounds[1])
        self.set_bound(v, bound)

    @expr_callback(Number)
    def visit_number(self, n):
        pass  # do nothing

    @expr_callback(ProductExpression)
    def visit_product(self, expr):
        bounds = [self.bound(c) for c in expr._args]
        bound = reduce(operator.mul, bounds, 1)
        self.set_bound(expr, bound)

    @expr_callback(DivisionExpression)
    def visit_division(self, expr):
        top, bot = expr._args
        bound = self.bound(top) / self.bound(bot)
        self.set_bound(expr, bound)

    @expr_callback(LinearExpression)
    def visit_linear(self, expr):
        bounds = [expr._coef[id(c)] * self.bound(c) for c in expr._args]
        bound = sum(bounds)
        self.set_bound(expr, bound)

    @expr_callback(SumExpression)
    def visit_sum(self, expr):
        bounds = [self.bound(c) for c in expr._args]
        bound = sum(bounds)
        self.set_bound(expr, bound)

    @expr_callback(NegationExpression)
    def visit_negation(self, expr):
        assert len(expr._args) == 1

        bound = self.bound(expr._args[0])
        new_bound = Bound(-bound.u, -bound.l)
        self.set_bound(expr, new_bound)

    @expr_callback(AbsExpression)
    def visit_abs(self, expr):
        assert len(expr._args) == 1

        bound = self.bound(expr._args[0])
        upper_bound = max(abs(bound.l), abs(bound.u))
        if bound.l <= 0 and bound.u >= 0:
            abs_bound = Bound(0, upper_bound)
        else:
            lower_bound = min(abs(bound.l), abs(bound.u))
            abs_bound = Bound(lower_bound, upper_bound)
        self.set_bound(expr, abs_bound)

    @expr_callback(UnaryFunctionExpression)
    def visit_unary_function(self, expr):
        assert len(expr._args) == 1

        name = expr._name
        arg = expr._args[0]
        arg_bound = self.bound(arg)

        if name == 'sqrt':
            if arg_bound.l < 0:
                raise ValueError('math domain error')
            new_bound = Bound(np.sqrt(arg_bound.l), np.sqrt(arg_bound.u))

        elif name == 'log':
            if arg_bound.l <= 0:
                raise ValueError('math domain error')
            new_bound = Bound(np.log(arg_bound.l), np.log(arg_bound.u))

        elif name == 'asin':
            if arg_bound.l < -1 or arg_bound.u > 1:
                raise ValueError('math domain error')
            new_bound = Bound(np.arcsin(arg_bound.l), np.arcsin(arg_bound.u))

        elif name == 'acos':
            if arg_bound.l < -1 or arg_bound.u > 1:
                raise ValueError('math domain error')
            # arccos is a decreasing function, swap upper and lower
            new_bound = Bound(np.arccos(arg_bound.u), np.arccos(arg_bound.l))

        elif name == 'atan':
            new_bound = Bound(np.arctan(arg_bound.l), np.arctan(arg_bound.u))

        elif name == 'exp':
            new_bound = Bound(np.exp(arg_bound.l), np.exp(arg_bound.u))

        elif name == 'sin':
            if arg_bound.u - arg_bound.l >= 2 * np.pi:
                new_bound = Bound(-1, 1)
            else:
                new_bound = _sin_bound(arg_bound.l, arg_bound.u)

        elif name == 'cos':
            if arg_bound.u - arg_bound.l >= 2 * np.pi:
                new_bound = Bound(-1, 1)
            else:
                # translate left by pi/2
                l = arg_bound.l - 0.5 * np.pi
                u = arg_bound.u - 0.5 * np.pi
                # -sin(x - pi/2) == cos(x)
                new_bound = Bound(0, 0) - _sin_bound(l, u)

        else:
            raise RuntimeError('unknown unary function {}'.format(name))
        self.set_bound(expr, new_bound)


def expr_bounds(expr):
    """Given an expression, computes its bounds"""
    v = BoundsVisitor()
    v.visit(expr)
    return v.memo[id(expr)]


def _is_positive(bounds, expr):
    bound = bounds[id(expr)]
    return bound.l > 0


def is_positive(expr):
    v = BoundsVisitor()
    v.visit(expr)
    return _is_positive(v.memo, expr)


def _is_nonnegative(bounds, expr):
    bound = bounds[id(expr)]
    return bound.l >= 0


def is_nonnegative(expr):
    v = BoundsVisitor()
    v.visit(expr)
    return _is_nonnegative(v.memo, expr)


def _is_nonpositive(bounds, expr):
    return not _is_positive(bounds, expr)


def is_nonpositive(expr):
    return not is_positive(expr)


def _is_negative(bounds, expr):
    return not _is_nonnegative(bounds, expr)


def is_negative(expr):
    return not is_negative(expr)


if __name__ == '__main__':
    import pyomo.environ as aml
    from pyomo_compat import set_pyomo4_expression_tree
    set_pyomo4_expression_tree()
    x = aml.Var()
    y = aml.Var()
    z = aml.Var()
    expr0 = (x + y) * z
