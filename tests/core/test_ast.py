from famapy.core.ast import ast

class TestAST:

    ast1 = FamaAST("not A implies B and not D excludes F and J requires B")
    print(ast1)

    ast2 = FamaAST("A excludes B")
    print(ast2)

    ast3 = FamaAST("(A and B) and C")
    print(ast3)

TestAST()