from typing import Optional


class Node:
    operations = ['requires', 'excludes', 'and', 'or', 'implies', 'not']

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
            return f'{self.data}\r\n/ \\\r\n{self.left}{self.right}'

        if self.left and not self.right:
            return f'{self.data}\r\n/ {self.left}'

        if not self.left and self.right:
            return f'{self.data}\\\r\n{self.right}'

        return str(self.data)


class AST:

    def __init__(self, root: str):
        self.root = Node(root)

    @classmethod
    def create_simple_binary_operation(cls, operation: str, left: str, right: str) -> 'AST':
        ast = cls(operation)
        ast.root.left = Node(left)
        ast.root.right = Node(right)
        return ast

    @classmethod
    def create_simple_unary_operation(cls, operation: str, elem: str) -> 'AST':
        ast = cls(operation)
        ast.root.left = Node(elem)
        return ast

    def __str__(self) -> str:
        return str(self.root)
