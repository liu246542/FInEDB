#!/usr/bin/python3

import random
import pickle
import pandas as pd
# from decimal import Decimal
from functools import partial
from multiprocessing import Pool
from schemes import spx, fdb
from collections import namedtuple
# from pprint import pprint
from utils.tools import ParseRawData

# Create several SQL queries.

SQL_Query = namedtuple("SQL_Query", ["Select", "Where", "Value"])


def atom_process_task(query_tuple, folder_name, tb_list):
    tk_size = []
    # tk_fdb = []
    # tk1_fdb = []
    # tk2_fdb = []
    # tk3_fdb = []

    ct_fdb = fdb.Client()
    ct_fdb.load_tables(folder_name, tb_list)
    ct_fdb.construct_index(test_flag=1)
    tk = ct_fdb.gen_token(query_tuple, tb_list[0])
    tk_size.append(len(pickle.dumps(tk, -1)))
    tk_size.append(len(pickle.dumps(tk[0], -1)))
    tk_size.append(len(pickle.dumps(tk[1], -1)))
    tk_size.append(len(pickle.dumps(tk[2], -1)))
    del ct_fdb

    # tk_spx = []
    # tk1_spx = []
    # tk2_spx = []

    ct_spx = spx.Client()
    ct_spx.load_tables(folder_name, tb_list)
    ct_spx.construct_index()
    tk = ct_spx.gen_token(query_tuple, tb_list[0])
    tk_size.append(len(pickle.dumps(tk, -1)))
    tk_size.append(len(pickle.dumps(tk[0], -1)))
    tk_size.append(len(pickle.dumps(tk[1], -1)))
    del ct_spx

    return tk_size


def test_communication_size(folder_name, tb_list, query_list):
    tk_fdb = []
    tk1_fdb = []
    tk2_fdb = []
    tk3_fdb = []

    tk_spx = []
    tk1_spx = []
    tk2_spx = []

    # print(folder_name)
    # raise RuntimeError("Break")

    with Pool() as p:
        size_list = p.map(partial(atom_process_task,
                                  folder_name=folder_name,
                                  tb_list=tb_list), query_list)

    for size_tuple in size_list:
        tk_fdb.append(size_tuple[0])
        tk1_fdb.append(size_tuple[1])
        tk2_fdb.append(size_tuple[2])
        tk3_fdb.append(size_tuple[3])

        tk_spx.append(size_tuple[4])
        tk1_spx.append(size_tuple[5])
        tk2_spx.append(size_tuple[6])

    return (tk_fdb, tk1_fdb, tk2_fdb, tk3_fdb, tk_spx, tk1_spx, tk2_spx)


def gen_query(select_num, where_num, folder_name, tb_name):
    raw_table = ParseRawData(folder_name, tb_name)
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
    test_folder = ["../data/sf0.001"]
    tb_list = ["customer", "lineitem", "nation", "orders",
               "part", "partsupp", "region", "supplier"]
    tb_list = ["lineitem"]

    query_list = []
    for i in range(16):
        query_tuple = gen_query(i + 1, 15, test_folder[0], tb_list[0])
        query_list.append(query_tuple)
    res = test_communication_size(test_folder[0], tb_list, query_list)
    # pprint(res)

    data_frame = pd.DataFrame({
        "No. of Select Attrs": [x + 1 for x in range(16)],
        "Token Size FInEDB": res[0],
        "TK_1 Size FInEDB": res[1],
        "TK_2 Size FInEDB": res[2],
        "TK_3 Size FInEDB": res[3],
        "Token Size SPX": res[4],
        "TK_1 SPX": res[5],
        "TK_2 SPX": res[6],
    })
    print(data_frame)
    data_frame.to_csv("./4-Communication-Query-SELECT.csv", index=False)

    query_list = []
    for i in range(16):
        query_tuple = gen_query(15, i + 1, test_folder[0], tb_list[0])
        query_list.append(query_tuple)
    res = test_communication_size(test_folder[0], tb_list, query_list)
    # pprint(res)

    data_frame = pd.DataFrame({
        "No. of Where Attrs": [x + 1 for x in range(16)],
        "Token Size FInEDB": res[0],
        "TK_1 Size FInEDB": res[1],
        "TK_2 Size FInEDB": res[2],
        "TK_3 Size FInEDB": res[3],
        "Token Size SPX": res[4],
        "TK_1 SPX": res[5],
        "TK_2 SPX": res[6],
    })
    print(data_frame)
    data_frame.to_csv("./4-Communication-Query-WHERE.csv", index=False)

    """
    raw_table = ParseRawData("../data/sf0.001", "customer")
    query_tuple = gen_query(2, 3, raw_table)
    print(query_tuple)
    """
