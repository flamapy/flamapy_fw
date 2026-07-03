from typing import Any, Optional
from enum import Enum

from flamapy.core.exceptions import FlamaException


class ASTOperation(Enum):
    # logical operators
    REQUIRES = "REQUIRES"
    EXCLUDES = "EXCLUDES"
    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    IMPLIES = "IMPLIES"
    NOT = "NOT"
    EQUIVALENCE = "EQUIVALENCE"
    # Comparison operators
    EQUALS = "EQUALS"
    LOWER = "LOWER"
    GREATER = "GREATER"
    LOWER_EQUALS = "LOWER_EQUALS"
    GREATER_EQUALS = "GREATER_EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    # Arithmetic operators
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    # Aggregation operators
    SUM = "SUM"
    AVG = "AVG"
    # Set operators
    LEN = "LEN"
    # Numeric agregation operators
    FLOOR = "FLOOR"
    CEIL = "CEIL"


LOGICAL_OPERATORS = [
    ASTOperation.REQUIRES,
    ASTOperation.EXCLUDES,
    ASTOperation.AND,
    ASTOperation.OR,
    ASTOperation.XOR,
    ASTOperation.IMPLIES,
    ASTOperation.NOT,
    ASTOperation.EQUIVALENCE,
]


ARITHMETIC_OPERATORS = [
    ASTOperation.ADD,
    ASTOperation.SUB,
    ASTOperation.MUL,
    ASTOperation.DIV,
    ASTOperation.EQUALS,
    ASTOperation.LOWER,
    ASTOperation.GREATER,
    ASTOperation.LOWER_EQUALS,
    ASTOperation.GREATER_EQUALS,
    ASTOperation.NOT_EQUALS,
]


AGGREGATION_OPERATORS = [
    ASTOperation.SUM,
    ASTOperation.AVG,
    ASTOperation.LEN,
    ASTOperation.FLOOR,
    ASTOperation.CEIL,
]


class NodeType(Enum):
    """Semantic type of a leaf node in the AST."""
    FEATURE = "Feature"
    LITERAL = "Literal"
    OPERATOR = "Operator"


class Node:
    def __init__(
        self,
        data: Any,
        left: "Node" = None,  # type: ignore[assignment]
        right: "Node" = None,  # type: ignore[assignment]
        node_type: Optional[NodeType] = None,
    ):
        self.data = data
        self.left = left
        self.right = right
        self.node_type = node_type

    def is_term(self) -> bool:
        return not self.is_op()

    def is_op(self) -> bool:
        return isinstance(self.data, ASTOperation)

    def is_unary_op(self) -> bool:
        return self.is_op() and self.data in [ASTOperation.NOT]

    def is_unique_term(self) -> bool:
        return not self.is_op() and self.left is None

    def is_binary_op(self) -> bool:
        return not self.is_unique_term() and not self.is_unary_op() and not self.is_aggregate_op()

    def is_aggregate_op(self) -> bool:
        return self.is_op() and self.data in AGGREGATION_OPERATORS

    def is_feature(self) -> bool:
        """Return True if this node is explicitly marked as a feature reference."""
        return self.node_type == NodeType.FEATURE

    def is_literal(self) -> bool:
        """Return True if this node is a literal value (not a feature reference).

        Falls back to a type-based check for nodes without an explicit node_type.
        """
        if self.node_type is not None:
            return self.node_type == NodeType.LITERAL
        return isinstance(self.data, (int, float))

    def __str__(self) -> str:
        data = self.data.value if self.is_op() else str(self.data)
        if self.left and self.right:
            return f"{data}[{self.left}][{self.right}]"
        if self.left and not self.right:
            return f"{data}[{self.left}][]"
        if not self.left and self.right:
            return f"{data}[][{self.right}]"
        return str(data)

    @staticmethod
    def _get_pretty_str_node(node: "Node") -> str:
        res = ""
        if node.is_op():
            res = f"{node.pretty_str()}"
            if node.is_binary_op():
                res = f"({res})"
        else:
            res = str(node)
        return res

    def pretty_str(self) -> str:
        data = self.data.value if self.is_op() else str(self.data)
        left = Node._get_pretty_str_node(self.left) if self.left is not None else ""
        right = Node._get_pretty_str_node(self.right) if self.right is not None else ""

        if self.is_unique_term():
            res = f"{data}"
        elif self.is_unary_op():
            res = f"{data} {left}"
        elif self.is_aggregate_op():
            if self.right is not None:
                res = f"{data}({left}, {right})"
            else:
                res = f"{data}({left})"  # type: ignore[unreachable]
        else:  # binary operation
            res = f"{left} {data} {right}"
        return res


