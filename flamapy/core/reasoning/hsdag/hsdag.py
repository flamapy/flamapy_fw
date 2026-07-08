"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/hs/HSDAG.java
"""
from typing import List, Optional, Dict, Union

from .labeler.labeler import IHSLabelable, LabelerType, AbstractHSParameters
from .node import Node, NodeStatus
from .. import utils
from ..utils import diff, contains


class HSDAGException(Exception):
    """
    Exception class for HSDAG
    """


class HSDAG:
    """
    Implementation of the HS-dag algorithm.
    IHSLabeler algorithms could return labels (conflict or diagnosis) which are not minimal.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, labeler: IHSLabelable) -> None:
        self.labeler = labeler  # could be FastDiag or QuickXPlain

        self.max_number_diagnoses = -1  # maximum number of diagnoses to be found
        self.max_number_conflicts = -1  # maximum number of conflicts to be found
        self.max_depth = 0  # maximum depth of the HS-dag

        self.node_labels: List[List[int]] = []  # list of diagnoses or conflicts found
        self.path_labels: List[List[int]] = []  # list of diagnoses or conflicts found

        self.root: Optional[Node] = None  # root node of the HS-dag
        self.open_nodes: List[Node] = []  # list of open nodes
        # Map of <label, list of nodes which have the label as its label>
        self.label_nodes_map: Dict[int, List[Node]] = {}
        self.nodes_lookup: Dict[int, Node] = {}  # Map of <pathLabel, Node>

    def get_conflicts(self) -> List[List[int]]:
        """
        Returns the list of conflicts found.
        """
        if self.labeler.get_type() == LabelerType.CONFLICT:
            return self.node_labels
        return self.path_labels

    def get_diagnoses(self) -> List[List[int]]:
        """
        Returns the list of diagnoses found.
        """
        if self.labeler.get_type() == LabelerType.CONFLICT:
            return self.path_labels
        return self.node_labels

    def should_stop_construction(self) -> bool:
        condition1 = (self.max_number_diagnoses != -1
                      and self.max_number_diagnoses <= len(self.get_diagnoses()))
        condition2 = (self.max_number_conflicts != -1
                      and self.max_number_conflicts <= len(self.get_conflicts()))
        return condition1 or condition2

    def construct(self) -> None:
        """
        Constructs the HS-dag.
        """
        param = self.labeler.get_initial_parameters()

        has_root_label = self.create_root(param)

        if not self.should_stop_construction() and has_root_label:
            self.create_nodes()

    def create_root(self, param: AbstractHSParameters) -> bool:
        """
        Creates the root node of the HS-dag.
        """
        has_root_label = True

        if not self.has_root():
            labels = self.compute_label(self.labeler, param)

            if len(labels) == 0:
                has_root_label = False
            else:  # create root node
                label = self.select_label(labels)
                self.root = Node.create_root(label, param)

                self.open_nodes.append(self.root)

                self.add_node_labels(labels)  # to reuse labels
                self.add_item_to_label_nodes_map(label, self.root)

        return has_root_label

    def create_nodes(self) -> None:
        """
        Creates nodes of the HS-dag.
        """
        while self.has_nodes_to_expand():
            node = self.get_next_node()

            if not node.is_root():
                if self.skip_node(node):
                    continue

                self.label(node)

                if self.should_stop_construction():
                    break

            if node.status == NodeStatus.OPEN:
                self.expand(node)

    def label(self, node: Node) -> None:
        """
        Labels a node - identify new conflict or diagnosis.
        """
        # Reusing labels - H(node) ∩ S = {}, then label node by S
        labels = self.get_reusable_labels(node)

        # compute labels if there are none to reuse
        if len(labels) == 0:
            labels = self.compute_label_from_node(self.labeler, node)

            self.process_labels(labels)

        if len(labels) > 0:
            label = self.select_label(labels)

            node.label = label
            self.add_item_to_label_nodes_map(label, node)

        else:  # found a path label
            self.found_a_path_label_at_node(node)

    def expand(self, node_to_expand: Node) -> None:
        """
        Creates children of a node.
        """
        for arc_label in node_to_expand.label:
            param_parent_node = node_to_expand.parameters
            if param_parent_node is None:
                raise HSDAGException("The parent node must have parameters.")

            new_param = self.labeler.identify_new_node_parameters(param_parent_node, arc_label)

            # rule 1.a - reuse node
            node = self.get_reusable_node(node_to_expand.path_label, arc_label)
            if node is not None:
                node.add_parent(node_to_expand)
            else:  # rule 1.b - generate a new node
                node = Node(parent=node_to_expand, arc_label=arc_label, parameters=new_param)
                hashcode = sum(node.path_label)
                self.nodes_lookup[hashcode] = node

                if not self.can_prune(node):
                    self.open_nodes.append(node)

    def add_item_to_label_nodes_map(self, label: List[int], node: Node) -> None:
        """
        Adds a node to the label_nodes_map.
        """
        hashcode = sum(label)
        if hashcode in self.label_nodes_map:
            self.label_nodes_map[hashcode].append(node)
        else:
            self.label_nodes_map[hashcode] = [node]

    @staticmethod
    def compute_label(labeler: IHSLabelable, param: AbstractHSParameters) -> List[List[int]]:
        return labeler.get_label(param)

    @staticmethod
    def compute_label_from_node(labeler: IHSLabelable, node: Node) -> List[List[int]]:
        param = node.parameters
        if param is None:
            raise HSDAGException("The node must have parameters.")
        return HSDAG.compute_label(labeler, param)

    def add_node_labels(self, labels: List[List[int]]) -> None:
        for label in labels:
            self.node_labels.append(label)

    def found_a_path_label_at_node(self, node: Node) -> None:
        node.status = NodeStatus.CHECKED
        path_label = node.path_label.copy()

        self.path_labels.append(path_label)

    @staticmethod
    def select_label(labels: List[List[int]]) -> List[int]:
        return labels[0]

    def has_nodes_to_expand(self) -> bool:
        return len(self.open_nodes) > 0

    def get_next_node(self) -> Node:
        return self.open_nodes.pop(0)

    def has_root(self) -> bool:
        return self.root is not None

    # Pruning engine
    def skip_node(self, node: Node) -> bool:
        condition1 = self.max_depth != 0 and self.max_depth < node.level
        return node.status != NodeStatus.OPEN or condition1 or self.can_prune(node)

    def can_prune(self, node_2prime: Node) -> bool:
        # 3.i - if n is checked, and n'' is such that H(n) ⊆ H(n'), then close the node n''
        # n is a diagnosis
        for path_label in self.path_labels:
            # if node.path_label.containsAll(path_label):
            if all(elem in path_label for elem in node_2prime.path_label):
                node_2prime.status = NodeStatus.CLOSED
                return True

        # 3.ii - if n has been generated and node n'' is such that H(n') = H(n),
        # then close node n''
        for node in self.open_nodes:
            if len(node.path_label) == len(node_2prime.path_label) \
                    and len(diff(node.path_label, node_2prime.path_label)) == 0:
                node_2prime.status = NodeStatus.CLOSED
                return True
        return False

    def get_reusable_labels(self, node: Node) -> List[List[int]]:
        labels = []
        for label in self.node_labels:
            # H(node) ∩ S = {}
            if not utils.has_intersection(node.path_label, label):
                labels.append(label)
        return labels

    def get_reusable_node(self, path_labels: List[int], arc_label: int) -> Union[Node, None]:
        if len(path_labels) == 0:
            new_path_labels = [arc_label]
        else:
            new_path_labels = path_labels.copy()
            new_path_labels.append(arc_label)
        hashcode = sum(new_path_labels)
        return self.nodes_lookup.get(hashcode)

    def process_labels(self, labels: List[List[int]]) -> None:
        # check existing and obtained labels for subset-relations
        if len(labels) <= 0:
            return

        non_min_labels: List[List[int]] = []
        for first_label in self.node_labels:
            if contains(non_min_labels, first_label):
                continue

            for second_label in labels:
                if contains(non_min_labels, second_label):
                    continue

                greater = first_label if len(first_label) > len(second_label) else second_label
                smaller = second_label if len(first_label) > len(second_label) else first_label
                if not utils.contains_all(greater, smaller):
                    continue

                non_min_labels.append(greater)
                # update the DAG
                nodes = self.label_nodes_map.get(sum(greater))

                if nodes is None:
                    continue

                # get a list of nodes which have the status OPEN
                open_nodes = [n for n in nodes if n.status == NodeStatus.OPEN]

                self.update_dag(greater, open_nodes, smaller)

        # remove the known non - minimal conflicts
        for non_min_label in non_min_labels:
            labels.remove(non_min_label)  # labels.removeAll(non_min_labels)
            hashcode = sum(non_min_label)
            del self.label_nodes_map[hashcode]  # non_min_labels.forEach(label_nodesMap::remove)

        # add new labels to the list of labels
        self.add_node_labels(labels)

    def update_dag(self, greater: List[int], open_nodes: List[Node], smaller: List[int]) -> None:
        for node in open_nodes:
            node.label = smaller  # relabel the node with smaller
            # add new label to the map
            self.add_item_to_label_nodes_map(smaller, node)
            delete = diff(greater, smaller)

            for label in delete:
                child = node.children.get(label)
                if child is None:
                    continue
                child.parents.remove(node)
                del node.children[label]
                self.clean_up_nodes(child)

    def clean_up_nodes(self, node: Node) -> None:
        hashcode = sum(node.path_label)
        del self.nodes_lookup[hashcode]

        if node.status == NodeStatus.OPEN:
            node.status = NodeStatus.PRUNED

        # downward clean up
        for arc_label in node.children.keys():
            child = node.children.get(arc_label)
            if child is not None:
                self.clean_up_nodes(child)
