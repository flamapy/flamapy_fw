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
    def create_simple_binary_operation(cls, operation: ASTOperation, left: str, right: str) -> 'AST':
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


    def __str__(self) -> str:
        return str(self.root)
