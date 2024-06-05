#!/usr/bin/python3

from collections import namedtuple


def int2binstr(int_value):
    assert isinstance(int_value, int)
    return bin(int_value)[2:]


def binstr2int(bin_str):
    assert isinstance(bin_str, str)
    return int(bin_str, 2)


Node = namedtuple("Node", ["name", "c_node", "p_node", "cv_range", "level"])


class TDAG(object):
    """
    docstring for TDAG
    """

    def __init__(self, max_value):
        self.height = len(int2binstr(max_value))

    def __CollectParents__(self, node, node_dict):
        if isinstance(node, int):
            node = node_dict.get(int2binstr(node).rjust(self.height, "0"))
        if node.p_node != []:
            res_nodes = set(node.p_node)
            for p in node.p_node:
                temp_nodes = self.__CollectParents__(node_dict.get(p),
                                                     node_dict)
                res_nodes = res_nodes.union(set(temp_nodes))
            return res_nodes
        else:
            return set()

    def construct(self, value_list, recursive=0):
        # return a list contains a set of nodes
        value_set = sorted(set(value_list))
        Tree_Nodes = {}
        print(f"Tree Height is {self.height}")
        for i in range(self.height, -1, -1):
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
                    child_nodes = ["0", "1"]
                    cover_range = [0, 2 ** self.height - 1]
                if i == 1:
                    parent_node = ["root"]
                node_def = Node(name, child_nodes, parent_node, cover_range, i)
                level_nodes.append(node_def)
            Tree_Nodes.setdefault(i, level_nodes)

        for i in range(1, self.height):
            node_list = Tree_Nodes.get(i)
            level_nodes = []
            for j in range(len(node_list) - 1):
                name = node_list[j].name + "_" + node_list[j + 1].name
                child_nodes = [node_list[j].c_node[1],
                               node_list[j + 1].c_node[0]]
                cover_range = [node_list[j].cv_range[1],
                               node_list[j + 1].cv_range[0]]
                node_def = Node(name, child_nodes, [], cover_range, i)
                level_nodes.append(node_def)

                node_list_next = Tree_Nodes.get(i + 1)
                node_list_next[2 * j + 1].p_node.append(name)
                node_list_next[2 * j + 2].p_node.append(name)
            Tree_Nodes[i].extend(level_nodes)

        Node_Dict = {}

        for level in Tree_Nodes.keys():
            for i in Tree_Nodes.get(level):
                Node_Dict.setdefault(i.name, i)

        Multi_Maps = {}

        for value in value_set:
            name_index = int2binstr(value).rjust(self.height, "0")
            leaf_node = Node_Dict.get(name_index)
            parent_node = list(self.__CollectParents__(leaf_node, Node_Dict))
            if recursive:
                Multi_Maps.setdefault(name_index, [value])
                for label in parent_node:
                    Multi_Maps.setdefault(label, Node_Dict.get(label).c_node)
            else:
                parent_node.append(name_index)
                for label in parent_node:
                    Multi_Maps.setdefault(label, [])
                    Multi_Maps.get(label).append(value)
        return (Multi_Maps, Node_Dict)


if __name__ == '__main__':
    from tools import ParseRawData
    # Raw_Data = ParseRawData("../data/sf0.01", "orders")
    Raw_Data = ParseRawData("../data/sf0.01", "nation")
    (t_name, t_data, t_type) = Raw_Data
    # max_value = max(list(t_data["O_CUSTKEY"]))
    max_value = max(list(t_data["_id"]))
    print(max_value)
    # max_value = max(list(t_data["O_CUSTKEY"]))
    tdag = TDAG(max_value)
    # print(len(list(t_data["O_CUSTKEY"])))
    # print(f"value length:{len(list(t_data["O_CUSTKEY"]))}")
    # tdag.construct(list(t_data["O_CUSTKEY"]), 1)
    tdag.construct(list(t_data["_id"]), 1)
