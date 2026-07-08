#!/usr/bin/env python
"""Provides utility functions."""
from typing import List, Tuple


def split(clauses: List[int]) -> Tuple[List[int], List[int]]:
    """
    Splits the given list of constraints/clauses into two parts.
    :param clauses: a list of clauses
    :return: a tuple of two lists
    """
    half_size = len(clauses) // 2
    return clauses[:half_size], clauses[half_size:]


def diff(list_x: List[int], list_y: List[int]) -> List[int]:
    """
    Returns the difference of two lists.
    :param list_x: list
    :param list_y: list
    :return: list
    """
    return [item for item in list_x if item not in list_y]


def get_hashcode(clauses: List[int]) -> str:
    """
    Returns the hashcode of the given CNF formula.
    :param clauses: a list of clauses
    :return: the hashcode of the given CNF formula
    """
    # clauses = sorted(clauses, key=lambda x: x[0])
    clauses = sorted(clauses)
    return str(clauses)


def has_intersection(list1: List[int], list2: List[int]) -> bool:
    return any(i in list1 for i in list2)


def contains(list_of_lists: List[List[int]], a_list: List[int]) -> bool:
    return any(a_list == x for x in list_of_lists)


def contains_all(greater: List[int], smaller: List[int]) -> bool:
    return all(i in smaller for i in greater)
