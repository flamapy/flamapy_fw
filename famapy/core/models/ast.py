from typing import Optional


class Node:
    operations = ['requires', 'excludes', 'and', 'or', 'implies', 'not', 'equivalence']

    def __init__(self, data: str):
        self.left: Optional['Node'] = None  # pylint: disable=unsubscriptable-object
        self.right: Optional['Node'] = None  # pylint: disable=unsubscriptable-object
        self.data = data

    def is_feature(self) -> bool:
        return not self.is_op()

    def is_op(self) -> bool:
        ''' We check if the operation is available by comparing it on mayus '''
        return (
            isinstance(self.data, str) and
            (self.data.upper() in (operation.upper() for operation in Node.operations))
        )

    def __str__(self) -> str:
        if self.left and self.right:
            return f'{self.data}[{self.left}][{self.right}]'

        if self.left and not self.right:
            return f'{self.data}[{self.left}][]'

        if not self.left and self.right:
            return f'{self.data}[][{self.right}]'

        return str(self.data)


class AST:

    def __init__(self, root: Node):
        self.root = root

    @classmethod
    def create_simple_binary_operation(cls, operation: str, left: str, right: str) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = Node(left)
        ast.root.right = Node(right)
        return ast

    @classmethod
    def create_simple_unary_operation(cls, operation: str, elem: str) -> 'AST':
        ast = cls(Node(operation))
        ast.root.left = Node(elem)
        return ast

    def __str__(self) -> str:
        return str(self.root)


def convert_into_cnf(ast: AST) -> AST:
    # 1. Convert to negation normal form
    # 1.1. Eliminate implications, equivalences, and excludes
    # 1.2. Move NOTs inwards by repeatdly applying De Morgan's Law and eliminate doble negations.
    # 2. Distribute ORs invwards over ANDs, applying the Distribute property
    ast =  eliminate_complex_operators(ast)


def eliminate_implication(node: Node) -> Node:
    """Replace P => Q with !P ∨ Q."""
    pnot_node = Node("NOT")
    pnot_node.left = node.left
    new_node = Node("OR")
    new_node.left = pnot_node
    new_node.right = node.right
    return new_node

def eliminate_equivalence(node: Node) -> Node:
    """Replace P <=> Q with (P ∨ !Q) ∧ (!P ∨ Q)."""
    qnot_node = Node("NOT")
    qnot_node.left = node.right 
    pnot_node = Node("NOT")
    pnot_node.left = node.left

    left_node = Node("OR")
    left_node.left = node.left 
    left_node.right = qnot_node

    right_node = Node("OR")
    right_node.left = pnot_node 
    right_node.right = node.right

    new_node = Node("AND")
    new_node.left = left_node
    new_node.right = right_node
    return new_node

def eliminate_exclusion(node: Node) -> Node:
    """Replace P => !Q with !P ∨ !Q."""
    pnot_node = Node("NOT")
    pnot_node.left = node.left
    qnot_node = Node("NOT")
    qnot_node.left = node.right
    new_node = Node("OR")
    new_node.left = pnot_node
    new_node.right = qnot_node
    return new_node

def eliminate_complex_operators(ast: AST) -> AST:
    """Eliminate imlications, equivalences, and excludes.

    Repeatedly replace P => Q with !P ∨ Q; 
    replace P <=> Q with (P ∨ !Q) ∧ (!P ∨ Q);
    and replace P => !Q with !P ∨ !Q.
    """
    node = ast.root
    stack = []
    stack.append(node)
    root = None
    while stack:
        n = stack.pop()
        if n.is_op():
            new_node = None
            if n.data.upper() == 'REQUIRES' or n.data.upper() == 'IMPLIES':
                new_node = eliminate_implication(n)
            elif n.data.upper() == 'EQUIVALENCE':
                new_node = eliminate_implication(n)
            elif n.data.upper() == 'EXCLUDES':
                new_node = eliminate_exclusion(n)
            elif n.data.upper() == 'NOT':
                stack.append(n.left)
            else:  # OR, AND nodes
                stack.append(n.left)
                stack.append(n.right)

            if new_node is not None:
                stack.append(new_node.left)
                stack.append(new_node.right)
            
            if root is None:
                if new_node is not None:
                    root = new_node
                else:
                    root = n
    return AST(root)

def apply_demorganlaw_or(node: Node) -> Node:
    """Replace !(P ∨ Q) with (!P) ∧ (!Q)."""
    pnot_node = Node("NOT")
    pnot_node.left = node.left 
    qnot_node = Node("NOT")
    qnot_node.left = node.right
    new_node = Node("AND")
    new_node.left = pnot_node 
    new_node.right = qnot_node
    return new_node

def apply_demorganlaw_and(node: Node) -> Node:
    """Replace !(P ∧ Q) with (!P) ∨ (!Q)."""
    pnot_node = Node("NOT")
    pnot_node.left = node.left 
    qnot_node = Node("NOT")
    qnot_node.left = node.right
    new_node = Node("OR")
    new_node.left = pnot_node 
    new_node.right = qnot_node
    return new_node

def move_nots_inwards(ast: AST) -> AST:
    """Move NOTs inwards by repeatedly applying De Morgan's Law, and eliminate doble negations.
    
    Specifically, replace !(P ∨ Q) with (!P) ∧ (!Q);
    replace !(P ∧ Q) with (!P) ∨ (!Q);
    and replace !!P with P.
    """
    node = ast.root
    stack = []
    stack.append(node)
    root = None
    while stack:
        n = stack.pop()
        if n.is_op():
            new_node = None
            if n.data.upper() == 'NOT':
                if n.left.is_op():
                    if n.left.data.upper() == 'OR':
                        new_node = apply_demorganlaw_or(n.left)
                    elif n.left.data.upper() == 'AND':
                        new_node = apply_demorganlaw_and(n.left)
                    elif n.left.data.upper() == 'NOT':
                        # Eliminate doble negation
                        new_node = n.left.left
                    else:  # OR, AND nodes
                        stack.append(n.left)
                        stack.append(n.right)

            if new_node is not None:
                stack.append(new_node.left)
                stack.append(new_node.right)
            
            if root is None:
                if new_node is not None:
                    root = new_node
                else:
                    root = n

    return AST(root)
