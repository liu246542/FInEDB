#!/usr/bin/python3

import pickle
import pandas as pd
import random
from decimal import Decimal
from functools import partial
from multiprocessing import Pool
from schemes import spx, fdb
from pprint import pprint
from utils.tools import ParseRawData
from collections import namedtuple

SQL_Query = namedtuple("SQL_Query", ["Select", "Where", "Value"])


def atom_process_task(folder_name, tb_list):
    emm_size = []

    ct_fdb = fdb.Client()
    ct_fdb.load_tables(folder_name, tb_list)
    emm = ct_fdb.construct_index(test_flag=1)
    emm_size.append(len(pickle.dumps(emm[0], -1)))
    emm_size.append(len(pickle.dumps(emm[1], -1)))
    del ct_fdb, emm

    ct_spx = spx.Client()
    ct_spx.load_tables(folder_name, tb_list)
    emm = ct_spx.construct_index()
    emm_size.append(len(pickle.dumps(emm, -1)))
    for e in emm:
        emm_size.append(len(pickle.dumps(e, -1)))
    del ct_spx, emm

    return emm_size


def bytes2MB(x):
    return Decimal(x / 1048576).quantize(Decimal("0.00"))


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


def test_storage_size(folder_list, tb_list):
    disk_size_fdb = []
    filter_size_fdb = []
    disk_size_spx = []

    EMM_R_size = []
    EMM_C_size = []
    EMM_V_size = []
    EDX_size = []

    with Pool() as p:
        size_list = p.map(partial(atom_process_task,
                                  tb_list=tb_list), folder_list)

    for size_tuple in size_list:
        disk_size_fdb.append(size_tuple[0])
        filter_size_fdb.append(size_tuple[1])
        disk_size_spx.append(size_tuple[2])
        EMM_R_size.append(size_tuple[3])
        EMM_C_size.append(size_tuple[4])
        EMM_V_size.append(size_tuple[5])
        EDX_size.append(size_tuple[6])

    return (disk_size_fdb, filter_size_fdb, disk_size_spx,
            EMM_R_size, EMM_C_size, EMM_V_size, EDX_size)


if __name__ == '__main__':
    # "../data/sf0.001", "../data/sf0.002", "../data/sf0.003",
    # test_folder = ["../data/sf0.005"]
    test_folder = ["../data/sf0.001"]
    # "../data/sf0.002", "../data/sf0.003",
                   # "../data/sf0.004", "../data/sf0.005", "../data/sf0.006",
                   # "../data/sf0.007", "../data/sf0.008", "../data/sf0.009"]
                   # "../data/sf0.01"]
    # tb_list = ["lineitem"]
    # rg_tb_list = ["lineitem_rg"]
    tb_list = ["customer", "lineitem", "nation", "orders",
               "part", "partsupp", "region", "supplier"]

    """
    ct_fdb = fdb.Client()
    ct_fdb.load_tables(test_folder[0], tb_list)
    emm = ct_fdb.construct_index(test_flag=1)

    # pprint(ct_fdb.bff_dict)

    query_tuple = gen_query(2, 3, test_folder[0], tb_list[0])
    print(query_tuple.Select)

    tk = ct_fdb.gen_token(query_tuple, tb_list[0])
    pprint(tk)
    print(len(pickle.dumps(tk, -1)))
    """

    ct_spx = spx.Client()
    ct_spx.load_tables(test_folder[0], tb_list)
    query_tuple = gen_query(2, 3, test_folder[0], tb_list[0])
    print(query_tuple.Select)

    tk = ct_spx.gen_query(query_tuple, tb_list[0])
    pprint(tk)
    print(len(pickle.dumps(tk, -1)))

    """
    test_result = test_storage_size(test_folder, tb_list)

    data_frame = pd.DataFrame({
        "Scale": [x.split("/")[2] for x in test_folder],
        "Original Size": [Decimal(x / 1048576).quantize(Decimal("0.00"))
                          for x in test_result[0]],
        "Modified Size": [Decimal(x / 1048576).quantize(Decimal("0.00"))
                          for x in test_result[1]],
        "Ratio": test_result[2]
    })
    print(data_frame)
    """
