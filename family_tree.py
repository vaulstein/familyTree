import uuid
from six import string_types
import copy

from exceptions import *

__version__ = "0.1"

MALE_RELATIONS = {
                     "husband": 0, "father": -1, "brother": -1, "brothers": -1, "son": 1,
                     "sons": 1, "grandfather": -2, "grandson": 2, "grandsons": 2,
                     "uncle": -2, "cousin": -1, "cousins": -1
                 }
FEMALE_RELATIONS = {
                        "wife": 0, "mother": -1, "sister": -1, "daughter": 1, "daughters": 1,
                        "grandmother": -2, "granddaughter": 2, "aunt": -2, "cousin": -1, "cousins": -1
                    }


def sanitize_id(id):
    return id.strip().replace(" ", "")


(_ADD, _DELETE, _INSERT) = range(3)
(_ROOT, _DEPTH, _WIDTH) = range(3)


def process_input(input_from_user):
    commom_message = '''Invalid input.
        Add Person Using:
        [Relation]=[Exisiting Member] [Relation]=[New Member]
        Query format:
        Person=[Exisiting Member] Relation=[New Member]'''
    if not isinstance(input_from_user, string_types):
        raise InvalidInputType(commom_message)

    split_inputs = input_from_user.split(' ')
    if len(split_inputs) != 2:
        raise InvalidInputType(commom_message)

    try:
        first_part, first_name = split_inputs[0].split('=')
        second_part, second_name = split_inputs[1].split('=')
    except (TypeError, ValueError):
        raise InvalidInputType(commom_message)

    first_part, first_name = first_part.lower(), first_name.lower()
    second_part, second_name = second_part.lower(), second_name.lower()

    if first_part == 'person':
        if second_part == 'relation':
            male_true = second_name in MALE_RELATIONS.keys()
            female_true = second_name in FEMALE_RELATIONS.keys()
            if male_true or female_true:
                try:
                    if male_true:
                        index_to_query = MALE_RELATIONS[second_name]
                        male = True
                    else:
                        index_to_query = FEMALE_RELATIONS[second_name]
                        male = False
                except KeyError:
                    raise InvalidInputType('Relation query not part of supported queries.')
                if second_name in ['counsin', 'cousins']:
                    male = None
                return {'type': 'search', 'index_to_query': index_to_query, 'related_to': first_name,
                        'relation': second_name, 'male': male}
            else:
                raise InvalidInputType('Relation query not part of supported queries.')
        else:
            raise InvalidInputType(commom_message)
    else:
        first_male = first_part in MALE_RELATIONS.keys()
        first_female = first_part in FEMALE_RELATIONS.keys()
        second_male = second_part in MALE_RELATIONS.keys()
        second_female = second_part in FEMALE_RELATIONS.keys()
        if first_male or first_female:
            if second_male or second_female:
                try:
                    if second_male:
                        index_to_add = MALE_RELATIONS[second_part]
                        male = True
                    elif second_female:
                        index_to_add = FEMALE_RELATIONS[second_part]
                        male = False
                    if first_male:
                        index_to_search = MALE_RELATIONS[first_part]
                        male_search = True
                    elif first_female:
                        index_to_search = FEMALE_RELATIONS[first_part]
                        male_search = False
                    try:
                        assert index_to_add+index_to_search == 0
                    except AssertionError:
                        raise InvalidInputType("Relations don't match")
                except KeyError:
                    raise InvalidInputType('Relation not part of supported queries.')
                return {'type': 'add', 'index_to_add': index_to_add, 'male': male,
                        'to_search': first_name, 'to_add': second_name, 'relation': second_part,
                        'male_search': male_search}

        raise InvalidInputType('Relations not part of supported relations')


class Node:

    def __init__(self, name, male=False, identifier=None, expanded=True):
        self.__identifier = (str(uuid.uuid1()) if identifier is None else
                sanitize_id(str(identifier)))
        self.male = male
        self.name = name
        self.partner = None
        self.expanded = expanded
        # self.pointer = pointer
        self.__bpointer = None
        self.__fpointer = []

    @property
    def identifier(self):
        return self.__identifier

    @property
    def bpointer(self):
        return self.__bpointer

    @bpointer.setter
    def bpointer(self, value):
        if value is not None:
            self.__bpointer = sanitize_id(value)

    @property
    def fpointer(self):
        return self.__fpointer

    def update_fpointer(self, identifier, mode=_ADD):
        if mode is _ADD:
            self.__fpointer.append(sanitize_id(identifier))
        elif mode is _DELETE:
            self.__fpointer.remove(sanitize_id(identifier))
        elif mode is _INSERT:
            self.__fpointer = [sanitize_id(identifier)]