class AST:
    """Abstract Syntax Tree (AST) to store constraints."""

    def __init__(self, root: Node):
        self.root = root

    @classmethod
    def create_simple_binary_operation(
        cls, operation: ASTOperation, left: str, right: str
    ) -> "AST":
        return cls(Node(operation, Node(left), Node(right)))

    @classmethod
    def create_simple_unary_operation(cls, operation: ASTOperation, elem: str) -> "AST":
        return cls(Node(operation, Node(elem)))

    @classmethod
    def create_binary_operation(cls, operation: ASTOperation, left: Node, right: Node) -> "AST":
        return cls(Node(operation, left, right))

    @classmethod
    def create_unary_operation(cls, operation: ASTOperation, elem: Node) -> "AST":
        return cls(Node(operation, elem))

    def to_cnf(self) -> "AST":
        return convert_into_cnf(self)

    def get_clauses(self, method: str = 'distributive') -> list[list[Any]]:
        """Return the CNF clauses of this AST.

        ``method='distributive'`` (default) uses the classic distributive expansion and
        returns clauses over the formula's own variables. ``method='tseytin'`` uses the
        Tseytin transformation; the returned clauses may contain fresh auxiliary
        variables. Use :meth:`get_clauses_with_aux` when those auxiliary variable names
        are needed (e.g. to register them as non-feature solver variables).
        """
        if method == 'tseytin':
            clauses, _ = tseytin_cnf(self)
            return clauses
        ast = self.to_cnf()
        return get_clauses(ast)

    def get_clauses_with_aux(self, method: str = 'tseytin') -> tuple[list[list[Any]], list[str]]:
        """Return ``(clauses, aux_names)`` for the given CNF ``method``.

        For ``'tseytin'`` this exposes the auxiliary variable names introduced by the
        encoding. For ``'distributive'`` the auxiliary list is always empty.
        """
        if method == 'tseytin':
            return tseytin_cnf(self)
        return get_clauses(self.to_cnf()), []

    def get_operators(self) -> list[ASTOperation]:
        operators = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node is not None:
                if node.is_op():
                    operators.append(node.data)
                if node.is_unary_op():
                    stack.append(node.left)
                elif node.is_binary_op():
                    stack.append(node.right)
                    stack.append(node.left)
        return operators

    def get_operands(self) -> list[Any]:
        operands = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node is not None:
                if node.is_term():
                    operands.append(node.data)
                elif node.is_unary_op():
                    stack.append(node.left)
                elif node.is_binary_op():
                    stack.append(node.right)
                    stack.append(node.left)
        return operands

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
        # Replace P EXCLUDES Q with !P v !Q.
        left = simplify_formula(AST(left)).root
        right = simplify_formula(AST(right)).root
        result = AST.create_binary_operation(
            ASTOperation.OR, Node(ASTOperation.NOT, left), Node(ASTOperation.NOT, right)
        )
    elif logic_op == ASTOperation.EQUIVALENCE:
        # Replace P <=> Q with P => Q ∧ Q => P.
        new_left = simplify_formula(
            AST.create_binary_operation(ASTOperation.IMPLIES, left, right)
        ).root
        new_right = simplify_formula(
            AST.create_binary_operation(ASTOperation.IMPLIES, right, left)
        ).root
        result = AST.create_binary_operation(ASTOperation.AND, new_left, new_right)
    elif logic_op == ASTOperation.XOR:
        # Replace P XOR Q with (P ∧ !Q) v (!P ∧ Q).
        new_left = simplify_formula(
            AST.create_binary_operation(ASTOperation.AND, left, Node(ASTOperation.NOT, right))
        ).root
        new_right = simplify_formula(
            AST.create_binary_operation(ASTOperation.AND, Node(ASTOperation.NOT, left), right)
        ).root
        result = AST.create_binary_operation(ASTOperation.OR, new_left, new_right)
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
        res = AST.create_binary_operation(
            ASTOperation.AND, to_cnf(AST(node.left)).root, to_cnf(AST(node.right)).root
        )
    elif node.data == ASTOperation.OR:
        node.left = to_cnf(AST(node.left)).root
        node.right = to_cnf(AST(node.right)).root
        if node.left.data == ASTOperation.AND:
            res = AST.create_binary_operation(
                ASTOperation.AND,
                AST.create_binary_operation(ASTOperation.OR, node.left.left, node.right).root,
                AST.create_binary_operation(ASTOperation.OR, node.left.right, node.right).root,
            )
            res = to_cnf(res)
        elif node.right.data == ASTOperation.AND:
            res = AST.create_binary_operation(
                ASTOperation.AND,
                AST.create_binary_operation(ASTOperation.OR, node.left, node.right.left).root,
                AST.create_binary_operation(ASTOperation.OR, node.left, node.right.right).root,
            )
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
            result = AST.create_binary_operation(
                ASTOperation.OR,
                propagate_negation(node.left, negated).root,
                propagate_negation(node.right, negated).root,
            )
        else:
            result = AST.create_binary_operation(
                ASTOperation.AND,
                propagate_negation(node.left, negated).root,
                propagate_negation(node.right, negated).root,
            )
    elif node.data == ASTOperation.OR:
        if negated:
            result = AST.create_binary_operation(
                ASTOperation.AND,
                propagate_negation(node.left, negated).root,
                propagate_negation(node.right, negated).root,
            )
        else:
            result = AST.create_binary_operation(
                ASTOperation.OR,
                propagate_negation(node.left, negated).root,
                propagate_negation(node.right, negated).root,
            )
    elif negated:
        result = AST.create_unary_operation(ASTOperation.NOT, node)
    else:
        result = AST(node)
    return result


