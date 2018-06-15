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

"""Interfaces used in SUSPECT.

You don't need them, but they are nice for documentation purpose.
"""
import abc


class Problem(object):
    """Generic problem with vertices of type V."""
    pass


class Visitor(metaclass=abc.ABCMeta):
    """Visitor for vertices of Problem."""
    @abc.abstractmethod
    def visit(self, vertex, ctx):
        """Visit vertex. Return True if the vertex should be considered "dirty"."""
        pass


class Iterator(metaclass=abc.ABCMeta):
    """Iterator over vertices of Problem."""
    @abc.abstractmethod
    def iterate(self, problem, visitor, ctx, *args, **kwargs):
        """Iterate over vertices of problem, calling visitor on each one of them.

        Returns the list of vertices for which the visitor returned a True value.
        """
        pass


class ForwardIterator(Iterator): # pylint: disable=abstract-method
    """An iterator for iterating over nodes in ascending depth order."""
    pass


class BackwardIterator(Iterator): # pylint: disable=abstract-method
    """An iterator for iterating over nodes in descending depth order."""
    pass


class Rule(object):
    """Represent a series of contraints on an expression yielding a value."""
    root_expr = None

    def checked_apply(self, expr, ctx):
        """Apply rule to ``expr`` and ``ctx`` after checking matching ``expression_type``."""
        if expr.expression_type != self.root_expr:
            raise ValueError('expected {} expression type, but had {}'.format(
                self.root_expr, expr.expression_type
            ))
        return self.apply(expr, ctx)

    def apply(self, expr, ctx):
        """Apply rule to ``expr`` and ``ctx``."""
        pass
