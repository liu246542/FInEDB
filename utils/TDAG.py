#!/usr/bin/python3

import math
import pprint
from tools import ParseRawData
from collections import namedtuple


def int2binstr(int_value):
    assert isinstance(int_value, int)
    return bin(int_value)[2:]


def binstr2int(bin_str):
    assert isinstance(bin_str, str)
    return int(bin_str, 2)


Node = namedtuple("Node", ["name", "c_node", "p_node", "cv_range"])


class TDAG(object):
    """
    docstring for TDAG
    """

    def __init__(self, max_value):
        # self.height = math.ceil(math.log(max_value + 1, 2))
        self.height = len(int2binstr(max_value))

    # def __CollectParents__(self, node):
        # while node.p_node != []:
            # res_nodes = []
            # res_nodes.extend(node.p_node)
            # res_nodes.extend(self.__CollectParents__())

    def construct(self, value_list):
        # return a list contains a set of nodes
        value_set = sorted(set(value_list))
        # print(value_set)
        Tree_Nodes = {}
        print(self.height)
        for i in range(self.height, -1, -1):
            # level_nodes = {}
            level_nodes = []
            for j in range(2 ** i):
                name = int2binstr(j).rjust(i, "0")
                child_nodes = [name + "0", name + "1"]
                parent_node = [name[0:-1]]
                cover_range = [binstr2int(x) for x in
                               [name.ljust(self.height, "0"),
                                name.ljust(self.height, "1")]]
                if i == self.height:
                    child_nodes = []
                    cover_range = [cover_range[0]]
                if i == 0:
                    name = "root"
                    parent_node = []
                    cover_range = [0, 2 ** self.height - 1]
                if i == 1:
                    parent_node = ["root"]
                node_def = Node(name, child_nodes, parent_node, cover_range)
                # Tree_Nodes.append(node_def)
                level_nodes.append(node_def)
                # level_nodes.setdefault(name, node_def)
                # Tree_Nodes.setdefault(name, node_def)
            Tree_Nodes.setdefault(i, level_nodes)
        # print(Tree_Nodes.get(0))
        # pprint.pprint(Tree_Nodes)

        for i in range(1, self.height):
            # pprint.pprint(Tree_Nodes.get(i))
            node_list = Tree_Nodes.get(i)
            level_nodes = []
            for j in range(len(node_list) - 1):
                name = node_list[j].name + "_" + node_list[j + 1].name
                child_nodes = [node_list[j].c_node[1],
                               node_list[j + 1].c_node[0]]
                cover_range = [node_list[j].cv_range[1],
                               node_list[j + 1].cv_range[0]]
                node_def = Node(name, child_nodes, [], cover_range)
                level_nodes.append(node_def)

                node_list_next = Tree_Nodes.get(i + 1)
                node_list_next[2 * j + 1].p_node.append(name)
                node_list_next[2 * j + 2].p_node.append(name)
            Tree_Nodes[i].extend(level_nodes)
            # DAG_Nodes.setdefault(i, level_nodes)
        # pprint.pprint(Tree_Nodes)

        Node_Dict = {}

        for level in Tree_Nodes.keys():
            for i in Tree_Nodes.get(level):
                Node_Dict.setdefault(i.name, i)
        # pprint.pprint(Node_Dict)
        print(len(Node_Dict.keys()))

        Nece_Maps = {}

        for value in value_set:
            name_index = int2binstr(value).rjust(self.height, "0")
            # for pnode in Node_Dict.get(name_index).p_node:
                #

            pprint.pprint(Node_Dict.get(name_index))
        # pprint.pprint(value_set)

        # for i in range(self.height + 1):
            # print(Tree_Nodes.get(i))
        """
        for i in range(self.height, -1, -1):
            print(i)
            if i == self.height:
                # leaf nodes
                leaf_nodes = [int2binstr(x).rjust(self.height, "0")
                              for x in value_set]
                Tree_Nodes.setdefault(i, leaf_nodes)
            else:
                pass
        """

        """
        for i in range(self.height, -1, -1):
            level_nodes = []
            if i == 0:
                # level_nodes.append("root")
                node = Node("root", ["0", "1"], [], [0, 2 ** self.height - 1])
                level_nodes.append(node)
            else:
                for j in range(2 ** i):
                    node_bin = int2binstr(j).rjust(i, "0")
                    level_nodes.append(node_bin)
            Tree_Nodes.append(level_nodes)
        # print(len(Tree_Nodes))
        print(Tree_Nodes[-3:])
        """
        return value_set


if __name__ == '__main__':
    Raw_Data = ParseRawData("../data/sf0.01", "nation")
    (t_name, t_data, t_type) = Raw_Data
    max_value = max(list(t_data["_id"]))
    print(max_value)
    # max_value = max(list(t_data["O_CUSTKEY"]))
    tdag = TDAG(max_value)
    tdag.construct(list(t_data["_id"]))
