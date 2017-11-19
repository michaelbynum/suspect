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

from convexity_detection.monotonicity.monotonicity import Monotonicity
from convexity_detection.util import numeric_types, numeric_value
from convexity_detection.math import almosteq, almostgte


def pow_monotonicity(mono_handler, expr):
    assert len(expr._args) == 2
    base, exponent = expr._args

    if isinstance(base, numeric_types):
        base = numeric_value(base)
        mono_f = mono_handler.monotonicity(exponent)
        if base < 0:
            return Monotonicity.Unknown
        elif almosteq(base, 0):
            return Monotonicity.Constant
        elif 0 < base < 1:
            if mono_f.is_nondecreasing() and mono_handler.is_nonpositive(exponent):
                return Monotonicity.Nondecreasing
            elif mono_f.is_nonincreasing() and mono_handler.is_nonnegative(exponent):
                return Monotonicity.Nondecreasing
            else:
                return Monotonicity.Unknown
        elif almostgte(base, 1):
            if mono_f.is_nondecreasing() and mono_handler.is_nonnegative(exponent):
                return Monotonicity.Nondecreasing
            elif mono_f.is_nonincreasing() and mono_handler.is_nonpositive(exponent):
                return Monotonicity.Nondecreasing
            else:
                return Monotonicity.Unknown

        return Monotonicity.Unknown
    elif isinstance(exponent, numeric_types):
        exponent = numeric_value(exponent)
        mono_f = mono_handler.monotonicity(base)
        if almosteq(exponent, 1):
            return mono_f
        elif almosteq(exponent, 0):
            return Monotonicity.Constant
        else:
            is_integer = almosteq(exponent, int(exponent))
            is_even = almosteq(exponent % 2, 0)
            if is_integer and is_even:
                if exponent > 0:
                    if mono_f.is_nondecreasing() and mono_handler.is_nonnegative(base):
                        return Monotonicity.Nondecreasing
                    elif mono_f.is_nonincreasing() and mono_handler.is_nonpositive(base):
                        return Monotonicity.Nondecreasing
                    elif mono_f.is_nondecreasing() and mono_handler.is_nonpositive(base):
                        return Monotonicity.Nonincreasing
                    elif mono_f.is_nonincreasing() and mono_handler.is_nonnegative(base):
                        return Monotonicity.Nonincreasing
                    else:
                        return Monotonicity.Unknown
                else:
                    if mono_f.is_nonincreasing() and mono_handler.is_nonnegative(base):
                        return Monotonicity.Nondecreasing
                    elif mono_f.is_nondecreasing() and mono_handler.is_nonpositive(base):
                        return Monotonicity.Nondecreasing
                    elif mono_f.is_nonincreasing() and mono_handler.is_nonpositive(base):
                        return Monotonicity.Nonincreasing
                    elif mono_f.is_nondecreasing() and mono_handler.is_nonnegative(base):
                        return Monotonicity.Nonincreasing
                    else:
                        return Monotonicity.Unknown

            elif is_integer:  # is odd
                if exponent > 0 and mono_f.is_nondecreasing():
                    return Monotonicity.Nondecreasing
                elif exponent < 0 and mono_f.is_nonincreasing():
                    return Monotonicity.Nondecreasing
                elif exponent > 0 and mono_f.is_nonincreasing():
                    return Monotonicity.Nonincreasing
                elif exponent < 0 and mono_f.is_nondecreasing():
                    return Monotonicity.Nonincreasing
                else:
                    return Monotonicity.Unknown
            else:  # not an integer
                if not mono_handler.is_nonpositive(base):
                    return Monotonicity.Unknown
                elif exponent > 0:
                    return mono_f
                elif exponent < 0:
                    if mono_f.is_nondecreasing():
                        return Monotonicity.Nonincreasnig
                    elif mono_f.is_nonincreasing():
                        return Monotonicity.Nondecreasing
                    else:
                        return Monotonicity.Unknown
                else:
                    return Monotonicity.Unknown

    return Monotonicity.Unknown