TSEYTIN_AUX_PREFIX = "__tseytin_"


def _negate_literal(literal: Any) -> Any:
    """Flip the sign of a CNF literal that uses the ``"-name"`` string convention."""
    if isinstance(literal, str) and literal.startswith("-"):
        return literal[1:]
    return "-" + str(literal)


def _tseytin_gate_clauses(op: ASTOperation, gate: Any, a: Any, b: Any) -> list[list[Any]]:
    """Biconditional clauses encoding ``gate <=> (a op b)`` for a binary logical ``op``.

    ``a`` and ``b`` are literals; ``gate`` is the fresh auxiliary literal. Encoding each
    connective directly (rather than expanding it first) is what keeps the transformation
    linear in the formula size.
    """
    g, na, nb, ng = gate, _negate_literal(a), _negate_literal(b), _negate_literal(gate)
    if op == ASTOperation.AND:
        return [[ng, a], [ng, b], [g, na, nb]]
    if op == ASTOperation.OR:
        return [[g, na], [g, nb], [ng, a, b]]
    if op in (ASTOperation.IMPLIES, ASTOperation.REQUIRES):  # a -> b  ==  (not a) or b
        return [[g, a], [g, nb], [ng, na, b]]
    if op == ASTOperation.EXCLUDES:  # (not a) or (not b)
        return [[g, a], [g, b], [ng, na, nb]]
    if op == ASTOperation.EQUIVALENCE:  # a <-> b
        return [[ng, na, b], [ng, a, nb], [g, a, b], [g, na, nb]]
    if op == ASTOperation.XOR:  # a xor b
        return [[ng, a, b], [ng, na, nb], [g, na, b], [g, a, nb]]
    raise FlamaException(
        f"Operation '{op}' is not a propositional connective supported by the Tseytin "
        f"transformation."
    )


def tseytin_cnf(ast: AST) -> tuple[list[list[Any]], list[str]]:
    """Return an equisatisfiable CNF of ``ast`` using the Tseytin transformation.

    Unlike the distributive :func:`to_cnf`, this produces a CNF whose size is linear
    in the size of the formula by introducing one fresh auxiliary variable per gate.
    Each logical connective is encoded directly (no distributive expansion), so formulas
    that blow up under :func:`to_cnf` (XOR chains, wide equivalences) stay compact. Gates
    are encoded as full biconditionals (``g <=> subformula``) so that every model of the
    original formula extends to exactly one model of the encoding; this preserves model
    counts and configuration enumeration (once auxiliary variables are projected out).

    Returns a tuple ``(clauses, aux_names)`` where ``clauses`` is a list of clauses
    (each a list of literals in the same ``"-name"`` string convention as
    :func:`get_clauses`) and ``aux_names`` lists every auxiliary variable name
    introduced (each prefixed with :data:`TSEYTIN_AUX_PREFIX`) so callers can register
    them as solver variables that are not features.

    Raises :class:`FlamaException` if the formula contains a non-propositional operator
    (arithmetic, comparison or aggregation).
    """
    clauses: list[list[Any]] = []
    aux_names: list[str] = []
    counter = [0]

    def literal_of(node: Node) -> Any:
        if node.is_term():
            return node.data
        if node.data == ASTOperation.NOT:
            # Negation of a single literal is free; no gate needed.
            return _negate_literal(literal_of(node.left))
        left_lit = literal_of(node.left)
        right_lit = literal_of(node.right)
        counter[0] += 1
        gate = f"{TSEYTIN_AUX_PREFIX}{counter[0]}"
        aux_names.append(gate)
        clauses.extend(_tseytin_gate_clauses(node.data, gate, left_lit, right_lit))
        return gate

    root_literal = literal_of(ast.root)
    clauses.append([root_literal])  # assert the whole formula is true
    return clauses, aux_names


def get_clauses(ast: AST) -> list[list[Any]]:
    """Return the list of clauses represented by the AST root node in conjunctive normal form."""
    node = ast.root
    result = []
    if node.is_term():
        result = [[node.data]]
    elif node.data == ASTOperation.NOT:
        result = [["-" + node.left.data]]
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
        term = node.left.data if node.left.is_term() else f"-{node.left.left.data}"
        clause.append(term)
    if node.right.is_op() and node.right.data == ASTOperation.OR:
        # recursive OR belongs to the same clause
        clause.extend(get_clause_from_or_node(node.right))
    else:
        term = node.right.data if node.right.is_term() else f"-{node.right.left.data}"
        clause.append(term)
    return clause
