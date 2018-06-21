# Copyright 2018 Francesco Ceccon
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

"""FBBT bounds initialization rules."""
from suspect.interval import Interval
from suspect.interfaces import UnaryFunctionRule
from suspect.expression import UnaryFunctionType


class _UnaryFunctionBoundsRule(UnaryFunctionRule):
    initial_bound = None

    def apply(self, expr, _ctx):
        child = expr.children[0]
        return {
            child: self.initial_bound,
        }


class SqrtRule(_UnaryFunctionBoundsRule):
    """Bound propagation rule for sqrt."""
    func_type = UnaryFunctionType.Sqrt
    initial_bound = Interval(0, None)


class LogRule(_UnaryFunctionBoundsRule):
    """Bound propagation rule for log."""
    func_type = UnaryFunctionType.Log
    initial_bound = Interval(0, None)


class AsinRule(_UnaryFunctionBoundsRule):
    """Bound propagation rule for asin."""
    func_type = UnaryFunctionType.Asin
    initial_bound = Interval(-1, 1)


class AcosRule(_UnaryFunctionBoundsRule):
    """Bound propagation rule for acos."""
    func_type = UnaryFunctionType.Acos
    initial_bound = Interval(-1, 1)
