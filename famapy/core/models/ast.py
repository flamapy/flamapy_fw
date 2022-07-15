from typing import Any
from enum import Enum


class ASTOperation(Enum):
    REQUIRES = 'REQUIRES'
    EXCLUDES = 'EXCLUDES'
    AND = 'AND'
    OR = 'OR'
    XOR = 'XOR'
    IMPLIES = 'IMPLIES'
    NOT = 'NOT'
    EQUIVALENCE = 'EQUIVALENCE'


class Node:

    def __init__(self, data: Any, left: 'Node' = None, right: 'Node' = None):  # type: ignore
        self.data = data
        self.left = left
        self.right = right

    def is_term(self) -> bool:
        return not self.is_op()

    def is_op(self) -> bool:
        return isinstance(self.data, ASTOperation)

    def is_unary_op(self) -> bool:
        return self.is_op() and self.data in [ASTOperation.NOT]

    def is_unique_term(self) -> bool:
        return not self.is_op() and self.left is None

    def is_binary_op(self) -> bool:
        return not self.is_unique_term() and not self.is_unary_op()

    def __str__(self) -> str:
        data = self.data.value if self.is_op() else self.data
        if self.left and self.right:
            return f'{data}[{self.left}][{self.right}]'
        if self.left and not self.right:
            return f'{data}[{self.left}][]'
        if not self.left and self.right:
            return f'{data}[][{self.right}]'
        return str(data)

    @staticmethod
    def _get_pretty_str_node(node: 'Node') -> str:
        res = ''
        if node.is_op():
            res = f'{node.pretty_str()}'
            if node.is_binary_op():
                res = f'({res})'
        else:
            res = str(node)
        return res

    def pretty_str(self) -> str:
        data = self.data.value if self.is_op() else self.data
        left = Node._get_pretty_str_node(self.left) if self.left is not None else ''
        right = Node._get_pretty_str_node(self.right) if self.right is not None else ''

        if self.is_unique_term():
            res = f'{data}'
        elif self.is_unary_op():
            res = f'{data} {left}'
        else:  # binary operation
            res = f'{left} {data} {right}'
        return res


class AST:
    """Abstract Syntax Tree (AST) to store constraints."""

    def __init__(self, root: Node):
        self.root = root

    @classmethod
    def create_simple_binary_operation(cls, operation: ASTOperation,
                                       left: str, right: str) -> 'AST':
        return cls(Node(operation, Node(left), Node(right)))

    @classmethod
    def create_simple_unary_operation(cls, operation: ASTOperation, elem: str) -> 'AST':
        return cls(Node(operation, Node(elem)))

    @classmethod
    def create_binary_operation(cls, operation: ASTOperation, left: Node, right: Node) -> 'AST':
        return cls(Node(operation, left, right))

    @classmethod
    def create_unary_operation(cls, operation: ASTOperation, elem: Node) -> 'AST':
        return cls(Node(operation, elem))

    def to_cnf(self) -> 'AST':
        return convert_into_cnf(self)

    def get_clauses(self) -> list[list[Any]]:
        ast = self.to_cnf()
        return get_clauses(ast)

    def __str__(self) -> str:
        return str(self.root)

    def pretty_str(self) -> str:
        return self.root.pretty_str()


def convert_into_nnf(ast: AST) -> AST:
    ast = simplify_formula(ast)
    return propagate_negation(ast.root)


def convert_into_cnf(ast: AST) -> AST:
    ast = simplify_formula(ast)
    ast = propagate_negation(ast.root)
    return to_cnf(ast)


def simplify_formula(ast: AST) -> AST:
    """Convert a propositional formula to an equivalent formula without '=>', '<=>', 'XOR',
    'REQUIRES', 'EXCLUDES'.

    Adapted from [Büning, Hans Kleine, and Theodor Lettmann.
    Propositional logic: deduction and algorithms. Vol. 48. Cambridge University Press, 1999.]
    """
    logic_op = ast.root.data
    left = ast.root.left
    right = ast.root.right
    if logic_op in (ASTOperation.REQUIRES, ASTOperation.IMPLIES):
        # Replace P => Q with !P v Q.
        left = simplify_formula(AST(left)).root
        right = simplify_formula(AST(right)).root
        result = AST.create_binary_operation(ASTOperation.OR, Node(ASTOperation.NOT, left), right)
    elif logic_op == ASTOperation.EXCLUDES:
        # Replace P EXCLUDES Q with P => !Q.
        left = simplify_formula(AST(left)).root
        right = simplify_formula(AST(right)).root
        result = AST.create_binary_operation(ASTOperation.IMPLIES,
                                             left, Node(ASTOperation.NOT, right))
    elif logic_op == ASTOperation.EQUIVALENCE:
        # Replace P <=> Q with P => Q ∧ Q => P.
        left = simplify_formula(AST.create_binary_operation(ASTOperation.IMPLIES,
                                                            left, right)).root
        right = simplify_formula(AST.create_binary_operation(ASTOperation.IMPLIES,
                                                             right, left)).root
        result = AST.create_binary_operation(ASTOperation.AND, left, right)
    elif logic_op == ASTOperation.XOR:
        # Replace P XOR Q with (P ∧ !Q) v (!P ∧ Q).
        left = simplify_formula(AST.create_binary_operation(ASTOperation.AND,
                                                            left,
                                                            Node(ASTOperation.NOT, right))).root
        left = simplify_formula(AST.create_binary_operation(ASTOperation.AND,
                                                            Node(ASTOperation.NOT, left),
                                                            right)).root
        result = AST.create_binary_operation(ASTOperation.OR, left, right)
    elif logic_op == ASTOperation.AND:
        left = simplify_formula(AST(left)).root
        right = simplify_formula(AST(right)).root
        result = AST.create_binary_operation(ASTOperation.AND, left, right)
    elif logic_op == ASTOperation.OR:
        left = simplify_formula(AST(left)).root
        right = simplify_formula(AST(right)).root
        result = AST.create_binary_operation(ASTOperation.OR, left, right)
    elif logic_op == ASTOperation.NOT:
        left = simplify_formula(AST(left)).root
        result = AST.create_unary_operation(ASTOperation.NOT, left)
    else:
        result = ast
    return result


