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
        #We check if the op is available by comparing it on mayus
        return (isinstance(self.data, str) and 
            ( self.data.upper() in (op.upper() for op in Node.operations )))
    
    def __str__(self):
        if ( self.left and self.right):
            return str(self.data) + '\r\n/ ' + '\\\r\n' +  str(self.left) +str(self.right) 
        elif (self.left and not self.right):
            return str(self.data) + '\r\n/ '  +  str(self.left) 
        elif (not self.left and self.right):
            return str(self.data) + '\\\r\n'  +str(self.right) 
        else:
            return str(self.data)
class AST:
    
    def __init__(self, root):
        self.root = Node(root)

    @staticmethod
    def create_simple_binary_operation(op,left,right):
        ast = AST(op)
        ast.root.left=Node(left)
        ast.root.right=Node(right)
        return ast

    @staticmethod
    def create_simple_unary_operation(op,elem):
        ast = AST(op)
        ast.left=elem
        return ast

    def __str__(self):
        return str(self.root)