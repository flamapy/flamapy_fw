import itertools

from flamapy.core.models.ast import (
    AST,
    ASTOperation,
    Node,
    convert_into_cnf,
    simplify_formula,
    tseytin_cnf,
    TSEYTIN_AUX_PREFIX,
)


def evaluate(node: Node, assignment: dict[str, bool]) -> bool:
    """Evaluate a propositional formula over AND/OR/NOT and variable terminals."""
    if node.is_term():
        return assignment[node.data]
    if node.data == ASTOperation.NOT:
        return not evaluate(node.left, assignment)
    if node.data == ASTOperation.AND:
        return evaluate(node.left, assignment) and evaluate(node.right, assignment)
    if node.data == ASTOperation.OR:
        return evaluate(node.left, assignment) or evaluate(node.right, assignment)
    raise ValueError(f"Unexpected operation after simplification: {node.data}")


def assert_equivalent_to(ast: AST, expected: dict[tuple[bool, bool], bool]) -> None:
    for transform in (simplify_formula, convert_into_cnf):
        result = transform(ast)
        for val_a, val_b in itertools.product([True, False], repeat=2):
            assignment = {'A': val_a, 'B': val_b}
            assert evaluate(result.root, assignment) == expected[(val_a, val_b)], (
                f"{transform.__name__}: wrong value for A={val_a}, B={val_b}"
            )


def test_simplify_xor() -> None:
    ast = AST.create_binary_operation(ASTOperation.XOR, Node('A'), Node('B'))
    assert_equivalent_to(ast, {
        (True, True): False,
        (True, False): True,
        (False, True): True,
        (False, False): False,
    })


def test_simplify_equivalence() -> None:
    ast = AST.create_binary_operation(ASTOperation.EQUIVALENCE, Node('A'), Node('B'))
    assert_equivalent_to(ast, {
        (True, True): True,
        (True, False): False,
        (False, True): False,
        (False, False): True,
    })


def test_simplify_implies() -> None:
    ast = AST.create_binary_operation(ASTOperation.IMPLIES, Node('A'), Node('B'))
    assert_equivalent_to(ast, {
        (True, True): True,
        (True, False): False,
        (False, True): True,
        (False, False): True,
    })


# --- Tseytin transformation ---------------------------------------------------

def _eval_clauses(clauses: list, assignment: dict[str, bool]) -> bool:
    """Evaluate CNF clauses (``"-name"`` literal convention) under a full assignment."""
    for clause in clauses:
        satisfied = False
        for literal in clause:
            if literal.startswith('-'):
                if not assignment[literal[1:]]:
                    satisfied = True
                    break
            elif assignment[literal]:
                satisfied = True
                break
        if not satisfied:
            return False
    return True


def _feature_vars(clauses: list) -> list[str]:
    names = set()
    for clause in clauses:
        for literal in clause:
            name = literal[1:] if literal.startswith('-') else literal
            if not name.startswith(TSEYTIN_AUX_PREFIX):
                names.add(name)
    return sorted(names)


def assert_model_preserving(ast: AST, variables: list[str]) -> None:
    """Every original model extends to exactly one Tseytin model; non-models to zero."""
    clauses, aux_names = tseytin_cnf(ast)
    reference = simplify_formula(ast).root
    for feat_bits in itertools.product([True, False], repeat=len(variables)):
        feat_assign = dict(zip(variables, feat_bits))
        expected = evaluate(reference, feat_assign)
        extensions = 0
        for aux_bits in itertools.product([True, False], repeat=len(aux_names)):
            assignment = {**feat_assign, **dict(zip(aux_names, aux_bits))}
            if _eval_clauses(clauses, assignment):
                extensions += 1
        assert extensions == (1 if expected else 0), (
            f"{feat_assign}: expected {int(expected)} extensions, got {extensions}"
        )


def _xor_chain(variables: list[str]) -> AST:
    node = Node(variables[0])
    for name in variables[1:]:
        node = Node(ASTOperation.XOR, node, Node(name))
    return AST(node)


def test_tseytin_preserves_models_xor() -> None:
    assert_model_preserving(_xor_chain(['A', 'B', 'C']), ['A', 'B', 'C'])


def test_tseytin_preserves_models_mixed() -> None:
    # (A <=> B) AND (C => (A OR D))
    left = Node(ASTOperation.EQUIVALENCE, Node('A'), Node('B'))
    right = Node(ASTOperation.IMPLIES, Node('C'), Node(ASTOperation.OR, Node('A'), Node('D')))
    assert_model_preserving(AST(Node(ASTOperation.AND, left, right)), ['A', 'B', 'C', 'D'])


def test_tseytin_single_literal_has_no_aux() -> None:
    clauses, aux_names = tseytin_cnf(AST(Node('A')))
    assert aux_names == []
    assert clauses == [['A']]


def test_tseytin_is_linear_where_distributive_explodes() -> None:
    # Parity's distributive CNF grows exponentially (2^(n-1) clauses); keep n small
    # enough that the distributive expansion still terminates for the comparison.
    variables = ['v0', 'v1', 'v2', 'v3', 'v4']
    ast = _xor_chain(variables)
    distributive = ast.get_clauses(method='distributive')
    tseytin, aux_names = tseytin_cnf(ast)
    # Tseytin stays linear in the gate count while distributive is already larger here.
    assert len(tseytin) <= 6 * len(variables)
    assert len(tseytin) < len(distributive)
    assert _feature_vars(tseytin) == variables