def to_cnf(formula: AST) -> AST:
    """Convert a propositional formula in NNF to an equivalent formula in conjunctive normal form.

    Adapted and fixed from [Alexander Knüppel. The Role of Complex Constraints in Feature Modeling.
    Master's Thesis. 2016].
    """
    res = formula
    node = formula.root
    if node.data == ASTOperation.AND:
        res = AST.create_binary_operation(ASTOperation.AND,
                                          to_cnf(AST(node.left)).root,
                                          to_cnf(AST(node.right)).root)
    elif node.data == ASTOperation.OR:
        node.left = to_cnf(AST(node.left)).root
        node.right = to_cnf(AST(node.right)).root
        if node.left.data == ASTOperation.AND:
            res = AST.create_binary_operation(ASTOperation.AND,
                                              AST.create_binary_operation(ASTOperation.OR,
                                                                          node.left.left,
                                                                          node.right).root,
                                              AST.create_binary_operation(ASTOperation.OR,
                                                                          node.left.right,
                                                                          node.right).root)
            res = to_cnf(res)
        elif node.right.data == ASTOperation.AND:
            res = AST.create_binary_operation(ASTOperation.AND,
                                              AST.create_binary_operation(ASTOperation.OR,
                                                                          node.left,
                                                                          node.right.left).root,
                                              AST.create_binary_operation(ASTOperation.OR,
                                                                          node.left,
                                                                          node.right.right).root)
            res = to_cnf(res)
        else:
            res = AST.create_binary_operation(ASTOperation.OR, node.left, node.right)
    return res


def to_nnf(ast: AST) -> AST:
    """Convert a simplified propositional formula to an equivalent formula in negation normal form.

    A simplified formula only contains '∧', 'v', and 'not'.

    Adapted from [Alexander Knüppel. The Role of Complex Constraints in Feature Modeling.
    Master's Thesis. 2016].
    """
    return propagate_negation(ast.root)


def propagate_negation(node: Node, negated: bool = False) -> AST:
    result = None
    if node.data == ASTOperation.NOT:
        negated = not negated
        result = propagate_negation(node.left, negated)
    elif node.data == ASTOperation.AND:
        if negated:
            result = AST.create_binary_operation(ASTOperation.OR,
                                                 propagate_negation(node.left, negated).root,
                                                 propagate_negation(node.right, negated).root)
        else:
            result = AST.create_binary_operation(ASTOperation.AND,
                                                 propagate_negation(node.left, negated).root,
                                                 propagate_negation(node.right, negated).root)
    elif node.data == ASTOperation.OR:
        if negated:
            result = AST.create_binary_operation(ASTOperation.AND,
                                                 propagate_negation(node.left, negated).root,
                                                 propagate_negation(node.right, negated).root)
        else:
            result = AST.create_binary_operation(ASTOperation.OR,
                                                 propagate_negation(node.left, negated).root,
                                                 propagate_negation(node.right, negated).root)
    else:
        if negated:
            result = AST.create_unary_operation(ASTOperation.NOT, node)
        else:
            result = AST(node)
    return result


def get_clauses(ast: AST) -> list[list[Any]]:
    """Return the list of clauses represented by the AST root node in conjunctive normal form."""
    node = ast.root
    result = []
    if node.is_term():
        result = [[node.data]]
    elif node.data == ASTOperation.NOT:
        result = [['-' + node.left.data]]
    elif node.data == ASTOperation.OR:
        result = [get_clause_from_or_node(node)]
    elif node.data == ASTOperation.AND:  # Each AND gives us two clauses
        result.extend(get_clauses(AST(node.left)))
        result.extend(get_clauses(AST(node.right)))
    return result


def get_clause_from_or_node(node: Node) -> list[Any]:
    clause = []
    if node.left.is_op() and node.left.data == ASTOperation.OR:
        # recursive OR belongs to the same clause
        clause.extend(get_clause_from_or_node(node.left))
    else:
        term = node.left.data if node.left.is_term() else f'-{node.left.left.data}'
        clause.append(term)
    if node.right.is_op() and node.right.data == ASTOperation.OR:
        # recursive OR belongs to the same clause
        clause.extend(get_clause_from_or_node(node.right))
    else:
        term = node.right.data if node.right.is_term() else f'-{node.right.left.data}'
        clause.append(term)
    return clause
