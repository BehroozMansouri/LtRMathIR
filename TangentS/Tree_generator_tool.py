import os
import unicodedata


class Node:
    """
    node of formula tree, the value can be V!x, N!2
    the children have order, if the value has type U! then they are all the same
    the parent will be used for traversing
    """
    def __init__(self, value, id):
        self.value = value
        self.lst_children = []
        self.parent = None
        self.id = id

    def set_father(self, node):
        self.parent = node

    def add_child(self, value, id):
        temp = Node(value, id)
        temp.set_father(self)
        self.lst_children.append(temp)
        return temp


def get_depth(root):
    if root.lst_children == [] or len(root.lst_children) == 0:
        return 1
    max_depth = -1
    for child_node in root.lst_children:
        curr_depth = get_depth(child_node)
        if curr_depth+1 > max_depth:
            max_depth = curr_depth + 1
    return max_depth


def is_digit(param):
    try:
        int(param)
        return True
    except:
        return False


def correct(string):
    i = 0
    temp = ""
    # print(string)
    while i < len(string):
        if is_digit(string[i]):
            number = int(string[i])
            i += 1
            val = string[i]
            for x in range(0, number):
                temp += val
        else:
            temp += string[i]
        i += 1
    # print(temp)
    return temp


class TreeCreator:

    @staticmethod
    def create_formula_nodes(source_directory):
        map_tree_formulas = {}
        map_tree_queries = {}
        for directory in os.listdir(source_directory):
            if directory == "Queries":
                for filename in os.listdir(source_directory + "/" + directory):
                    tree = TreeCreator.file_tuples_to_node(source_directory + "/" + directory + "/" + filename)
                    temp = os.path.splitext(filename)[0]
                    map_tree_queries[temp] = tree
            else:
                for filename in os.listdir(source_directory + "/" + directory):
                    tree = TreeCreator.file_tuples_to_node(source_directory + "/" + directory + "/" + filename)
                    temp = os.path.splitext(filename)[0]
                    temp = str(unicodedata.normalize('NFKD', temp).encode('ascii', 'ignore'))
                    temp = temp[2:]
                    temp = temp[:0]
                    temp = temp.lower()
                    map_tree_formulas[temp] = tree
        return map_tree_formulas, map_tree_queries

    @staticmethod
    def create_formula_tree_map(source_directory):
        map_tree_formulas = {}
        map_tree_queries = {}
        for directory in os.listdir(source_directory):
            if directory == "Queries":
                for filename in os.listdir(source_directory + "/" + directory):
                    tree = TreeCreator.file_tuples_to_string(source_directory + "/" + directory + "/" + filename)
                    temp = os.path.splitext(filename)[0]
                    map_tree_queries[temp] = tree
            else:
                for filename in os.listdir(source_directory + "/" + directory):
                    tree = TreeCreator.file_tuples_to_string(source_directory + "/" + directory + "/" + filename)
                    temp = os.path.splitext(filename)[0]
                    temp = str(unicodedata.normalize('NFKD', temp).encode('ascii', 'ignore'))
                    temp = temp[2:]
                    temp = temp[:0]
                    temp = temp.lower()
                    map_tree_formulas[temp] = tree
        return map_tree_formulas, map_tree_queries


    @staticmethod
    def create_formula_queries(source_directory):
        map_tree_formulas = {}
        map_tree_queries = {}
        for directory in os.listdir(source_directory):
            if directory == "Queries":
                for filename in os.listdir(source_directory + "/" + directory):
                    tree = TreeCreator.file_tuples_to_string(source_directory + "/" + directory + "/" + filename)
                    temp = os.path.splitext(filename)[0]
                    map_tree_queries[temp] = tree

        return map_tree_queries
    @staticmethod
    def create_formula_tree_map_collection(source_directory):
        map_tree_formulas = {}
        for directory in os.listdir(source_directory):
            if directory == "Queries":
                continue
            else:
                for filename in os.listdir(source_directory + "/" + directory):
                    tree = TreeCreator.file_tuples_to_string(source_directory + "/" + directory + "/" + filename)
                    temp = os.path.splitext(filename)[0]
                    temp = str(unicodedata.normalize('NFKD', temp).encode('ascii', 'ignore'))
                    temp = temp[2:]
                    temp = temp[:0]
                    temp = temp.lower()
                    map_tree_formulas[temp] = tree
        return map_tree_formulas

    @staticmethod
    def file_tuples_to_string(file_path):
        try:
            lst = TreeCreator.__read_tuples(file_path)
            # root = TreeCreator.__tuples_to_tree(lst)#tuples_to_tree(lst)#tuples_to_tree(lst)
            root = TreeCreator.__edge_tuples_to_tree(lst)#tuples_to_tree(lst)  # tuples_to_tree(lst)#tuples_to_tree(lst)
            # root = TreeCreator.__slt_tuples_to_tree(lst)#tuples_to_tree(lst)  # tuples_to_tree(lst)#tuples_to_tree(lst)
            return TreeCreator.__get_string_tree(root)
        except:
            print(file_path)
            return None

    @staticmethod
    def direct_tuples_to_string(lst_tuples, has_edge):
        try:
            if has_edge:
                root = TreeCreator.__edge_tuples_to_tree(lst_tuples)
            else:
                root = TreeCreator.__tuples_to_tree(lst_tuples)
            return TreeCreator.__get_string_tree(root)
        except:
            print("Error")
            return None

    @staticmethod
    def file_tuples_to_node(file_path):
        try:
            lst = TreeCreator.__read_tuples(file_path)
            root = TreeCreator.__tuples_to_tree(lst)
            return root
        except:
            print(file_path)
            return None

    @staticmethod
    def __read_tuples(file_name):
        file = open(file_name)
        lst = []
        line = file.readline().strip("\n")
        while line:
            line = line.replace("}", "$$$")
            line = line.replace("{", "$$$")
            elements = line.split("\t")[0:3]
            lst.append(elements)
            line = file.readline().strip("\n")
        return lst

    @staticmethod
    def __get_string_tree(node):
        if not node.lst_children:
            return '{' + node.value + '}'
        result = '{' + node.value
        for child in node.lst_children:
            result += TreeCreator.__get_string_tree(child)
        return result + '}'

    @staticmethod
    def __tuples_to_tree(lst_tuples):
        """
        Given the list of tuples extracted from the tree by Tangent-S, creates the tree.
        :param lst_tuples:
        :return:
        """
        root = None
        current = None
        id = 0
        for tuple in lst_tuples:
            if root is None:
                root = Node(tuple[0], id)
                id += 1
                if tuple[1] != '0!':
                    current = root.add_child(tuple[1], id)
                    id += 1
            elif tuple[1] == '0!':
                current = current.parent
            else:
                while current.value != tuple[0]:
                    current = current.parent
                current = current.add_child(tuple[1], id)
                id += 1
        return root

    @staticmethod
    def __edge_tuples_to_tree(lst_tuples):
        """
        Given the list of tuples extracted from the tree by Tangent-S, we create the tree.
        :param lst_tuples:
        :return:
        """
        root = None
        current = None
        id = 0
        for tuple in lst_tuples:
            if root is None:
                root = Node(tuple[0], id)
                id += 1
                if tuple[1] != '0!':
                    current = root.add_child(tuple[2], id)
                    id += 1
                    current = current.add_child(tuple[1], id)
                    id += 1
            elif tuple[1] == '0!':
                current = current.parent
            else:
                while current.value != tuple[0]:
                    current = current.parent
                current = current.add_child(tuple[2], id)
                id += 1
                current = current.add_child(tuple[1], id)
                id += 1
        return root

    @staticmethod
    def get_tree_depth(lst_tuples):
        try:
            root = TreeCreator.__tuples_to_tree(lst_tuples)
            return get_depth(root)
        except:
            print("Depth Error")
            return 0

    @staticmethod
    def get_variation_from_baseline(lst_tuples):
        max_length = -1
        try:
            for tuple in lst_tuples:
                # print(tuple)
                string = str(tuple[3])
                string = string.strip()
                string = correct(string)
                string = string.replace('n', '', string.count('n'))
                if len(string) > max_length:
                    max_length = len(string)
            return max_length
        except:
            # print("Var Error")
            return 0

    @staticmethod
    def tuples_to_tree(lst_tuples):
        """
        Given the list of tuples extracted from the tree by Tangent-S, creates the tree.
        :param lst_tuples:
        :return:
        """
        root = None
        current = None
        id = 0
        for tuple in lst_tuples:
            if root is None:
                root = Node(tuple[0], id)
                id += 1
                if tuple[1] != '0!':
                    current = root.add_child(tuple[1], id)
                    id += 1
            elif tuple[1] == '0!':
                current = current.parent
            else:
                while current.value != tuple[0]:
                    current = current.parent
                current = current.add_child(tuple[1], id)
                id += 1
        return root