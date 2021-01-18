import math

class FamaAST():

    unary_operators = ["not"]
    binary_operators = ["&&","&","||","|","and","or","implies","excludes","requires"]
    constraints = ["implies","excludes","requires"]

    string = ""
    nodes = []
    list = []


    def __init__(self,string=""):
        self.string = string
        self.nodes = []
        self.list = self.generate_list(string)
        self.generate()

    def generate_list(self,string):
        processed_string = ""
        characters = []
        for i in range(len(string)):
            c = string[i]
            if c == "(" or c == ")":
                characters.append(" ")
            characters.append(c)
        processed_string = processed_string.join(characters)
        return list(processed_string.split(" "))

    def node(self):
        return 0

    def __str__(self):
        return "\n--> Printing AST: \"" + self.string + "\"" + self.print_tree(self.get_root(),"\n\n" + self.get_root().get_name())

    def print_tree(self,node,string):

        childs_nodes = self.get_childs(node)
        for n in childs_nodes:
            string = string + self.print_tree(n,"\n"  + self.print_tabs(n) + n.get_name())

        return string

    def print_tabs(self,node):
        level = node.get_level()
        tabs = ""
        for i in range(level):
            tabs = tabs + "\t"
        return tabs

    def height(self):
        # TODO
        return 1

    def generate(self):
        # get root node
        parent_item = self.find_parent_item(0,len(self.list))
        name_node = self.list[parent_item]
        token = parent_item
        node = Node(token=token,is_root=True,binary_operator=True,operator=name_node,level=1)
        self.nodes.append(node)

        # explore the tree
        self.explore(0,parent_item,points_to=parent_item,level=1)
        self.explore(parent_item+1,len(self.list),points_to=parent_item,level=1)


    def explore(self,i,j,points_to,level):

        parent_item = self.find_parent_item(i,j)
        name_node = self.list[parent_item]
        token = parent_item

        if name_node in self.binary_operators:
            node = Node(token=token,binary_operator=True,points_to=points_to, operator=name_node,level=level)
            self.nodes.append(node)
            self.explore(i,parent_item,parent_item,level+1)
            self.explore(parent_item+1,j,parent_item,level+1)

        #elif name_node in self.unary_operators:
        elif self.list[i] in self.unary_operators:
            node_feature = Node(token=token,is_feature=True, feature=self.list[i+1], points_to=points_to,level=level)
            # TODO arreglar
            node_unary = Node(token=234342,is_leaf=True, unary_operator=True, points_to=token, operator=self.list[i],level=level+1)
            self.nodes.append(node_feature)
            self.nodes.append(node_unary)

        else:
            node = Node(token=token,is_leaf=True,is_feature=True, feature=name_node, points_to=points_to,level=level)
            self.nodes.append(node)
            
    # auxiliary methods
    def find_parent_item(self,i,j):

        item = self.find_and_op_index(i,j)

        if(item == -1):
            item = self.find_or_op_index(i,j)
        
        if(item == -1):
            item = self.find_first_op_index(i,j)

        if(item == -1):
            item = self.find_not_op_index(i,j)

        if(item == -1):
            item = self.find_feature_index(i,j)

        return item

    def find_and_op_index(self,i,j):
        for item in range(i,j):
            name_node = self.list[item]
            if(name_node == "and" or name_node == "AND" or name_node == "&&" or name_node == "&"):
                return item
        return -1

    def find_or_op_index(self,i,j):
        for item in range(i,j):
            name_node = self.list[item]
            if(name_node == "or" or name_node == "OR" or name_node == "||" or name_node == "|"):
                return item
        return -1

    def find_first_op_index(self,i,j):
        for item in range(i,j):
            name_node = self.list[item]
            if name_node in self.constraints:
                return item
        return -1

    def find_not_op_index(self,i,j):
        for item in range(i,j):
            name_node = self.list[item]
            if(name_node == "not" or name_node == "NOT"):
                return item
        return -1

    def find_feature_index(self,i,j):
        for item in range(i,j):
            name_node = self.list[item]
            if not name_node in self.constraints and not name_node in self.unary_operators and not name_node in self.binary_operators:
                return item
        return -1

    # common methods
    def get_nodes_by_feature(self,feature):
        res_node = []
        for node in self.nodes:
            if node.get_name() == feature:
                res_node.append(node)
        return res_node

    def get_root(self):
        res_node = None
        for node in self.nodes:
            if node.is_root:
                res_node = node
                break
        return res_node

    def get_childs(self,parent_node):
        childs = []
        points_to = parent_node.get_token()
        for node in self.nodes:
            if node.get_points_to() == str(points_to):
                childs.append(node)
        return childs

    def get_nodes(self):
        return self.nodes
        
class Node():

    token = None

    is_root = False
    is_leaf = False
    feature = ""
    is_feature = False
    unary_operator = False
    binary_operator = False
    points_to = None
    operator = ""

    level = 0

    def __init__(self,token=None,is_root=False,is_leaf=False,feature="",is_feature=False,unary_operator=False,binary_operator=False,points_to=None,operator="",level=0):
        self.token = token
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.feature = feature
        self.is_feature = is_feature
        self.unary_operator = unary_operator
        self.binary_operator = binary_operator
        self.points_to = points_to
        self.operator = operator
        self.level = level

    def is_leaf(self):
        return self.is_leaf

    def is_root(self):
        return self.points_to == None

    def get_token(self):
        return self.token

    def get_points_to(self):
        return str(self.points_to)

    def get_name(self):
        if self.is_feature:
            return self.feature
        else:
            return self.operator

    def get_level(self):
        return self.level

    def __str__(self):
        string = ""
        if self.is_feature:
            string = string + self.feature
        else:
            string = string + self.operator

        return string

#if __name__ == "__main__":
#    main()