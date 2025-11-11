import operator


import ast
from typing import Callable, List, Type, Dict, Optional

from aspyx.reflection import TypeDescriptor

# Map AST operators to Python functions
BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}

COMPARE_OPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

BOOL_OPS = {
    ast.And: all,
    ast.Or: any
}

class TypedFunction:
    def __init__(self, func: Callable, arg_types: List[Type], return_type: Type):
        self.func = func
        self.arg_types = arg_types
        self.return_type = return_type

    def __call__(self, *args):
        if len(args) != len(self.arg_types):
            raise TypeError(f"Expected {len(self.arg_types)} arguments, got {len(args)}")
        for a, t in zip(args, self.arg_types):
            if not isinstance(a, t):
                raise TypeError(f"Argument {a} is not of type {t}")
        result = self.func(*args)
        if not isinstance(result, self.return_type):
            raise TypeError(f"Return value {result} is not of type {self.return_type}")
        return result

class ParseContext:
    def __init__(self, type: Type, functions: Dict[str, TypedFunction]):
        self.type = type
        self.type_descriptor = TypeDescriptor.for_type(type)
        self.functions = functions

    # public

    def get_property(self, name: str) -> TypeDescriptor.PropertyDescriptor:
        return self.type_descriptor.get_property(name)

    def get_type(self, name: str) -> Type:
        return self.type_descriptor.get_property(name).type

    def get_function_type(self, name: str) -> Type:
        return self.functions[name].return_type

    def eval_function(self, name: str) -> TypedFunction:
        return self.functions[name]

    def eval_attribute(self, name: str, type: Type = None):
        return TypeDescriptor.for_type(type).get_property(name).type

class EvalContext:
    def __init__(self, instance, variables: Dict[str, Callable]):
        self.instance = instance
        self.variables = variables

    # public

    def eval(self, name: str):
        return self.variables[name]()

def make_properties(instance) -> Dict[str, Callable]:
    descriptor = TypeDescriptor.for_type(type(instance))
    return {
        k: (lambda p=p: p.get(instance))
        for k, p in descriptor.properties.items()
    }

class ClassContext(EvalContext):
    def __init__(self, instance, variables: Optional[Dict[str, Callable]] = None):
        super().__init__(instance, variables if variables is not None else {})


class Eval:
    def __init__(self, type):
        self.type = type

    def eval(self, context: EvalContext):
        pass

class EvalConst(Eval):
    def __init__(self, value):
        super().__init__(type(value))

        self.value = value

    def eval(self, context: EvalContext):
        return self.value

class EvalName(Eval):
    def __init__(self, name: str, context: ParseContext):
        super().__init__(context.get_type(name))

        self.name = name
        self.property = context.get_property(name)

    def eval(self, context: EvalContext):
        return self.property.get(context.instance)#context.eval(self.name)

class EvalBinOp(Eval):
    def __init__(self, left, op, right):
        super().__init__(type=left.type) # TODO for now

        self.left = left
        self.right = right
        self.op = op

    def eval(self, context: EvalContext):
        return self.op(self.left.eval(context), self.right.eval(context))

class EvalCall(Eval):
    def __init__(self, func_node: object, arg_nodes: List[Eval], context: ParseContext) -> None:
        super().__init__(type=context.get_function_type(func_node.id))

        if isinstance(func_node, ast.Name):
            self.function = context.eval_function(func_node.id)

        self.arg_nodes = arg_nodes

    def eval(self, context: EvalContext):
        args = [arg.eval(context) for arg in self.arg_nodes]

        return self.function(*args)

# Comparisons
class EvalCompare(Eval):
    def __init__(self, left, ops, comparators):
        super().__init__(type=bool)

        self.left = left
        self.ops = ops
        self.comparators = comparators

    def eval(self, context: EvalContext):
        lhs = self.left.eval(context)
        for op, rhs_node in zip(self.ops, self.comparators):
            rhs = rhs_node.eval(context)
            if not op(lhs, rhs):
                return False
            lhs = rhs
        return True

# Boolean operations
class EvalBoolOp(Eval):
    def __init__(self, op, values):
        super().__init__(type=bool)

        self.op = op
        self.values = values

    def eval(self, context: EvalContext):
        results = [v.eval(context) for v in self.values]
        return self.op(results)

class EvalAttribute(Eval):
    def __init__(self, value_node, attr: str, context: ParseContext):
        super().__init__(type=bool)

        self.value_node = value_node

        descriptor = TypeDescriptor.for_type(value_node.type)

        self.attr = descriptor.get_property(attr)#context.eval_attribute(attr, type=value_node.type)

    def eval(self, context: EvalContext):
        value = self.value_node.eval(context)

        return self.attr.get(value)

class ExpressionCompiler:
    def parse(self, expression: str, context: ParseContext) -> Eval:
        tree = ast.parse(expression, mode="eval")
        return self.create(tree, context)

    # internal

    def create_func(self, node, context: ParseContext):
        pass

    def create(self, node, context: ParseContext):
        if isinstance(node, ast.Expression):
            return self.create(node.body, context)

        elif isinstance(node, ast.Constant):
            return EvalConst(node.value)

        elif isinstance(node, ast.Name):
            return EvalName(node.id, context)

        elif isinstance(node, ast.BinOp):
            return EvalBinOp(self.create(node.left, context), BIN_OPS[type(node.op)], self.create(node.right, context))

        elif isinstance(node, ast.Compare):
            ops = [COMPARE_OPS[type(o)] for o in node.ops]
            comparators = [self.create(c, context) for c in node.comparators]
            return EvalCompare(self.create(node.left, context), ops, comparators)

        elif isinstance(node, ast.BoolOp):
            return EvalBoolOp(BOOL_OPS[type(node.op)], [self.create(v, context) for v in node.values])

        elif isinstance(node, ast.Call):
            return EvalCall(node.func, [self.create(arg, context) for arg in node.args], context)

        elif isinstance(node, ast.Attribute):
            return EvalAttribute(self.create(node.value, context), node.attr, context=context)

        else:
            raise ValueError(f"Unsupported AST node: {node}")