class Tree:

    def __init__(self):
        self.nodes = []
        self.persons = []
        # self.pointer = {}

    def get_index(self, position):
        try:
            for index, node in enumerate(self.nodes):
                if node.identifier == position:
                    break
            return index
        except UnboundLocalError as e:
            raise ParentNotAdded('No Person named {} exists in the Tree.'.format(position))

    def santity_checks(self, name, new_insert, parent):

        name_is_string = isinstance(name, string_types)
        if not name_is_string:
            raise InvalidPersonType('Invalid input for name: {}. Allowed type strings.'.format(name))
        if name.lower() in self.persons:
            raise DuplicatePersonError('{} already exists. Duplicates not allowed!'.format(name))
        if not new_insert:
            if parent not in self.persons:
                raise PersonNotFoundError('{} is not part of Family. Please add first!'.format(parent))
        return {'success': True, 'message': 'Passed Checks!'}

    def create_node(self, name, identifier=None, parent=None, male=False, partner=False):
        new_insert = True
        pointer = 0

        if parent:
            new_insert = False

        clean = self.santity_checks(name, new_insert, parent)
        if not clean.get('success', None):
            return clean.get('message', None)

        # if not self.nodes:
        #     self.pointer[0] = [name.lower()]

        # if parent:
        #     parent_pointer = self[parent].pointer
        #     pointer = parent_pointer + 1
        #     if pointer in self.pointer:
        #         self.pointer[pointer].append(name.lower())
        #     else:
        #         self.pointer[pointer] = [name.lower()]
        node = Node(name, identifier=identifier, male=male)

        if partner:
            if self[partner].partner:
                raise RelationExistsError('Relation already exists!')
            self[partner].partner = name
        else:
            self.nodes.append(node)
            self.__update_fpointer(parent, node.identifier, _ADD)
            node.bpointer = parent
        self.persons.append(identifier)

        return node

    def show(self, position, level=_ROOT):
        queue = self[position].fpointer
        if level == _ROOT:
            if self[position].partner:
                print("{0} [{1}] + {2}".format(self[position].name,
                                               self[position].identifier,
                                               self[position].partner
                                               ))
            else:
                print("{0} [{1}]".format(self[position].name,
                                         self[position].identifier))
        else:
            if self[position].partner:
                print("\t"*level, "{0} [{1}] + {2}".format(self[position].name,
                                                           self[position].identifier,
                                                           self[position].partner
                                                           ))
            else:
                print("\t"*level, "{0} [{1}]".format(self[position].name,
                                                     self[position].identifier))
        if self[position].expanded:
            level += 1
            for element in queue:
                self.show(element, level)  # recursive call

    def find_parent(self, position, search_index):
        if search_index == 0:
            return copy.deepcopy(self[position])
        else:
            position = self[position].bpointer
            search_index += 1
            return self.find_parent(position, search_index)

    def find_child(self, position, search_index, male, fetch_all=None):
        if search_index == 0:
            required_childs = []
            for pos in position:
                if not male or self[pos].male == male:
                    required_childs.append(self[pos].name)
                    if not fetch_all:
                        break
            return required_childs
        else:
            if isinstance(position, string_types):
                position = self[position].fpointer
            elif isinstance(position, list):
                child_position = []
                for pos in position:
                    child_position.extend(self[pos].fpointer)
                    if not fetch_all:
                        break
                position = child_position
            search_index -= 1
            return self.find_child(position, search_index, male, fetch_all)

    def find_relation(self, position, search_index, male, relation, fetch_all=None):
        if search_index < 0:
            required_person = self.find_parent(position, search_index)
            if relation in ["father", "mother", "grandfather", "grandmother"]:
                if male == required_person.male:
                    return required_person.name
                else:
                    return required_person.partner
            elif relation in ["brother", "brothers", "sister", "sisters"]:
                sibling_nodes = []
                required_person.fpointer.remove(position)
                for sib in required_person.fpointer:
                    if not male or self[sib].male == male:
                        sibling_nodes.append(self[sib].name)
                        if not fetch_all:
                            break
                return sibling_nodes
            elif relation in ["uncle", "uncles", "aunt", "aunts"]:
                parent_siblings = []
                required_person.fpointer.remove(self[position].bpointer)
                for sib in required_person.fpointer:
                    if male == self[sib].male:
                        parent_siblings.append(self[sib].name)
                    else:
                        if self[sib].partner:
                            parent_siblings.append(self[sib].partner)
                    if not fetch_all:
                        break
                return parent_siblings
        elif search_index > 0:
            return self.find_child(position, search_index, male, fetch_all)
        else:
            required_person = self[position]
            if male == required_person.male:
                return required_person.name
            else:
                return required_person.partner

    def expand_tree(self, position, mode=_DEPTH):
        # Python generator. Loosly based on an algorithm from 'Essential LISP' by
        # John R. Anderson, Albert T. Corbett, and Brian J. Reiser, page 239-241
        yield position
        queue = self[position].fpointer
        while queue:
            yield queue[0]
            expansion = self[queue[0]].fpointer
            if mode is _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode is _WIDTH:
                queue = queue[1:] + expansion  # width-first

    def is_branch(self, position):
        return self[position].fpointer

    def __update_fpointer(self, position, identifier, mode):
        if position is None:
            return
        else:
            self[position].update_fpointer(identifier, mode)

    def __update_bpointer(self, position, identifier):
        self[position].bpointer = identifier

    def __getitem__(self, key):
        return self.nodes[self.get_index(key)]

    def __setitem__(self, key, item):
        self.nodes[self.get_index(key)] = item

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, identifier):
        return [node.identifier for node in self.nodes
                if node.identifier is identifier]


