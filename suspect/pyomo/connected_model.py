from numbers import Number

import pyomo.environ as pyo
from pyomo.core.expr.numeric_expr import (
    nonpyomo_leaf_types,
    NumericConstant,
    SumExpression,
)
from pyomo.core.expr.visitor import ExpressionValueVisitor
from pyomo.core.kernel.component_map import ComponentMap

from suspect.float_hash import BTreeFloatHasher
from suspect.pyomo.expr_dict import ExpressionDict
from suspect.pyomo.quadratic import QuadraticExpression


def create_connected_model(model, active=True):
    connected = model.clone()

    model_to_connected_map = ComponentMap()
    components = ExpressionDict(float_hasher=BTreeFloatHasher())

    for var in model.component_data_objects(pyo.Var, active=active, sort=True, descend_into=True):
        connected_var = connected.find_component(var.getname(fully_qualified=True))
        model_to_connected_map[var] = connected_var
        components[connected_var] = connected_var

    for constraint in model.component_data_objects(pyo.Constraint, active=active, sort=True, descend_into=True):
        connected_constraint = connected.find_component(constraint.getname(fully_qualified=True))
        model_to_connected_map[constraint] = connected_constraint

    for objective in model.component_data_objects(pyo.Objective, active=active, sort=True, descend_into=True):
        connected_objective = connected.find_component(objective.getname(fully_qualified=True))
        model_to_connected_map[objective] = connected_objective

    convert_visitor = _ConvertExpressionVisitor(components, model_to_connected_map)

    for constraint in connected.component_data_objects(pyo.Constraint, active=active, sort=True, descend_into=True):
        new_body = convert_visitor.dfs_postorder_stack(constraint.body)
        constraint._body = new_body

    for objective in connected.component_data_objects(pyo.Objective, active=active, sort=True, descend_into=True):
        new_body = convert_visitor.dfs_postorder_stack(objective.expr)
        objective._expr = new_body

    return connected, model_to_connected_map


class _ConvertExpressionVisitor(ExpressionValueVisitor):
    def __init__(self, memo, component_map):
        self.memo = memo
        self.component_map = component_map

    def visiting_potential_leaf(self, node):
        if node.__class__ in nonpyomo_leaf_types:
            expr = NumericConstant(float(node))
            expr = self.set(expr, expr)
            return True, expr

        if node.is_constant():
            expr = self.set(node, node)
            return True, expr

        if node.is_variable_type():
            var = self.get(node)
            assert var is not None
            return True, var
        return False, None

    def visit(self, node, values):
        new_expr = self.get(node)
        if new_expr is not None:
            self.set(node, new_expr)
            return new_expr

        if type(node) == SumExpression and node.polynomial_degree() == 2:
            new_expr = _convert_quadratic_expression(node)
        else:
            new_expr = node.create_node_with_local_data(tuple(values))
        self.set(node, new_expr)
        return new_expr

    def get(self, expr):
        if isinstance(expr, Number):
            const = NumericConstant(expr)
            return self.get(const)
        else:
            return self.memo[expr]

    def set(self, expr, new_expr):
        self.component_map[expr] = new_expr
        if self.memo.get(expr) is not None:
            return self.memo[expr]
        self.memo[expr] = new_expr
        return new_expr


def _convert_quadratic_expression(expr):
    # Check if there is any non bilinear term
    nonbilinear_found = False
    for arg in expr.args:
        if arg.polynomial_degree() != 2:
            nonbilinear_found = True
            break

    if not nonbilinear_found:
        return QuadraticExpression(expr)

    quadratic_args = []
    nonquadratic_args = []
    for arg in expr.args:
        if arg.__class__ not in nonpyomo_leaf_types and arg.polynomial_degree() == 2:
            quadratic_args.append(arg)
        else:
            nonquadratic_args.append(arg)

    assert len(nonquadratic_args) > 0
    quadratic = QuadraticExpression(quadratic_args)
    nonquadratic_args.append(quadratic)
    return SumExpression(nonquadratic_args)
