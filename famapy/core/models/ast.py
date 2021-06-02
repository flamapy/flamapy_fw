from typing import Any, List, Optional


class Node:  # noqa
    def __init__(  # noqa
        self,
        token: int,
        is_leaf: bool = False,
        feature: str = "",
        is_feature: bool = False,
        unary_operator: bool = False,
        binary_operator: bool = False,
        points_to: Any = None, operator: str = "",
        level: int = 0
    ):

        self._token = token  # _ meaning private in python
        self.is_leaf = is_leaf
        self.feature = feature
        self.is_feature = is_feature
        self.unary_operator = unary_operator
        self.binary_operator = binary_operator
        self.points_to = points_to
        self.operator = operator
        self.level = level

    @property
    def token(self) -> Any:
        return self._token

    def is_root(self) -> bool:
        return self.points_to is None

    def get_points_to(self) -> str:
        if self.points_to is None:
            return "None"
        return str(self.points_to)

    def get_name(self) -> str:
        name = ""
        if self.is_feature:
            name = self.feature
        else:
            name = self.operator

        return name

    def get_level(self) -> int:
        return self.level

    def __str__(self) -> str:
        return (
            f'Node: {self.get_name()}, '
            f'points to: {self.get_points_to()}, '
            f'token: {self._token}, '
            f'level: {self.get_level()}'
        )


class ASTINFO:
    unary_operators = ["not"]
    binary_operators = ["or", "and", "implies", "excludes", "requires"]

    @staticmethod
    def get_unary_operators() -> List[str]:
        return ASTINFO.unary_operators

    # TODO: use list as variable is not correct
    @staticmethod
    def set_unary_operators(operators: List[str]) -> None:
        ASTINFO.unary_operators = operators

    @staticmethod
    def get_binary_operators() -> List[str]:
        return ASTINFO.binary_operators

    @staticmethod
    def set_binary_operators(operators: List[str]) -> None:
        ASTINFO.binary_operators = operators


