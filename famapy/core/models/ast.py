from typing import Any, List, Optional

class Node:
    operations =["requires","excludes", "and", "or", "implies", "not"]
    
    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data

    def is_feature(self):
        return not self.is_op()

    def is_op(self):
        return isinstance(self.data, str) and ( self.data in Node.operations )
    
    def __str__(self):
        return str(self.data)

class AST:
    
    def __init__(self, root):
        self.root = Node(root)

    @staticmethod
    def create_binary_operation(op,left,right):
        ast = AST(op)
        ast.root.left=Node(left)
        ast.root.right=Node(right)
        return ast

    @staticmethod
    def create_unary_operation(op,elem):
        ast = AST(op)
        ast.left=elem
        return ast

    def __str__(self):
        return str(self.root) + str(self.root.left) + str(self.root.right)