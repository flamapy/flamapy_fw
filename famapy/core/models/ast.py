from typing import Optional, Any
from enum import Enum


class ASTOperation(Enum):
    REQUIRES = 'REQUIRES'
    EXCLUDES = 'EXCLUDES'
    AND = 'AND'
    OR = 'OR'
    IMPLIES = 'IMPLIES'
    NOT = 'NOT'   
    EQUIVALENCE = 'EQUIVALENCE'


class Node:

    def __init__(self, data: Any):
        self.left: Optional['Node'] = None  # pylint: disable=unsubscriptable-object
        self.right: Optional['Node'] = None  # pylint: disable=unsubscriptable-object
        self.data = data

    def is_feature(self) -> bool:
        return not self.is_op()

    def is_op(self) -> bool:
        return isinstance(self.data, ASTOperation)

    def __str__(self) -> str:
        data = self.data.name if self.is_op() else self.data
            
        if self.left and self.right:
            return f'{data}[{self.left}][{self.right}]'

        if self.left and not self.right:
            return f'{data}[{self.left}][]'

        if not self.left and self.right:
            return f'{data}[][{self.right}]'

        return str(data)


class AST:

    def __init__(self, root: Node):
        self.root = root

    @classmethod
    def create_simple_binary_operation(cls, operation: ASTOperation, 
                                       left: str, right: str) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = Node(left)
        ast.root.right = Node(right)
        return ast

    @classmethod
    def create_simple_unary_operation(cls, operation: ASTOperation, elem: str) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = Node(elem)
        return ast

    @classmethod
    def create_binary_operation(cls, operation: ASTOperation, left: Node, right: Node) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = left
        ast.root.right = right
        return ast

    @classmethod
    def create_unary_operation(cls, operation: ASTOperation, elem: Node) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = elem
        return ast

    def to_cnf(self) -> 'AST':
        return convert_into_cnf(self)

    def get_clauses(self) -> list[list[Any]]:
        ast = self.to_cnf()
        clauses = get_clauses(ast.root)
        if len(clauses) > 0 and not isinstance(clauses[0], list):
            return [clauses]
        return clauses

    def __str__(self) -> str:
        return str(self.root)


def convert_into_cnf(ast: AST) -> AST:
    """Convert to negation normal form.

    Three steps are performed:
      1. Eliminate implications, equivalences, and excludes.
      2. Move NOTs inwards by repeatdly applying De Morgan's Law and eliminate doble negations.
      3. Distribute ORs invwards over ANDs, applying the Distribute property.
    """
    ast = eliminate_complex_operators(ast)
    ast = move_nots_inwards(ast)
    ast  = distribute_ors(ast)
    return ast

def eliminate_implication(node: Node) -> Node:
    """Replace P => Q with !P ∨ Q."""
    left = AST.create_unary_operation(ASTOperation.NOT, node.left).root
    return AST.create_binary_operation(ASTOperation.OR, left, node.right).root

def eliminate_equivalence(node: Node) -> Node:
    """Replace P <=> Q with (P ∨ !Q) ∧ (!P ∨ Q)."""
    pnot = AST.create_unary_operation(ASTOperation.NOT, node.left).root
    qnot = AST.create_unary_operation(ASTOperation.NOT, node.right).root
    left = AST.create_binary_operation(ASTOperation.OR, node.left, qnot).root 
    right = AST.create_binary_operation(ASTOperation.OR, pnot, node.right).root 
    return AST.create_binary_operation(ASTOperation.AND, left, right).root 

def eliminate_exclusion(node: Node) -> Node:
    """Replace P EXCLUDES !Q with !P ∨ !Q."""
    left = AST.create_unary_operation(ASTOperation.NOT, node.left).root
    right = AST.create_unary_operation(ASTOperation.NOT, node.right).root
    return AST.create_binary_operation(ASTOperation.OR, left, right).root 

def eliminate_complex_operators(ast: AST) -> AST:
    """Eliminate implications, equivalences, and excludes"""
    node = ast.root
    if node is None or not node.is_op():
        return ast
    new_node = None
    if node.data == ASTOperation.REQUIRES or node.data == ASTOperation.IMPLIES:
        new_node = eliminate_implication(node)
    elif node.data == ASTOperation.EQUIVALENCE:
        new_node = eliminate_equivalence(node)
    elif node.data == ASTOperation.EXCLUDES:
        new_node = eliminate_exclusion(node)
    elif node.data == ASTOperation.NOT:
        new_node = eliminate_complex_operators(AST(node.left)).root
    else:
        node.left = eliminate_complex_operators(AST(node.left)).root
        node.right = eliminate_complex_operators(AST(node.right)).root
        return AST(node)
    return AST(new_node)