class ASTCHECK:

    @staticmethod
    def check_all(string: str) -> None:

        ASTCHECK.check_is_empty(string)
        ASTCHECK.check_parentheses(string)
        ASTCHECK.check_empty_parentheses(string)
        ASTCHECK.check_binary_operator_at_start_or_end(string)
        ASTCHECK.check_unary_operator_at_end(string)
        ASTCHECK.check_adjacent_binary_operators(string)
        ASTCHECK.check_adjacent_unary_plus_binary_operators(string)
        ASTCHECK.check_adjacent_features(string)
        ASTCHECK.check_binary_operator_preceded_or_succeeded_by_parentheses(string)
        ASTCHECK.check_unary_operator_succeeded_by_parentheses(string)

    @staticmethod
    def raise_syntax_error(string: str, element1: str = "", element2: str = "") -> None:

        raise_string = "SyntaxError: " + string

        if element1:
            raise_string += " " + element1

        if element2:
            raise_string += " " + element2

        raise SyntaxError(raise_string)

    @staticmethod
    def check_is_empty(string: str) -> None:

        if not bool(string.strip()):
            raise ValueError("ValueError: Empty string")

    @staticmethod
    def check_parentheses(string: str) -> None:

        count_open_parentheses = ASTUtilities.count_repeating_characters(string, "(")
        count_close_parentheses = ASTUtilities.count_repeating_characters(string, ")")

        if count_open_parentheses != count_close_parentheses:
            ASTCHECK.raise_syntax_error(
                "There is not the same number of open parentheses as closed ones"
            )

    @staticmethod
    def check_adjacent_binary_operators(string: str) -> None:

        string_list = ASTUtilities.string2list(string)

        for i in range(0, len(string_list) - 1):

            fist_item = ASTUtilities.clean_parentheses(string_list[i])
            second_item = ASTUtilities.clean_parentheses(string_list[i + 1])

            if (ASTUtilities.is_binary_operator(fist_item) and
                    ASTUtilities.is_binary_operator(second_item)):
                ASTCHECK.raise_syntax_error(
                    "There cannot be two adjacent binary operators:",
                    string_list[i],
                    string_list[i + 1]
                )

    @staticmethod
    def check_adjacent_unary_plus_binary_operators(string: str) -> None:

        string_list = ASTUtilities.string2list(string)

        for i in range(0, len(string_list) - 1):

            fist_item = ASTUtilities.clean_parentheses(string_list[i])
            second_item = ASTUtilities.clean_parentheses(string_list[i + 1])

            if (ASTUtilities.is_unary_operator(fist_item) and
                    ASTUtilities.is_binary_operator(second_item)):
                ASTCHECK.raise_syntax_error(
                    "There cannot be a unary operator followed by a binary operator:",
                    string_list[i],
                    string_list[i + 1]
                )

    @staticmethod
    def check_adjacent_features(string: str) -> None:

        string_list = ASTUtilities.string2list(string)

        for i in range(0, len(string_list) - 1):

            fist_item = ASTUtilities.clean_parentheses(string_list[i])
            second_item = ASTUtilities.clean_parentheses(string_list[i + 1])

            if ASTUtilities.is_feature(fist_item) and ASTUtilities.is_feature(second_item):
                ASTCHECK.raise_syntax_error(
                    "There cannot be two adjacent features:",
                    string_list[i],
                    string_list[i + 1]
                )

    @staticmethod
    def check_binary_operator_preceded_or_succeeded_by_parentheses(string: str) -> None:

        string_list = ASTUtilities.string2list(string)

        for idx, _string in enumerate(string_list):

            item_without_parentheses = ASTUtilities.clean_parentheses(_string)

            if (ASTUtilities.is_binary_operator(item_without_parentheses) and
                    _string != item_without_parentheses):
                ASTCHECK.raise_syntax_error(
                    "A binary operator cannot be preceded or succeeded by parentheses:",
                    _string,
                    string_list[idx + 1]
                )

    @staticmethod
    def check_unary_operator_succeeded_by_parentheses(string: str) -> None:

        string_list = ASTUtilities.string2list(string)

        for _string in string_list:

            item = ASTUtilities.clean_parentheses(_string)

            if ASTUtilities.is_unary_operator(item) and ")" in _string:
                ASTCHECK.raise_syntax_error(
                    "An unary operator cannot succeeded by parentheses:",
                    _string
                )

    @staticmethod
    def check_binary_operator_at_start_or_end(string: str) -> None:

        string_list = ASTUtilities.string2list(string)

        fist_item = ASTUtilities.clean_parentheses(string_list[0])
        second_item = ASTUtilities.clean_parentheses(string_list[-1])

        if ASTUtilities.is_binary_operator(fist_item):
            ASTCHECK.raise_syntax_error(
                "There cannot be binary operator at start:",
                string_list[0]
            )

        if ASTUtilities.is_binary_operator(second_item):
            ASTCHECK.raise_syntax_error(
                "There cannot be binary operators at end:",
                string_list[-1]
            )

    @staticmethod
    def check_unary_operator_at_end(string: str) -> None:

        string_list = ASTUtilities.string2list(string)

        item = ASTUtilities.clean_parentheses(string_list[-1])

        if ASTUtilities.is_unary_operator(item):
            ASTCHECK.raise_syntax_error(
                "There cannot be unary operators at end::",
                string_list[-1]
            )

    @staticmethod
    def check_empty_parentheses(string: str) -> None:

        for i in range(0, len(string) - 1):

            first_item = string[i]
            second_item = string[i + 1]

            if first_item == "(" and second_item == ")":
                ASTCHECK.raise_syntax_error(
                    "There cannot be empty parentheses:",
                    string[i],
                    string[i + 1]
                )


