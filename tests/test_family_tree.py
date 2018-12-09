import pytest

import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from family_tree import Tree
from exceptions import *


@pytest.fixture(scope="module")
def populate_tree():
    tree = Tree()
    tree.create_node("Evan", "evan", male=True)
    tree.create_node("Diana", "diana", partner="evan")
    tree.create_node("John", "john", male=True,  parent="evan")
    tree.create_node("Alex", "alex", male=True, parent="evan")
    tree.create_node("Nancy", "nancy", partner="alex")
    tree.create_node("Joe", "joe", male=True, parent= "evan")
    tree.create_node("Niki", "niki", partner="joe")
    tree.create_node("Nisha", "nisha", male=False, parent= "evan")
    tree.create_node("Adam", "adam", partner="nisha")
    tree.create_node("Jacob", "jacob", male=True, parent = "alex")
    tree.create_node("Shaun", "shaun", male=True, parent = "alex")
    tree.create_node("Bern", "bern", male=True, parent="jacob")
    tree.create_node("Sophia", "sophia", male=False, parent="jacob")
    tree.create_node("Piers", "piers", male=True, parent="joe")
    tree.create_node("Sally", "sally", male=False, parent="joe")
    tree.create_node("Sarah", "sarah", male=False, parent="piers")
    tree.create_node("Ruth", "ruth", male=False, parent="nisha")
    tree.create_node("Paul", "paul", male=True, parent="nisha")
    tree.create_node("William", "william", male=True, parent="nisha")
    tree.create_node("Steve", "steve", male=True, parent="william")
    tree.create_node("Roger", "roger", male=True, parent="paul")
    tree.create_node("Ram", "ram", male=True)
    return tree


def test_child_first():
    with pytest.raises(ParentNotAdded, match=r'No Person named .* exists in the Tree.'):
        tree = Tree()
        tree.create_node("Diana", "diana", partner="evan")


def test_invalid_type():
    with pytest.raises(InvalidPersonType):
        tree = Tree()
        tree.create_node(12323, "diana", partner="evan")


def test_duplicate_person(populate_tree):
    with pytest.raises(DuplicatePersonError):
        populate_tree.create_node("John", "john", male=True,  parent="evan")


def test_parent_missing(populate_tree):
    with pytest.raises(PersonNotFoundError):
        populate_tree.create_node("Simran", "simran", male=False,  parent="raj")


def test_exisiting_partne(populate_tree):
    with pytest.raises(RelationExistsError):
        populate_tree.create_node("Jancy", "jancy", male=False, partner="alex")


def test_output(capfd, populate_tree):
    print("=" * 80)
    populate_tree.show("evan")
    print("=" * 80)
    out, err = capfd.readouterr()
    assert out


def test_create_new_node():
    from family_tree import Node
    tree = Tree()
    user = tree.create_node("Diana", "diana")
    assert isinstance(user, Node)


@pytest.mark.parametrize("user_input, expected_output", [
    (12345, InvalidInputType),
    ("Some wrong input", InvalidInputType),
    ("Person:William Relation:Brother", InvalidInputType),
    ("Person:William", InvalidInputType),
    ("Person:William Relation:Brother", InvalidInputType),
    ("Person=William Wife=Brother", InvalidInputType),
    ("Person=William Relation=Bro", InvalidInputType),
    ("Person=William Relation=Brother-in-law", InvalidInputType),
    ("Mother=Zoe", InvalidInputType),
    ("Mother=Zoe Grandmother=Nisha", InvalidInputType),
    ("Mother=Zoe Sis=Nisha", InvalidInputType)
])
def test_process_input(user_input, expected_output):
    from family_tree import process_input
    with pytest.raises(expected_output):
        process_input(user_input)


@pytest.mark.parametrize("name, index, male, relation, fetch_all, expected", [
    ("william", -2, True, 'grandfather', False, 'Evan'),
    ("alex", 2, True, 'grandson', False, ['Bern']),
    ("william", -2, True, 'uncles', True, ['John', 'Alex', 'Joe']),
    ("william", -2, False, 'aunts', True, ['Nancy', 'Niki'])
])
def test_find_relations(name, index, male, relation, fetch_all, expected):
    # Cause of warnings : https://docs.pytest.org/en/latest/proposals/parametrize_with_fixtures.html
    tree = populate_tree()
    assert tree.find_relation(name, index, male, relation, fetch_all) == expected


def test_search_output(capfd):
    from family_tree import start
    process_input = {'type': 'search', 'index_to_query': -1, 'related_to': 'alex', 'relation': 'brother', 'male': True}
    tree = populate_tree()
    start(tree, process_input)
    expected_output = 'Output: Brother=John\n'
    out, err = capfd.readouterr()
    assert out == expected_output


def test_add_output(capfd):
    from family_tree import start
    process_input = {'type': 'add', 'index_to_add': 0, 'male': False, 'to_search': 'paul', 'to_add': 'sheila',
                     'relation': 'wife', 'male_search': True}
    tree = populate_tree()
    start(tree, process_input)
    expected_output = 'Output: Welcome to the family, Sheila'
    out, err = capfd.readouterr()
    assert expected_output in out