def apply_demorganlaw(node: Node, operation: ASTOperation) -> Node:
    """Apply De Morgan's Law.
        
    If operation is AND, replace !(P ∨ Q) with (!P) ∧ (!Q);
    if operation is OR, replace !(P ∧ Q) with (!P) ∨ (!Q).
    """
    left = AST.create_unary_operation(ASTOperation.NOT, node.left).root
    right = AST.create_unary_operation(ASTOperation.NOT, node.right).root
    new_node = AST.create_binary_operation(operation, left, right).root
    return new_node

def move_nots_inwards(ast: AST) -> AST:
    """Move NOTs inwards by repeatedly applying De Morgan's Law, 
    and eliminate doble negations by replacing !!P with P.
    """
    node = ast.root
    if node is None or not node.is_op():
        return ast
    if node.data != ASTOperation.NOT:
        node.left = move_nots_inwards(AST(node.left)).root
        node.right = move_nots_inwards(AST(node.right)).root
        return AST(node)
    else:
        if not node.left.is_op():
            return AST(node)
        else:
            new_node = None
            if node.left.data == ASTOperation.OR:
                new_node = apply_demorganlaw(node.left, ASTOperation.AND)
            elif node.left.data == ASTOperation.AND:
                new_node = apply_demorganlaw(node.left, ASTOperation.OR)
            elif node.left.data == ASTOperation.NOT:
                # Eliminate doble negation
                new_node = node.left.left
            return move_nots_inwards(AST(new_node))

def apply_distribution(node: Node, and_node: Node) -> Node:
    """Apply distribution property.
    
    Replace P ∨ (Q ∧ R) with (P ∨ Q) ∧ (P ∨ R).
    """
    left = AST.create_binary_operation(ASTOperation.OR, node, and_node.left).root
    right = AST.create_binary_operation(ASTOperation.OR, node, and_node.right).root
    return AST.create_binary_operation(ASTOperation.AND, left, right).root

def distribute_ors(ast: AST) -> AST:
    """Distribute ORs inwards over ANDs."""
    node = ast.root
    if node is None or not node.is_op():
        return ast
    if node.data != ASTOperation.OR:
        node.left = distribute_ors(AST(node.left)).root
        node.right = distribute_ors(AST(node.right)).root
        return AST(node)
    else:
        new_node = None
        if not node.left.is_op() and not node.right.is_op():
            return AST(node)

        if node.left.is_op():
            if node.left.data == ASTOperation.AND:
                new_node = apply_distribution(node.right, node.left)
                return distribute_ors(AST(new_node))
        
        if node.right.is_op():
            if node.right.data == ASTOperation.AND:
                new_node = apply_distribution(node.left, node.right) 
                return distribute_ors(AST(new_node))
        
        if new_node is None:
            node.left = distribute_ors(AST(node.left)).root
            node.right = distribute_ors(AST(node.right)).root
            return AST(node)

def get_clauses(node: Node) -> list[list[Any]]:
    """Return the list of clauses represented by the AST root node in normal conjuntive form."""
    if node is None or not node.is_op():
        return []
    if node.data == ASTOperation.AND:  # Each AND gives us two clauses
        clauses = []
        clauses_left = get_clauses(node.left)  # Recursive AND
        # recursive ANDs may introduce additional clauses
        if len(clauses_left) > 0 and isinstance(clauses_left[0], list):  
            for c in clauses_left:
                clauses.append(c)
        else:
            clauses.append(clauses_left)

        clauses_right = get_clauses(node.right)  # Recursive AND
        # recursive ANDs may introduce additional clauses
        if len(clauses_right) > 0 and isinstance(clauses_right[0], list):  
            for c in clauses_right:
                clauses.append(c)
        else:
            clauses.append(clauses_right)
        return clauses
    if node.data == ASTOperation.NOT:
        return ['-' + node.left.data]
    if node.data == ASTOperation.OR:
        clause = []
        if node.left.is_op():
            clause += get_clauses(node.left)  # recursive OR belongs to the same clause
        else:
            clause.append(node.left.data)
        if node.right.is_op():
            clause += get_clauses(node.right)  # recursive OR belongs to the same clause
        else:
            clause.append(node.right.data)
        return clause
    return []