class ASTUtilities:

    @staticmethod
    def string2list(string: str) -> List[str]:

        string = " ".join(string.split())
        return list(string.split(" "))

    # input string preprocessing
    @staticmethod
    def preprocessing(string: str) -> str:

        preprocessed_string = string

        preprocessed_string = ASTUtilities.computing_blank_spaces(preprocessed_string)

        return preprocessed_string

    @staticmethod
    def computing_blank_spaces(string: str) -> str:  # noqa: MC0001

        preprocessed_string = string

        if "(" in preprocessed_string or ")" in preprocessed_string:

            # remove spaces to the right of "("
            while "( " in preprocessed_string:
                for i in range(len(preprocessed_string) - 1):
                    if preprocessed_string[i] == "(" and preprocessed_string[i + 1] == " ":
                        preprocessed_string = ASTUtilities.replacer(preprocessed_string, "", i + 1)
                        break

            # remove spaces to the left of ")"
            while " )" in preprocessed_string:
                for i in range(len(preprocessed_string) - 1):
                    if preprocessed_string[i] == " " and preprocessed_string[i + 1] == ")":
                        preprocessed_string = ASTUtilities.replacer(preprocessed_string, "", i)
                        break

            # add a blank space to the left of "(" if what is on the left is not another "("
            end = False
            while not end:
                for i in range(1, len(preprocessed_string) - 1):
                    if preprocessed_string[i] == "(" and preprocessed_string[i - 1] != "(":
                        preprocessed_string = ASTUtilities.replacer(preprocessed_string, " (", i)
                        break
                    end = True

            # add a blank space to the right of ")" if what is on the right is not another ")"
            end = False
            while not end:
                for i in range(1, len(preprocessed_string) - 1):
                    if preprocessed_string[i] == ")" and preprocessed_string[i + 1] != ")":
                        preprocessed_string = ASTUtilities.replacer(preprocessed_string, ") ", i)
                        break
                    end = True

        # remove double spaces
        while "  " in preprocessed_string:
            for i in range(len(preprocessed_string) - 1):
                if preprocessed_string[i] == " " and preprocessed_string[i + 1] == " ":
                    preprocessed_string = ASTUtilities.replacer(preprocessed_string, "", i)
                    break

        # remove leading and trailing whitespace
        preprocessed_string = preprocessed_string.strip()

        return preprocessed_string

    @staticmethod
    def count_repeating_characters(string: str, character: str) -> int:
        count = 0

        for char in string:
            if char == character:
                count = count + 1
        return count

    @staticmethod
    def clean_parentheses(string: str) -> str:

        cleaned_string = string

        cleaned_string = cleaned_string.replace("(", "")
        cleaned_string = cleaned_string.replace(")", "")

        return cleaned_string

    @staticmethod
    def is_unary_operator(element: str) -> bool:
        return element in ASTINFO.get_unary_operators()

    @staticmethod
    def is_binary_operator(element: str) -> bool:
        return element in ASTINFO.get_binary_operators()

    @staticmethod
    def is_feature(element: str) -> bool:
        return (
            not ASTUtilities.is_binary_operator(element) and
            not ASTUtilities.is_unary_operator(element) and
            not element == ")" and not element == "("
        )

    @staticmethod
    def replacer(preprocessed_str: str, new_string: str, index: int, no_fail: bool = False) -> str:

        # raise an error if index is outside of the string
        if not no_fail and index not in range(len(preprocessed_str)):
            raise ValueError("index outside given string")

        # if not erroring, but the index is still not in the correct range
        if index < 0:  # add it to the beginning
            return new_string + preprocessed_str
        if index > len(preprocessed_str):  # add it to the end
            return preprocessed_str + new_string

        # insert the new string between "slices" of the original
        return preprocessed_str[:index] + new_string + preprocessed_str[index + 1:]


def print_tabs(node: Node) -> str:
    level = node.get_level()
    tabs = ""
    for _ in range(level - 1):
        tabs += "\t"
    return tabs


