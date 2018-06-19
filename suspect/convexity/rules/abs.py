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

"""Convexity detection rules for abs function."""
from suspect.convexity.convexity import Convexity
from suspect.expression import UnaryFunctionType
from suspect.interfaces import UnaryFunctionRule


class AbsRule(UnaryFunctionRule):
    """Return convexity of abs."""
    func_type = UnaryFunctionType.Abs

    def apply(self, expr, ctx):
        child = expr.children[0]
        cvx = ctx.convexity(child)
        bounds = ctx.bounds(child)
        if cvx.is_linear():
            return Convexity.Convex
        elif cvx.is_convex():
            if bounds.is_nonnegative():
                return Convexity.Convex
            elif bounds.is_nonpositive():
                return Convexity.Concave
        elif cvx.is_concave():
            if bounds.is_nonpositive():
                return Convexity.Convex
            elif bounds.is_nonnegative():
                return Convexity.Concave
        return Convexity.Unknown
