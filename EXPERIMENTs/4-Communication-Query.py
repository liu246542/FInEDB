#!/usr/bin/python3
import random
from collections import namedtuple
from utils.tools import ParseRawData

# Create several SQL queries.

SQL_Query = namedtuple("SQL_Query", ["Select", "Where", "Value"])


def gen_query(select_num, where_num, raw_table):
    (t_name, t_data, t_type) = raw_table
    att_list = list(t_data.columns)
    assert len(att_list) >= select_num

    index_list = list(range(len(att_list)))
    random.shuffle(index_list)
    choose_index = index_list[0:select_num]
    print(choose_index)
    select_att = [att_list[x] for x in choose_index]

    random.shuffle(index_list)
    choose_index = index_list[0:where_num]
    where_att = [att_list[x] for x in choose_index]
    value_list = []

    for att in where_att:
        value_list.append(random.choice(list(t_data[att])))
    return SQL_Query(select_att, where_att, value_list)


if __name__ == '__main__':
    raw_table = ParseRawData("../data/sf0.001", "customer")
    query_tuple = gen_query(2, 3, raw_table)
    print(query_tuple)