class AST():
    '''
    This algorithm obtains an abstract syntax tree from a text string.
    Support for parentheses is included
    '''

    def __init__(self, string: str = ""):

        # preprocessing
        preprocessed_string = ASTUtilities.preprocessing(string)

        # basic syntax checks
        ASTCHECK.check_all(preprocessed_string)

        self.string = preprocessed_string
        self.nodes: list[Node] = []
        self.list: list[str] = ASTUtilities.string2list(preprocessed_string)

        self.explore(i=0, j=len(self.list), points_to=None, level=0)

    def __str__(self) -> str:
        printed_tree = self.print_tree(self.get_root(), f'\n\n{self.get_root().get_name()}')
        return f'\n"{self.string}"{printed_tree}'

    def print_tree(self, node: Node, string: str) -> str:
        child_nodes = self.get_childs(node)
        for child_node in child_nodes:
            string += self.print_tree(
                child_node, "\n" + print_tabs(child_node) + child_node.get_name()
            )

        return string

    # extracts the positions of the binary operators in the range (i, j]
    def extract_binary_operators(self, i: int, j: int) -> List[int]:

        list_binary_operators = []

        for idx in range(i, j):
            if self.list[idx] in ASTINFO.get_binary_operators():
                list_binary_operators.append(idx)

        return list_binary_operators

    # extracts the positions of the unary operators in the range (i, j]
    def extract_unary_operators(self, i: int, j: int) -> List[int]:

        list_unary_operators = []

        for idx in range(i, j):
            if self.list[idx] in ASTINFO.get_unary_operators():
                list_unary_operators.append(idx)

        return list_unary_operators

    # discard binary operators enclosed in parentheses
    def discard_nodes_in_parentheses(self, i: int, j: int, possible_nodes: List[int]) -> List[int]:

        candidate_root_nodes_without_parentheses = []

        for element in possible_nodes:

            #  flag
            without_parentheses = True

            # EXPLANATION OF THE ALGORITHM
            # an element will be free if NEITHER to its left NOR to its right does not have
            # any elements with opening or closing parentheses

            # is there any parentheses "(" to the left?
            # note: the first element is not counted because it is considered an outer parenthesis,
            # hence the k! = i
            for k in range(i, element):
                if "(" in self.list[k] and k != i:
                    without_parentheses = False
                    break

            # is there any parentheses "(" to the right?
            # note: the last element is not counted because it is considered an outer parenthesis,
            # hence the k! = j-1
            if without_parentheses:
                for k in range(element + 1, j):
                    if ")" in self.list[k] and k != j - 1:
                        without_parentheses = False
                        break

            if without_parentheses:
                candidate_root_nodes_without_parentheses.append(element)

        return candidate_root_nodes_without_parentheses

    def explore(self, i: int, j: int, points_to: Any, level: int) -> None:
        """ DIVIDE AND CONQUER """

        # BASE CASE 1
        # There is the particular case of doing Divide and Conquer will win from a unary operator.
        # This causes it to be a sublist WITHOUT elements, since the unary operator
        # does not operate with elements to the left
        if j - i == 0:
            return

        # BASE CASE 2: list with a single element (it is a feature type "A")
        if j - i == 1:
            node = Node(
                is_leaf=True,
                is_feature=True,
                points_to=points_to,
                feature=ASTUtilities.clean_parentheses(self.list[i]),
                level=level + 1,
                token=i
            )
            self.nodes.append(node)

            return

        # BASE CASE 3: list with two elements (it is of type "not A")
        if j - i == 2:
            # the first node is the unary
            node_1 = Node(points_to=points_to, operator=self.list[i], level=level + 1, token=i)
            self.nodes.append(node_1)

            # the second node is the feature
            node_2 = Node(
                is_leaf=True,
                is_feature=True,
                points_to=i,
                feature=ASTUtilities.clean_parentheses(self.list[i + 1]),
                level=level + 2,
                token=i + 1
            )
            self.nodes.append(node_2)

            return

        # BASE CASE 4: list with three elements (it is of type "A implies B")
        if j - i == 3:
            # the parent node (operator) is the central node (i + 1)
            node = Node(
                operator=self.list[i + 1],
                points_to=points_to,
                level=level + 1,
                token=i + 1
            )
            self.nodes.append(node)

            # the first child (feature) is the node on the left
            node_1 = Node(
                is_leaf=True,
                is_feature=True,
                points_to=i + 1,
                feature=ASTUtilities.clean_parentheses(self.list[i]),
                level=level + 2,
                token=i
            )
            self.nodes.append(node_1)

            # the second child (feature) is the node on the right
            node_2 = Node(
                is_leaf=True,
                is_feature=True,
                points_to=i + 1,
                feature=ASTUtilities.clean_parentheses(self.list[i + 2]),
                level=level + 2,
                token=i + 2
            )
            self.nodes.append(node_2)

            return

        parent = self.find_out_parent_node(i, j)
        node = Node(points_to=points_to, operator=self.list[parent], level=level + 1, token=parent)
        self.nodes.append(node)

        # we execute divide and conquer
        self.explore(i, parent, points_to=parent, level=level + 1)
        self.explore(parent + 1, j, points_to=parent, level=level + 1)

    # finds the most suitable parent node in subset [i, j)
    def find_out_parent_node(self, i: int, j: int) -> int:

        candidate_binary_parent_nodes = self.extract_binary_operators(i, j)
        candidate_unary_parent_nodes = self.extract_unary_operators(i, j)

        candidate_binary_parent_nodes_without_parentheses = self.discard_nodes_in_parentheses(
            i=i,
            j=j,
            possible_nodes=candidate_binary_parent_nodes
        )
        candidate_unary_parent_nodes_without_parentheses = self.discard_nodes_in_parentheses(
            i=i,
            j=j,
            possible_nodes=candidate_unary_parent_nodes
        )

        # At the same level (understand by "same level" the nodes
        # which are free of parentheses),
        # unary operators take precedence if not previously
        # there are binary operators

        # if the list of binary operators is NOT empty
        if candidate_binary_parent_nodes_without_parentheses:

            # of all binary operators, the one with the highest priority is obtained
            parent = self.priority_binary_operator_according_to_hierarchy(
                candidate_binary_parent_nodes_without_parentheses
            )

        # if the list of binary operators is empty
        else:

            # of all unary operators, the one with the highest priority is obtained
            parent = self.priority_unary_operator_according_to_hierarchy(
                candidate_unary_parent_nodes_without_parentheses
            )

        return parent

    # given a list of unary operators, find the highest priority
    def priority_unary_operator_according_to_hierarchy(self, possible_nodes: List[int]) -> int:

        unary_operators = ASTINFO.get_unary_operators()
        position = len(unary_operators) - 1
        priority = possible_nodes[0]

        for element in possible_nodes:
            new_position = unary_operators.index(self.list[element])

            if new_position < position:
                position = new_position
                priority = element

        return priority

    # given a list of binary operators, find the highest priority
    def priority_binary_operator_according_to_hierarchy(self, possible_nodes: List[int]) -> int:

        binary_operators = ASTINFO.get_binary_operators()
        position = len(binary_operators) - 1
        priority = possible_nodes[0]

        for element in possible_nodes:
            new_position = binary_operators.index(self.list[element])

            if new_position < position:
                position = new_position
                priority = element

        return priority

    def get_nodes_by_feature(self, feature: str) -> List[Node]:
        res_node = []

        for node in self.nodes:
            if node.get_name() == feature:
                res_node.append(node)

        return res_node

    def get_root(self) -> Node:

        # we take the first node by default
        res_node = self.nodes[0]
        for node in self.nodes:

            if node.points_to is None:
                res_node = node
                break

        return res_node

    def get_childs(self, parent_node: Node) -> List[Node]:

        childs = []
        points_to = parent_node.token

        for node in self.nodes:
            if node.get_points_to() == str(points_to):
                childs.append(node)

        return childs

    def get_first_child(self, parent_node: Node) -> Optional[Node]:  # noqa

        children = self.get_childs(parent_node)

        if children:
            return children[0]

        return None

    def get_second_child(self, parent_node: Node) -> Optional[Node]:  # noqa

        children = self.get_childs(parent_node)

        if children:
            return children[-1]

        return None

    def get_nodes(self) -> List[Node]:

        return self.nodes

    def get_height(self) -> int:

        height = 1

        for node in self.get_nodes():
            level = node.get_level()
            if level > height:
                height = level

        return height

    def get_features(self) -> List[Node]:

        features = []

        for node in self.get_nodes():
            if node.is_feature:
                features.append(node)

        return features