def start(family_tree, normalized_input):
    if normalized_input['type'] == 'search':
        fetch_all = False
        if normalized_input['relation'].endswith('s'):
            fetch_all = True
        matches = family_tree.find_relation(normalized_input['related_to'], normalized_input['index_to_query'],
                                            normalized_input['male'], normalized_input['relation'], fetch_all)
        if matches:
            if isinstance(matches, list):
                new_matches = ','.join(matches)
                matches = new_matches
            print('Output: {}={}'.format(normalized_input['relation'].capitalize(), matches))
    else:
        fetch_all = False
        if normalized_input['relation'].endswith('s'):
            fetch_all = True
        matches = family_tree.find_relation(normalized_input['to_search'], normalized_input['index_to_add'],
                                            normalized_input['male_search'], normalized_input['relation'], fetch_all)
        partner = None
        if normalized_input['relation'] in ['wife', 'husband']:
            partner = normalized_input['to_search']
        family_tree.create_node(normalized_input['to_add'].capitalize(), normalized_input['to_add'],
                                male=normalized_input['male'], partner=partner)
        print('Output: Welcome to the family, {}'.format(normalized_input['to_add'].capitalize()))
    return matches


if __name__ == "__main__":

    from tests.test_family_tree import populate_tree

    print(r'''Welcome to Family Tree. v{v}.
    ______              _ _         _____             
    |  ___|            (_) |       |_   _|            
    | |_ __ _ _ __ ___  _| |_   _    | |_ __ ___  ___ 
    |  _/ _` | '_ ` _ \| | | | | |   | | '__/ _ \/ _ \
    | || (_| | | | | | | | | |_| |   | | | |  __/  __/
    \_| \__,_|_| |_| |_|_|_|\__, |   \_/_|  \___|\___|
                             __/ |                    
                            |___/                     
    This script will help you add members to the Family Tree and query relations.
    Assumptions are mentioned in the README.md
    Runs on Python 3+.
    Requirements are mentioned in requirements.txt
    Tree has already been populated so that you can get started with querying.
        '''.format(v=__version__))
    trees = populate_tree()
    print("=" * 80)
    trees.show("evan")
    print("=" * 80)
    while True:
        user_input = input('Input: ')
        try:
            processed_input = process_input(user_input)
            start(trees, processed_input)
        except Exception as e:
            print(e)
        continue_flag = input('Do you want to Continue? Type "y" to continue')
        if continue_flag.lower() != 'y':
            break


