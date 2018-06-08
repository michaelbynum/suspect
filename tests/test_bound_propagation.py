# Copyright 2017 Francesco Ceccon
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: skip-file
import pytest
from hypothesis import given, assume
from hypothesis.strategies import integers
from suspect.fbbt.propagation import BoundsPropagationVisitor
import suspect.dag.expressions as dex
from suspect.interval import Interval
from tests.conftest import (
    PlaceholderExpression,
    bound_description_to_bound,
    mono_description_to_mono,
    coefficients,
    reals,
    ctx
)


@pytest.fixture
def visitor():
    return BoundsPropagationVisitor()


@given(reals(), reals())
def test_variable_bound(visitor, ctx, a, b):
    lb = min(a, b)
    ub = max(a, b)
    var = dex.Variable('x0', lower_bound=lb, upper_bound=ub)
    visitor(var, ctx)
    assert ctx.bound[var] == Interval(lb, ub)


@given(reals())
def test_constant_bound(visitor, ctx, c):
    const = dex.Constant(c)
    visitor(const, ctx)
    assert ctx.bound[const] == Interval(c, c)


@given(reals(), reals(), reals(), reals())
def test_constraint_bound(visitor, ctx, a, b, c, d):
    e_lb, e_ub = min(a, b), max(a, b)
    c_lb, c_ub = min(c, d), max(c, d)
    assume(max(e_lb, c_lb) <= min(e_ub, c_ub))
    p = PlaceholderExpression()
    ctx.bound[p] = Interval(e_lb, e_ub)
    cons = dex.Constraint('c0', lower_bound=c_lb, upper_bound=c_ub, children=[p])
    visitor(cons, ctx)
    expected = Interval(max(e_lb, c_lb), min(c_ub, e_ub))
    assert ctx.bound[cons] == expected


@given(reals(max_value=100.0), reals(max_value=100.0))
def test_objective_bound(visitor, ctx, a, b):
    lb, ub = min(a, b), max(a, b)
    assume(lb < ub)
    p = PlaceholderExpression()
    ctx.bound[p] = Interval(lb, ub)
    o = dex.Objective('obj', children=[p])
    visitor(o, ctx)
    assert ctx.bound[o] == Interval(lb, ub)


@given(integers(min_value=1))
def test_even_pow_bound(visitor, ctx, n):
    p = PlaceholderExpression()
    c = dex.Constant(2*n)
    pow_ = dex.PowExpression(children=[p, c])
    visitor(pow_, ctx)
    assert ctx.bound[pow_].is_nonnegative()
